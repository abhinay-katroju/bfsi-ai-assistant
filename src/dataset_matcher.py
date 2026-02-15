"""Similarity matching and dataset-based response retrieval (Tier 1)"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class DatasetMatcher:
    """
    Handles Tier 1: Dataset similarity matching
    Finds and returns responses from the dataset if similarity is high
    """
    
    def __init__(self, dataset_path: Path, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2", threshold: float = 0.75):
        """
        Initialize dataset matcher with embeddings
        
        Args:
            dataset_path: Path to BFSI dataset JSON
            embedding_model_name: Sentence transformer model for embeddings
            threshold: Similarity threshold for returning dataset response
        """
        self.dataset_path = dataset_path
        self.threshold = threshold
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.dataset = self._load_dataset()
        self.dataset_embeddings = self._generate_embeddings()
        
        logger.info(f"Dataset loaded: {len(self.dataset)} samples")
        logger.info(f"Similarity threshold: {self.threshold}")
    
    def _load_dataset(self) -> List[Dict]:
        """Load BFSI dataset from JSON file"""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Validate dataset structure
        for idx, item in enumerate(dataset):
            if not all(key in item for key in ['instruction', 'input', 'output']):
                logger.warning(f"Dataset item {idx} missing required fields")
        
        return dataset
    
    def _generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all dataset instructions"""
        instructions = [item['instruction'] for item in self.dataset]
        embeddings = self.embedding_model.encode(instructions, show_progress_bar=True)
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def find_match(self, query: str, top_k: int = 3) -> Tuple[Optional[Dict], float]:
        """
        Find most similar dataset entry for given query
        
        Args:
            query: User query
            top_k: Number of top matches to return
            
        Returns:
            Tuple of (best_match_dict, similarity_score)
            Returns (None, 0.0) if no match above threshold
        """
        # Encode query
        query_embedding = self.embedding_model.encode(query).reshape(1, -1)
        
        # Compute similarities
        similarities = cosine_similarity(query_embedding, self.dataset_embeddings)[0]
        
        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_scores = similarities[top_indices]
        
        # Log matching details
        logger.debug(f"Query: {query}")
        for idx, (data_idx, score) in enumerate(zip(top_indices, top_scores)):
            logger.debug(f"  Match {idx+1}: {self.dataset[data_idx]['instruction'][:50]}... (score: {score:.4f})")
        
        # Return best match if above threshold
        best_idx = top_indices[0]
        best_score = top_scores[0]
        
        if best_score >= self.threshold:
            match = self.dataset[best_idx].copy()
            match['similarity_score'] = float(best_score)
            match['matched_instruction'] = self.dataset[best_idx]['instruction']
            logger.info(f"Strong match found (score: {best_score:.4f})")
            return match, best_score
        else:
            logger.info(f"No strong match found (best score: {best_score:.4f}, threshold: {self.threshold})")
            return None, best_score
    
    def get_top_matches(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Get top K matches for a query
        
        Args:
            query: User query
            top_k: Number of matches to return
            
        Returns:
            List of (match_dict, similarity_score) tuples
        """
        query_embedding = self.embedding_model.encode(query).reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.dataset_embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            match = self.dataset[idx].copy()
            match['similarity_score'] = float(similarities[idx])
            results.append((match, similarities[idx]))
        
        return results
    
    def get_dataset_stats(self) -> Dict:
        """Get statistics about the dataset"""
        return {
            "total_samples": len(self.dataset),
            "categories": self._get_categories(),
            "avg_instruction_length": np.mean([len(item['instruction']) for item in self.dataset]),
            "avg_output_length": np.mean([len(item['output']) for item in self.dataset]),
            "embedding_dimensions": self.dataset_embeddings.shape[1] if len(self.dataset_embeddings) > 0 else 0,
        }
    
    def _get_categories(self) -> Dict[str, int]:
        """Categorize dataset by instruction type"""
        categories = {}
        keywords = {
            "loan_eligibility": ["eligibility", "criteria", "qualify"],
            "application": ["application", "apply", "document"],
            "emi": ["emi", "payment", "installment"],
            "interest": ["interest", "rate", "p.a"],
            "account": ["account", "profile", "update"],
            "prepayment": ["prepay", "close", "early"],
            "transaction": ["transaction", "payment", "history"],
            "support": ["support", "help", "reset", "contact"]
        }
        
        for item in self.dataset:
            instruction = item['instruction'].lower()
            found_category = False
            for category, keywords_list in keywords.items():
                if any(kw in instruction for kw in keywords_list):
                    categories[category] = categories.get(category, 0) + 1
                    found_category = True
                    break
            if not found_category:
                categories['other'] = categories.get('other', 0) + 1
        
        return categories


class ResponseBuilder:
    """Build responses with source attribution"""
    
    @staticmethod
    def build_dataset_response(match: Dict) -> str:
        """Build response from dataset match"""
        return f"{match['output']}"
    
    @staticmethod
    def build_response_with_metadata(match: Dict, tier: str) -> Dict:
        """Build response with metadata for tracking"""
        return {
            "response": match['output'],
            "tier": tier,
            "confidence": match.get('similarity_score', 1.0),
            "source": "dataset_match",
            "matched_instruction": match.get('matched_instruction', match.get('instruction', 'N/A')),
        }


if __name__ == "__main__":
    # Test the matcher
    from src.config import DATA_DIR
    
    logging.basicConfig(level=logging.INFO)
    
    matcher = DatasetMatcher(DATA_DIR / "bfsi_dataset.json")
    
    # Test queries
    test_queries = [
        "What is the interest rate for a personal loan?",
        "How do I check my application status?",
        "What should I do if I miss an EMI payment?",
        "Can I prepay my loan early?",
    ]
    
    print("\n" + "="*80)
    print("DATASET MATCHER TEST")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        match, score = matcher.find_match(query)
        if match:
            print(f"✓ Match found (Score: {score:.4f})")
            print(f"  Instruction: {match['matched_instruction']}")
            print(f"  Response: {match['output'][:100]}...")
        else:
            print(f"✗ No match above threshold (Best score: {score:.4f})")
    
    print("\n" + "="*80)
    print("Dataset Statistics:")
    print(json.dumps(matcher.get_dataset_stats(), indent=2))
