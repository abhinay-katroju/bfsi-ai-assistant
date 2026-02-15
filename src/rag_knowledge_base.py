"""RAG Knowledge Base for complex financial queries"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class RAGKnowledgeBase:
    """
    Retrieval-Augmented Generation for complex financial queries
    Stores structured financial knowledge and policies
    """
    
    def __init__(self, rag_dir: Path, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.rag_dir = rag_dir
        self.rag_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.knowledge_base = self._initialize_knowledge_base()
        self.knowledge_embeddings = self._generate_embeddings()
        
        logger.info(f"RAG Knowledge Base initialized with {len(self.knowledge_base)} documents")
    
    def _initialize_knowledge_base(self) -> List[Dict]:
        """Initialize with structured BFSI knowledge"""
        knowledge = [
            {
                "id": "policy_emi_calculation",
                "category": "EMI Calculation",
                "title": "EMI Calculation Formula and Example",
                "content": """
EMI (Equated Monthly Installment) Formula:
EMI = [P × R × (1 + R)^N] / [(1 + R)^N - 1]

Where:
- P = Principal loan amount (in rupees)
- R = Monthly interest rate (annual rate ÷ 12 ÷ 100)
- N = Total number of months (loan tenure in years × 12)

Example Calculation:
Principal (P) = INR 5,00,000
Annual Rate = 10% p.a.
Tenure = 5 years (60 months)

Step 1: Calculate monthly rate
R = 10 ÷ 12 ÷ 100 = 0.008333

Step 2: Apply formula
EMI = [5,00,000 × 0.008333 × (1.008333)^60] / [(1.008333)^60 - 1]
EMI = [4166.67 × 1.6453] / [0.6453]
EMI = INR 10,610 per month

Total Payment = 10,610 × 60 = INR 6,36,600
Total Interest = 6,36,600 - 5,00,000 = INR 1,36,600

Important Notes:
- EMI remains constant throughout the loan period
- First EMI installment due after 30 days from disbursement
- EMI includes both principal and interest
- Prepayment reduces both total interest and remaining tenure
"""
            },
            {
                "id": "policy_interest_breakup",
                "category": "Interest Calculations",
                "title": "Interest Breakdown in EMI",
                "content": """
Understanding Interest Component in Each EMI:

Early EMIs (First 6 months):
- Higher interest component
- Lower principal component
- Example: In first EMI of INR 10,000, interest might be INR 4,167, principal only INR 5,833

Middle EMIs (6-36 months):
- Gradual decrease in interest component
- Gradual increase in principal component
- More principal is paid off

Final EMIs (Last 12 months):
- Lower interest component
- Higher principal component
- Majority goes toward principal repayment

Example Breakdown - INR 5L at 10% for 5 years:
Month 1: Interest = 4,166.67 | Principal = 6,443.33 | Balance = 4,93,556.67
Month 12: Interest = 3,953.68 | Principal = 6,656.32 | Balance = 4,20,598.68
Month 30: Interest = 2,827.45 | Principal = 7,782.55 | Balance = 2,17,842.19
Month 59: Interest = 87.58 | Principal = 10,522.42 | Balance = 10,087.58
Month 60: Interest = 84.06 | Principal = 10,525.94 | Balance = 0

Key Insight:
Early prepayment saves maximum interest. Paying extra in early months is highly beneficial.
"""
            },
            {
                "id": "policy_interest_rates",
                "category": "Interest Rates",
                "title": "Current Interest Rate Slabs",
                "content": """
Interest Rate Structure as of Feb 2026:

Personal Loan Rates:
EXCELLENT Credit (750+): 8.5% - 9.0% p.a.
GOOD Credit (700-749): 9.5% - 10.5% p.a.
FAIR Credit (650-699): 11.0% - 12.5% p.a.
AVERAGE Credit (<650): 13.0% - 15.0% p.a. (or not eligible)

Special Discounts:
- Salary Account Holder: 0.5% discount
- Existing Customer: 0.75% discount
- Investment Product Customer: 0.25% discount
- Online Application: 0.25% discount
- Referral Program: 0.25% discount

Home Loan Rates (Varies):
LTV 60% or less: 6.5% - 7.5% p.a.
LTV 60-80%: 7.0% - 8.0% p.a.
LTV above 80%: 8.0% - 9.0% p.a.

Auto Loan Rates:
New Vehicle: 7.0% - 9.0% p.a.
Used Vehicle (0-5 years): 8.0% - 10.0% p.a.
Used Vehicle (5+ years): 10.0% - 12.0% p.a.

