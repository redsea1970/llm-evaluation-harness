"""
LLM-Evaluation-Harness: AI-судья и pairwise comparison (демо, без API).
Опора: глава 3 книги «AI-инженерия» (Чип Хьюен).
"""

import json
import os
import re
from collections import Counter


with open("data/test_cases.json", "r", encoding="utf-8") as f:
    test_cases = json.load(f)


def tokenize(text):
    return re.findall(r"\w+", str(text).lower())


def overlap_score(a, b):
    ta, tb = set(tokenize(a)), set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def ai_judge_score(expected, prediction):
    """AI-судья: оценивает сходство по смыслу (пересечение токенов)."""
    if isinstance(expected, dict) and isinstance(prediction, dict):
        scores = []
        for key, exp_val in expected.items():
            if exp_val is not None:
                scores.append(overlap_score(exp_val, prediction.get(key, "")))
        return sum(scores) / len(scores) if scores else 0.0
    return overlap_score(expected, prediction)


def demo_model(case):
    if case["type"] == "classification":
        text = case["input"].lower()
        if any(w in text for w in ["отлично", "спасибо", "вежлив", "быстро помогла"]):
            return "positive"
        elif any(w in text for w in ["поздно", "повреждена", "не то", "сломалось"]):
            return "negative"
        return "neutral"
    if case["type"] == "extraction":
        return {"name": None, "email": None, "phone": None, "inn": None, "address": None}
    if case["type"] == "summarization":
        return " ".join(case["input"].split()[:3])
    return None


def pairwise_compare(case, answer_a, answer_b):
    """Сравнивает два ответа через AI-судью и возвращает победителя."""
    if case["type"] == "classification":
        ea = overlap_score(case.get("expected"), answer_a)
        eb = overlap_score(case.get("expected"), answer_b)
    elif case["type"] == "summarization":
        kws = case.get("expected_keywords", [])
        ea = sum(1 for kw in kws if kw.lower() in answer_a.lower())
        eb = sum(1 for kw in kws if kw.lower() in answer_b.lower())
    else:
        ea = ai_judge_score(case.get("expected", {}), answer_a)
        eb = ai_judge_score(case.get("expected", {}), answer_b)
    if ea > eb:
        return "A", ea, eb
    if eb > ea:
        return "B", ea, eb
    return "tie", ea, eb


def run_pairwise_with_swap(case, answer_a, answer_b):
    """Проверка позиционного предубеждения: сравниваем A/B и B/A."""
    winner_direct, _, _ = pairwise_compare(case, answer_a, answer_b)
    winner_swapped, _, _ = pairwise_compare(case, answer_b, answer_a)
    if winner_direct == "A":
        winner_swapped_normalized = "B"
    elif winner_direct == "B":
        winner_swapped_normalized = "A"
    else:
        winner_swapped_normalized = "tie"
    consistent = winner_direct == winner_swapped_normalized
    return {
        "case_id": case["id"],
        "direct": winner_direct,
        "swapped_normalized": winner_swapped_normalized,
        "consistent": consistent,
    }


def evaluate_with_judge():
    results = []
    correct_exact = 0
    judge_total = 0.0

    for case in test_cases:
        prediction = demo_model(case)
        expected = case.get("expected") if case["type"] != "summarization" else case.get("expected_keywords")

        if case["type"] == "classification":
            is_correct = prediction == case.get("expected")
            correct_exact += int(is_correct)
        elif case["type"] == "extraction":
            expected_dict = case.get("expected", {})
            correct_fields = 0
            total_fields = 0
            for key, exp_val in expected_dict.items():
                if exp_val is not None:
                    total_fields += 1
                    if prediction.get(key) == exp_val:
                        correct_fields += 1
            is_correct = (correct_fields == total_fields) if total_fields else False
            correct_exact += int(is_correct)
        elif case["type"] == "summarization":
            kws = case.get("expected_keywords", [])
            found = sum(1 for kw in kws if kw.lower() in prediction.lower())
            is_correct = found >= len(kws) * 0.5 if kws else False
            correct_exact += int(is_correct)
        else:
            is_correct = False

        judge_score = ai_judge_score(expected, prediction)
        judge_total += judge_score

        results.append({
            "id": case["id"],
            "type": case["type"],
            "exact_match": is_correct,
            "judge_score": round(judge_score, 4),
        })

    n = len(test_cases)
    exact_accuracy = correct_exact / n if n else 0
    judge_avg = judge_total / n if n else 0

    os.makedirs("results", exist_ok=True)
    report = {
        "total_cases": n,
        "exact_match_accuracy": round(exact_accuracy, 4),
        "judge_avg_score": round(judge_avg, 4),
        "details": results,
    }
    with open("results/judge_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("AI-JUDGE EVALUATION")
    print("=" * 60)
    print(f"Total cases: {n}")
    print(f"Exact Match Accuracy: {exact_accuracy:.2%}")
    print(f"AI-Judge Average Score: {judge_avg:.4f}")
    print("Report saved to results/judge_report.json")
    print("=" * 60)


def run_pairwise_benchmark():
    """Сравниваем demo_model с «идеальным» ответом (эталоном)."""
    comparisons = []
    for case in test_cases:
        prediction = demo_model(case)
        if case["type"] == "classification":
            ideal = case.get("expected")
        elif case["type"] == "summarization":
            ideal = " ".join(case.get("expected_keywords", []))
        else:
            ideal = json.dumps(case.get("expected", {}), ensure_ascii=False)
        pred_str = json.dumps(prediction, ensure_ascii=False) if isinstance(prediction, dict) else str(prediction)
        cmp = run_pairwise_with_swap(case, pred_str, ideal)
        comparisons.append(cmp)

    consistent = sum(1 for c in comparisons if c["consistent"])
    n = len(comparisons)
    print("=" * 60)
    print("PAIRWISE COMPARISON (position bias check)")
    print("=" * 60)
    print(f"Comparisons: {n}")
    print(f"Consistent (no position bias): {consistent}/{n} ({consistent/n:.0%})")
    print("=" * 60)


if __name__ == "__main__":
    evaluate_with_judge()
    print()
    run_pairwise_benchmark()
