"""Configuration settings for BFSI AI Assistant"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RAG_KNOWLEDGE_DIR = PROJECT_ROOT / "rag_knowledge"

# Dataset configuration
DATASET_FILE = DATA_DIR / "bfsi_dataset.json"
DATASET_SIZE = 150  # Minimum samples required

# Model configuration
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Lightweight SLM
FINE_TUNED_MODEL_PATH = MODELS_DIR / "fine_tuned_bfsi_model"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Response thresholds
SIMILARITY_THRESHOLD = 0.75  # For dataset matching
RELEVANCE_THRESHOLD = 0.6   # For RAG retrieval

# Safety and compliance
MAX_RESPONSE_LENGTH = 500
ALLOWED_QUERY_CATEGORIES = [
    "loan_eligibility",
    "application_status",
    "emi_details",
    "interest_rates",
    "payments",
    "transactions",
    "account_support",
    "customer_service"
]

# RAG configuration
RAG_CHUNK_SIZE = 512
RAG_OVERLAP = 50
USE_RAG_FOR_COMPLEX_QUERIES = True

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Logging
LOG_LEVEL = "INFO"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