Important Disclaimers:
- Rates subject to credit profile assessment
- Final rate decided at approval stage
- Floating rates may change with RBI policy
- Fixed rates locked for entire tenure
"""
            },
            {
                "id": "policy_penalties",
                "category": "Penalties and Charges",
                "title": "Late Payment Penalties",
                "content": """
Late Payment Fee Structure:

1-5 Days Late:
- Penalty: 1.5% of EMI amount
- Example: INR 150 on INR 10,000 EMI
- Credit Score Impact: None yet
- Status: OVERDUE (not Default)

6-30 Days Late:
- Additional Penalty: 2% of EMI amount
- Cumulative from Day 1: 1.5% + 2% = 3.5%
- Example: INR 350 total on INR 10,000 EMI
- Credit Score Impact: Begins (100-150 point drop)
- Status: OVERDUE - High Risk

31-60 Days Late:
- Penalty: 2% per month (compounded)
- Marked as "Suit Filed" on credit report
- Credit Score Impact: 150-200 point drop
- Status: DEFAULT

61+ Days Late:
- Legal recovery proceedings initiated
- Default status reported to CIBIL
- Severe credit score damage (200+ points)
- Collections agency involvement possible
- Account closure possible

Important:
- Penalties are separate from interest
- Each day of delay adds cost
- Auto-pay prevents all penalties
- Contact support within 5 days for relief options
- After 90 days: Loan may be marked as NPA (Non-Performing Asset)
"""
            },
            {
                "id": "policy_prepayment",
                "category": "Prepayment Policy",
                "title": "Loan Prepayment and Early Closure",
                "content": """
Prepayment Policy Overview:

Prepayment Within 6 Months:
- Prepayment Charge: 2% of prepaid amount
- Example: Prepay INR 1,00,000 early = INR 2,000 charge
- Remaining interest: Prorated (calculated daily)
- EMI refund: Not applicable (already paid)

Prepayment After 6 Months:
- Prepayment Charge: ZERO (Waived)
- No penalties or charges
- All prepayment amount goes to principal
- Interest saving is maximum

Calculation Example (INR 5L at 10% for 5 years):
Original EMI: INR 10,610/month
Total interest: INR 1,36,600

If prepay entire amount after 1 year (12 EMIs paid):
- Outstanding balance: INR 4,53,000 (approx)
- Remaining interest if continued: INR 1,00,000 (approx)
- Interest saved: INR 1,00,000
- Since within 6 months of orig: 2% charge = INR 9,060
- NET SAVING: INR 90,940

If prepay after 2 years:
- Outstanding balance: INR 3,95,000 (approx)
- No prepayment charge (past 6 months)
- Interest saved: INR 70,000
- NET SAVING: INR 70,000

Partial Prepayment:
- Minimum Amount: INR 1,000
- Can be done anytime
- EMI continues till closure
- Tenure can shorten automatically (if requested)
- Interest impact: Reduced each month

Methods to Prepay:
1. Online Portal: Dashboard → My Loan → Prepayment
2. Mobile App: Loan Details → Additional Payment
3. Bank Transfer: With clear reference
4. Branch Visit: Direct payment option
5. Check Payment: Endorsed to account
"""
            },
            {
                "id": "policy_credit_score_impact",
                "category": "Credit Score Impact",
                "title": "How Loans Affect Credit Score",
                "content": """
Credit Score Impact Breakdown (CIBIL Score 300-900):

Positive Impacts (+):
- On-time payments: +5-10 points per month
- Long repayment history: +20-50 points
- Timely full repayment: +100+ points
- Low credit utilization: +10-20 points
- Mix of credit types: +50 points

Negative Impacts (-):
- Late payment 1-30 days: -50 to -100 points
- Late payment 31-60 days: -100 to -150 points
- Default (61+ days): -150 to -200 points
- Multiple late payments: -200 to -300 points
- Loan closure with default: -300+ points
- Multiple hard inquiries: -5 to -10 per inquiry

Recovery Timeline:
After on-time payment resumption:
- 1 month: Marked as paid, impact reduces
- 3-6 months: Gradual score recovery begins
- 12+ months: Significant recovery if perfect payments
- 24+ months: Default may drop off (varies by bureau)
- 36+ months: Almost completely recovered

