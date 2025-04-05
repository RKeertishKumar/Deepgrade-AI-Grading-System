import random

def classify_prompt(prompt):
    categories = [
        "logical_reasoning",
        "summarization",
        "logical_verification",
        "information_extraction",
        "localization_recognition"
    ]
    
    values = [random.randint(0, 40) for _ in categories]
    total = sum(values)
    
    # Normalize to make sure the sum is around 100
    classification = {cat: round((val / total) * 100, 2) for cat, val in zip(categories, values)}
    
    # Sort categories by their values in descending order
    sorted_categories = sorted(classification.items(), key=lambda x: x[1], reverse=True)
    
    # Retain top 2 categories
    top_2 = sorted_categories[:2]
    top_2_sum = sum(val for _, val in top_2)
    others_value = 100 - top_2_sum
    
    # Adjust "others" to ensure the total is exactly 100
    final_classification = {cat: val for cat, val in top_2}
    final_classification["others"] = round(others_value, 2)
    
    # Ensure rounding does not cause the total to deviate from 100
    diff = 100 - sum(final_classification.values())
    if diff != 0:
        first_key = next(iter(final_classification))
        final_classification[first_key] += diff
    
    return final_classification
