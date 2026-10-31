import datetime

def calculate_regret_score(amount: float, category: str, purchase_time_str: str, historical_rate: float):
    """
    Takes transaction data and returns a regret score with explainability.
    """
    base_prob = 0.15
    contributions = []
    score = base_prob

    # 1. Temporal Feature (Night purchase)
    # Assuming time is passed as "23:42" (11:42 PM)
    hour = int(purchase_time_str.split(":")[0])
    if hour >= 23 or hour <= 4:
        score += 0.25
        contributions.append({"feature": "Late Night Purchase", "impact": "+0.25", "reason": f"Purchase occurred at {purchase_time_str}"})

    # 2. Category Feature (Fashion)
    if category.lower() in ["fashion", "apparel", "clothing"]:
        score += 0.20
        contributions.append({"feature": "Fashion Category", "impact": "+0.20", "reason": "Apparel has high return rates"})

    # 3. Behavioral Feature (Personal History)
    if historical_rate > 0.50:
        impact = round(historical_rate * 0.30, 2)
        score += impact
        contributions.append({"feature": "Personal History", "impact": f"+{impact}", "reason": f"{int(historical_rate*100)}% historical regret rate for this pattern"})

    # Cap the score at 0.99 so it doesn't exceed 100%
    final_score = min(round(score, 2), 0.99)
    
    risk_level = "HIGH" if final_score >= 0.70 else "MEDIUM" if final_score >= 0.40 else "LOW"

    return {
        "regret_probability": final_score,
        "risk_level": risk_level,
        "explainability": {
            "base_probability": base_prob,
            "contributions": contributions
        }
    }

# --- Local Test Block ---
if __name__ == "__main__":
    # Maya's simulated transaction data
    print("Running test for Maya's purchase...")
    result = calculate_regret_score(
        amount=150.00,
        category="Fashion",
        purchase_time_str="23:42",
        historical_rate=0.72
    )
    
    import json
    print(json.dumps(result, indent=2))