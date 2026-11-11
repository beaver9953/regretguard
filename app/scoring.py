import datetime

def calculate_regret_score(amount: float, merchant_name: str, purchase_time_str: str, historical_rate: float):
    """
    Takes real transaction data and returns a regret score with explainability.
    """
    base_prob = 0.15
    contributions = []
    score = base_prob

    # 1. Temporal Feature (Night purchase)
    try:
        hour = int(purchase_time_str.split(":")[0])
    except:
        hour = 12 # Default to afternoon if parsing fails
        
    if hour >= 23 or hour <= 4:
        score += 0.25
        contributions.append({"feature": "Late Night Purchase", "impact": "+0.25", "reason": f"Purchase occurred at {purchase_time_str}"})
    else:
        # If it's daytime, it actually decreases the risk
        score -= 0.10
        contributions.append({"feature": "Daytime Purchase", "impact": "-0.10", "reason": f"Purchase occurred at {purchase_time_str}"})

    # 2. Category Feature (Fashion) - Dynamically check the merchant name
    is_fashion = any(word in merchant_name.lower() for word in ["zara", "fashion", "apparel", "clothing", "shoes", "boots"])
    if is_fashion:
        score += 0.20
        contributions.append({"feature": "Fashion Category", "impact": "+0.20", "reason": f"Merchant '{merchant_name}' has high return rates"})

    # 3. Behavioral Feature (Personal History)
    if historical_rate > 0.50:
        impact = round(historical_rate * 0.30, 2)
        score += impact
        contributions.append({"feature": "Personal History", "impact": f"+{impact}", "reason": f"{int(historical_rate*100)}% historical regret rate for this pattern"})

    # Cap the score between 0.01 and 0.99
    final_score = max(0.01, min(round(score, 2), 0.99))
    
    risk_level = "HIGH" if final_score >= 0.70 else "MEDIUM" if final_score >= 0.40 else "LOW"

    return {
        "regret_probability": final_score,
        "risk_level": risk_level,
        "explainability": {
            "base_probability": base_prob,
            "contributions": contributions
        }
    }