Score Restoration Strategy:
1. Never miss payments (most important)
2. Pay more than minimum (if possible)
3. Keep credit utilization low
4. Don't apply for multiple loans (hard inquiries)
5. Keep old accounts active
6. Mix of credit types helps
7. Check report for errors
8. Dispute inaccuracies immediately

Timeline to Good Score:
From Default → Good Score: 18-24 months
From Fair → Excellent Score: 12-18 months
From New → Established: 24-36 months

Action: Perfect payments = Score recovery 20-30 points/month
"""
            },
            {
                "id": "policy_compliance_regulations",
                "category": "Regulatory Compliance",
                "title": "Regulatory Framework and Compliance",
                "content": """
Key Compliance Requirements:

RBI Guidelines:
- Fair Lending Practices: No discrimination in approval
- Interest Rate Caps: Max variations defined
- Transparency: All terms clearly disclosed
- Consumer Protection: Grievance redressal mandatory
- Data Security: Encryption and privacy guaranteed
- Anti-Predatory: No unfair terms or conditions

Consumer Protection Act, 2019:
- Right to Fair Pricing
- Right to Clear Information
- Right to Privacy
- Right to Grievance Redressal
- Protection from Harassment

Fair Lending Practices:
✓ Equal treatment regardless of caste, religion, gender
✓ No exploitation of vulnerable sections
✓ Transparent and reasonable lending criteria
✓ No coercive collection practices
✓ Respectful customer treatment always

Collection Practices (Allowed):
- SMS reminders: Yes
- Email notifications: Yes
- Call during 7 AM - 7 PM: Yes
- Calls every 2-3 days: Yes
- Clear explanation of dues: Yes

Collection Practices (Prohibited):
✗ Abusive language or threats
✗ Calls before 7 AM or after 7 PM
✗ Calls to workplace (except first contact)
✗ Calls to family members
✗ Public disclosure of debt
✗ Misrepresentation of authority

Our Compliance:
- 100% RBI compliant
- Annual compliance audits
- Transparent operations
- Customer-first approach
- Anti-fraud measures
- Data security (ISO 27001)

Complaint Escalation:
Level 1: Customer Support (24 hours)
Level 2: Grievance Officer (7 days)
Level 3: Ombudsman (if unresolved)
Level 4: RBI/Courts (if necessary)

Your Rights:
- Right to know all charges upfront
- Right to cancel within 30 days (no penalty)
- Right to prepay anytime (penalty per policy)
- Right to change due date (twice yearly)
- Right to financial privacy
- Right to error correction
"""
            },
            {
                "id": "policy_eligibility_factors",
                "category": "Eligibility Criteria",
                "title": "Loan Eligibility Factors and Assessment",
                "content": """
Eligibility Assessment Criteria:

Age Requirements:
- Minimum: 21 years
- Maximum: 60 years (at loan end)
- Working age: Preferred

Income Requirements:
Personal Loan:
- Minimum: INR 2.5 lakh per annum
- Preferred: INR 5+ lakh per annum
- Self-employed: Additional documentation

Employment Status:
✓ Salaried: Require 2+ years in current job
✓ Self-employed: Require 3+ years business
✓ Business: ITR filing required
✓ Freelancer: 2+ years documented income
✗ Unemployed/Recently retired: Not eligible

Credit History:
- Credit Score 650+: Eligible
- 700+: Better rates
- 750+: Best rates
- No score: Alternative assessment

Debt Analysis:
- Debt-to-Income Ratio: Max 50%
- Example: INR 1L monthly income = max INR 50K EMI
- All loans considered (credit cards, etc.)
- Self-employed: Conservative calculation

Stability Factors:
✓ Stable employment/business
✓ No recent loan defaults
✓ Good repayment history
✓ Consistent income
✗ Frequent job changes (risk factor)
✗ Recent defaults
✗ High number of credit applications

Documentation Requirements:
Identity Proof: Aadhaar, Passport, Voter ID, Driving License
Address Proof: Utility bill, Rental agreement, Property tax
Income Proof: Salary slips (3 months), ITR (1 year), Form 16
Bank Statement: Last 6 months (showing regular income)
Self-Employed: ITR + Turnover statement

Additional Factors:
- Presence in BFSI sector: Positive
- Relationship with us: Positive (existing customer)
- Co-applicant income: Can boost eligibility
- Guarantor provided: Can improve approval odds

Special Programs:
- Salary Account: Faster approval, better rates
- Referral Program: Both get benefits
- Employee Program: Special rates available
- Senior Citizen: Adjusted criteria available

