from tqdm.asyncio import tqdm_asyncio


def _is_correct(prediction: str | None, answer: str) -> bool:
    """Check exact match between prediction and answer (case-insensitive)."""
    if prediction is None:
        return False
    return prediction.strip().lower() == answer.strip().lower()

async def _evaluate_gaia_single(problem: dict, model: str, solve_fn) -> dict:
    """Evaluate a single problem-model pair and return result."""
    try:
        output = await solve_fn(model, problem["Question"])
        return {
            "task_id": problem["task_id"],
            "model": model,
            "correct": _is_correct(output.final_answer, problem["Final answer"]),
            "is_solvable": output.is_solvable,
            "prediction": output.final_answer,
            "answer": problem["Final answer"],
            "unsolvable_reason": output.unsolvable_reason,
        }
    except Exception as e:
        return {
            "task_id": problem["task_id"],
            "model": model,
            "correct": False,
            "is_solvable": None,
            "prediction": None,
            "answer": problem["Final answer"],
            "error": str(e),
        }


async def run_experiment(
    problems: list[dict], models: list[str], solve_fn
) -> dict[str, list]:
    """Evaluate all models on all problems."""
    tasks = [
        _evaluate_gaia_single(problem, model, solve_fn)
        for problem in problems
        for model in models
    ]

    all_results = await tqdm_asyncio.gather(*tasks)

    # Group results by model
    results = {model: [] for model in models}
    for result in all_results:
        results[result["model"]].append(result)

    return results