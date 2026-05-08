import os
import sys
import time
import json
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.engine import ProductCandidate, score_candidates

def evaluate_ai_quality():
    print("[*] Evaluating AI Recommendation Quality...")
    
    # Test Scenario: 1000 candidates (stressing the scoring loop)
    candidates = []
    for i in range(1000):
        candidates.append(ProductCandidate(
            product_id=f"P-{i}",
            product_name=f"Laptop {i}",
            seller_name=f"Seller {i}",
            seller_rating=4.0 + (i % 10) / 10.0,
            price=Decimal(1000 - i), # Lower i = higher price
            stock_qty=i % 100,
            delivery_days=2 + (i % 5),
            avg_review_stars=4.2
        ))

    start = time.time()
    ranked = score_candidates(candidates)
    latency = (time.time() - start) * 1000
    
    # Metrics
    quality_metrics = {
        "candidate_count": 1000,
        "scoring_latency_ms": round(latency, 2),
        "top_pick": {
            "name": ranked[0].product_name,
            "score": ranked[0].score,
            "explanation": ranked[0].explanation
        },
        "bottom_pick": {
            "name": ranked[-1].product_name,
            "score": ranked[-1].score
        },
        "score_distribution": {
            "above_80": len([c for c in ranked if c.score >= 0.8]),
            "below_40": len([c for c in ranked if c.score <= 0.4])
        }
    }

    log_path = "audit_logs/test_3/metrics/ai_quality_metrics.json"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(quality_metrics, f, indent=4)
    
    print(f"[+] AI Quality Evaluation complete. Latency: {latency:.2f}ms")

if __name__ == "__main__":
    evaluate_ai_quality()
