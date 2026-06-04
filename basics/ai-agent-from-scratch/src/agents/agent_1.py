## Agent 1
##
## Prompt directly to LLM.
##

import asyncio

from datasets import load_dataset
from dotenv import find_dotenv, load_dotenv
from evaluation.reporting import (
    generate_accuracy_table,
    generate_unsolvable_summary,
)
from evaluation.runner import run_experiment
from litellm import acompletion
from pydantic import BaseModel

# =========================
# Configuration
# =========================


MODELS = [
    "gpt-5",
    "gpt-5-mini",
    "anthropic/claude-sonnet-4-5",
    "anthropic/claude-haiku-4-5",
]

GAIA_SYSTEM_PROMPT = """ You are a general AI assistant. 
I will ask you a question. First, determine if you can solve this problem with your current capabilities and set "is_solvable" accordingly. 
If you can solve it, set "is_solvable" to true and provide your answer in "final_answer". 
If you cannot solve it, set "is_solvable" to false and explain why in "unsolvable_reason". 
Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. 
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. 
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. 
If you are asked for a comma separated list, apply the above rules depending on whether the element is a number or a string.”
"""

PROVIDER_SEMAPHORES = {
    "openai": asyncio.Semaphore(30),
    "anthropic": asyncio.Semaphore(10),
}


# =========================
# Agent Output Schema
# =========================


class GaiaOutput(BaseModel):
    is_solvable: bool
    unsolvable_reason: str = ""
    final_answer: str = ""


# =========================
# Agent Logic
# =========================


def get_provider(model: str) -> str:
    """Extract provider name from model string."""
    return "anthropic" if model.startswith("anthropic/") else "openai"


async def solve_problem(model: str, question: str) -> GaiaOutput:
    """Solve a single problem and return structured output."""
    provider = get_provider(model)

    async with PROVIDER_SEMAPHORES[provider]:
        response = await acompletion(
            model=model,
            messages=[
                {"role": "system", "content": GAIA_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            response_format=GaiaOutput,
            num_retries=2,
        )
        finish_reason = response.choices[0].finish_reason
        content = response.choices[0].message.content

        if finish_reason == "refusal" or content is None:
            return GaiaOutput(
                is_solvable=False,
                unsolvable_reason=f"Model refused to answer (finish_reason: {finish_reason})",
                final_answer="",
            )
        return GaiaOutput.model_validate_json(content)


# =========================
# Entry Execution
# =========================


async def run():
    load_dotenv(find_dotenv())

    dataset = load_dataset(
        "gaia-benchmark/GAIA",
        "2023_level1",
        split="validation",
    )

    subset = dataset.select(range(20))

    results = await run_experiment(subset, MODELS, solve_problem)

    stats = generate_accuracy_table(results)
    unsolvable = generate_unsolvable_summary(results)

    print("\n============= Accuracy Table =============")
    print(stats)

    print("\n============= Unsolvable Summary =============")
    print(unsolvable)


if __name__ == "__main__":
    asyncio.run(run())