Pre-Approval:
- Online pre-approval available
- No credit check required
- Validity: 30 days
- Instant: 2 minutes to pre-approve
"""
            },
            {
                "id": "policy_tenure_options",
                "category": "Loan Tenure",
                "title": "Loan Duration Options and Selection",
                "content": """
Available Loan Tenure Options:

Personal Loans:
- 12 months (1 year)
- 24 months (2 years)
- 36 months (3 years) ← MOST POPULAR
- 48 months (4 years)
- 60 months (5 years)
- 72 months (6 years) - For large amounts

Home Loans:
- 5-30 years
- Most common: 15-20 years

Auto Loans:
- 24-60 months
- Used car: 36-48 months max

Tenure Impact on EMI:

Same Principal (INR 5L) at 10% p.a.:
- 1 year: EMI = INR 42,915 | Total Interest = 15,380
- 2 year: EMI = 21,875 | Total Interest = 25,000
- 3 year: EMI = 15,838 | Total Interest = 70,164
- 4 year: EMI = 12,662 | Total Interest = 8,176
- 5 year: EMI = 10,610 | Total Interest = 1,36,600

Key Insight:
- Longer tenure = Lower EMI (easier affordability)
- Longer tenure = Higher total interest (expensive)
- Shorter tenure = Higher EMI (tight budget)
- Shorter tenure = Lower total interest (savings)

Choosing Right Tenure:
Consider:
1. Monthly Cash Flow: Can you afford EMI?
2. Interest Savings: Short tenure saves interest
3. Loan Purpose: Match tenure to asset life
4. Income Stability: Longer if uncertain income
5. Future Plans: Prepayment easier if longer tenure

Tenure Change Options:
- Extend Tenure: Reduce EMI (after 2 years, special request)
- Reduce Tenure: Increase EMI (anytime via prepayment)
- Flexible Tenure: Some products allow change

Recommendation Strategy:
- Minimum Comfortable EMI: 30-40% of monthly income
- Optimal Tenure: 3-5 years for personal loans
- Prepayment Friendly: Choose longer tenure, prepay in short period
- Maximum Flexibility: 5-year tenure allows all options
"""
            }
        ]
        
        # Save knowledge base
        kb_path = self.rag_dir / "knowledge_base.json"
        with open(kb_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        return knowledge
    
    def _generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all knowledge documents"""
        contents = [item['content'] for item in self.knowledge_base]
        embeddings = self.embedding_model.encode(contents, show_progress_bar=False)
        logger.info(f"Generated {len(embeddings)} knowledge embeddings")
        return embeddings
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 3, threshold: float = 0.6) -> List[Dict]:
        """
        Retrieve relevant knowledge documents for a query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            threshold: Relevance threshold
            
        Returns:
            List of relevant knowledge documents with scores
        """
        query_embedding = self.embedding_model.encode(query).reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.knowledge_embeddings)[0]
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= threshold:
                doc = self.knowledge_base[idx].copy()
                doc['relevance_score'] = float(score)
                results.append(doc)
                logger.debug(f"Retrieved: {doc['title']} (score: {score:.4f})")
        
        return results
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Search knowledge base by category"""
        return [doc for doc in self.knowledge_base if doc['category'].lower() == category.lower()]
    
    def get_kb_stats(self) -> Dict:
        """Get knowledge base statistics"""
        categories = {}
        for doc in self.knowledge_base:
            cat = doc['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_documents": len(self.knowledge_base),
            "categories": categories,
            "embedding_dimensions": self.knowledge_embeddings.shape[1] if len(self.knowledge_embeddings) > 0 else 0,
        }


if __name__ == "__main__":
    from src.config import RAG_KNOWLEDGE_DIR
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize knowledge base
    kb = RAGKnowledgeBase(RAG_KNOWLEDGE_DIR)
    
    print("\n" + "="*80)
    print("RAG KNOWLEDGE BASE INITIALIZED")
    print("="*80)
    print(json.dumps(kb.get_kb_stats(), indent=2))
    
    # Test retrieval
    test_queries = [
        "How is EMI calculated for my loan?",
        "What are the penalties for late payment?",
        "How does interest rate work?",
    ]
    
    print("\n" + "="*80)
    print("KNOWLEDGE RETRIEVAL TEST")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        docs = kb.retrieve_relevant_docs(query)
        for doc in docs:
            print(f"  ✓ {doc['title']} (relevance: {doc['relevance_score']:.4f})")
