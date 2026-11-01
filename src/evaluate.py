import json
import os

with open("data/test_cases.json", "r", encoding="utf-8") as f:
    test_cases = json.load(f)

def demo_model(case):
    if case["type"] == "classification":
        text = case["input"].lower()
        if any(w in text for w in ["отлично", "спасибо", "вежлив", "быстро помогла"]):
            return "positive"
        elif any(w in text for w in ["поздно", "повреждена", "не то", "сломалось"]):
            return "negative"
        else:
            return "neutral"
    elif case["type"] == "extraction":
        return {"name": None, "email": None, "phone": None, "inn": None, "address": None}
    elif case["type"] == "summarization":
        return " ".join(case["input"].split()[:3])
    return None

def evaluate():
    results = []
    correct = 0
    total = 0

    for case in test_cases:
        prediction = demo_model(case)
        t = case["type"]

        if t == "classification":
            expected = case.get("expected")
            is_correct = prediction == expected
            correct += int(is_correct)
            total += 1
            results.append({"id": case["id"], "type": t, "expected": expected, "prediction": prediction, "correct": is_correct})

        elif t == "extraction":
            expected = case.get("expected", {})
            correct_fields = 0
            total_fields = 0
            if isinstance(expected, dict) and isinstance(prediction, dict):
                for key, exp_val in expected.items():
                    if exp_val is not None:
                        total_fields += 1
                        if prediction.get(key) == exp_val:
                            correct_fields += 1
            is_correct = (correct_fields == total_fields) if total_fields > 0 else False
            correct += int(is_correct)
            total += 1
            results.append({"id": case["id"], "type": t, "expected": expected, "prediction": prediction, "correct": is_correct})

        elif t == "summarization":
            expected_keywords = case.get("expected_keywords", [])
            found = sum(1 for kw in expected_keywords if kw.lower() in prediction.lower())
            is_correct = found >= len(expected_keywords) * 0.5 if expected_keywords else False
            correct += int(is_correct)
            total += 1
            results.append({"id": case["id"], "type": t, "expected_keywords": expected_keywords, "prediction": prediction, "keywords_found": found, "correct": is_correct})

    accuracy = correct / total if total > 0 else 0

    by_type = {}
    for r in results:
        t = r["type"]
        if t not in by_type:
            by_type[t] = {"correct": 0, "total": 0}
        by_type[t]["total"] += 1
        if r["correct"]:
            by_type[t]["correct"] += 1

    os.makedirs("results", exist_ok=True)
    report = {
        "total_cases": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "by_type": {
            t: {"accuracy": round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0, "correct": v["correct"], "total": v["total"]}
            for t, v in by_type.items()
        },
        "details": results
    }

    with open("results/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print("LLM EVALUATION REPORT")
    print("=" * 50)
    print(f"Total cases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")
    print()
    print("By type:")
    for t, v in by_type.items():
        acc = v["correct"] / v["total"] if v["total"] > 0 else 0
        print(f"  {t}: {v['correct']}/{v['total']} ({acc:.2%})")
    print()
    print("Details saved to: results/report.json")
    print("=" * 50)

if __name__ == "__main__":
    evaluate()
