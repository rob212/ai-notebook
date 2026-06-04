from collections import Counter

import pandas as pd


def generate_accuracy_table(data: dict[str, list]) -> pd.DataFrame:
    table = []

    for model, tasks in data.items():
        total = len(tasks)
        if total == 0:
            judged_accuracy = "0/0 (0%)"
            judged_solvable = "0/0 (0%)"
        else:
            correct_count = sum(1 for t in tasks if t.get("correct"))
            solvable_count = sum(1 for t in tasks if t.get("is_solvable"))

            judged_accuracy = (
                f"{correct_count}/{total} ({correct_count / total * 100:.0f}%)"
            )
            judged_solvable = (
                f"{solvable_count}/{total} ({solvable_count / total * 100:.0f}%)"
            )

        table.append(
            {
                "Model": model,
                "Judged Accuracy": judged_accuracy,
                "Judged Solvable": judged_solvable,
            }
        )

    df = pd.DataFrame(table)
    # Optional: sort by accuracy descending
    df = df.sort_values("Judged Accuracy", ascending=False).reset_index(drop=True)
    return df


def generate_unsolvable_summary(data: dict[str, list]) -> pd.DataFrame:
    """
    Aggregates identical unsolvable_reason strings across all models
    and returns a count table.
    """

    reasons = []

    for _model, tasks in data.items():
        for task in tasks:
            reason = task.get("unsolvable_reason", "")
            if reason:  # ignore empty strings
                reasons.append(reason.strip())

    # Count identical reasons
    reason_counts = Counter(reasons)

    # Convert to DataFrame
    df = pd.DataFrame(reason_counts.items(), columns=["Unsolvable Reason", "Count"])

    # Sort by most frequent
    df = df.sort_values("Count", ascending=False).reset_index(drop=True)

    return df