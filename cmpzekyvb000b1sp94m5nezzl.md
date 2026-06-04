---
title: "🤖 Building Your First AI Agent"
seoTitle: "Building your first AI Agent"
seoDescription: "A tutorial blog post on how to build your first AI Agent from Scratch using Foundation Models. Learning the basics of AI Agents through practice."
datePublished: 2026-06-04T11:19:37.613Z
cuid: cmpzekyvb000b1sp94m5nezzl
slug: building-your-first-ai-agent
cover: https://cdn.hashnode.com/uploads/covers/6a1ed89dc5484173f87dd5bd/c3657bcb-8787-4f81-9250-05754d8d1cc3.jpg
tags: ai, python, learning, beginners, ai-agents

---

To create our first AI agent, we will build upon the [basic concepts](https://ai-notebook.uk/basic-concepts-when-building-ai-agents) we explored previously.

To complete our agent, we need to complete a number of tasks:

*   define our structured output response format
    
*   create our system prompt to elicit a more relevant LLM response
    
*   create a `solve_problem` with API calling and error handling
    
*   select which models to test
    
*   establish how we'll judge correctness
    

* * *

## Defining our Structured Output response format

We'll instruct the LLM to respond to our question in a specific format that will allow us to reliably extract the model's final answer for comparison with that of the suggested answer in the [Gaia dataset](https://ai-notebook.uk/evaluation-measuring-our-agents-capabilities-with-gaia).

```python
from pydantic import BaseModel

class GaiaOutput(BaseModel):
    is_solvable: bool
    unsolvable_reason: str = ""
    final_answer: str = ""
```

The `is_solvable` field will be populated by the LLM to indicate as to whether it believes it can solve the problem with it's current capabilities. When `is_solvable` is False, we will ask the LLM to populate the unsolvable\_reason field with why the model cannot provide an answer. For example, "I need current information but cannot search the web".

Making both the unsolvable\_reason and final\_answer optional with empty string defaults allow clean handling of both solvable and unsolvable cases.

* * *

## System prompt

This is the prompt we will provide to our LLM to define it's identity and how it should behave.

```python
GAIA_SYSTEM_PROMPT = """ You are a general AI assistant.
I will ask you a question. First, determine if you can solve this problem with your current capabilities and set "is_solvable" accordingly.
If you can solve it, set "is_solvable" to true and provide your answer in "final_answer".
If you cannot solve it, set "is_solvable" to false and explain why in "unsolvable_reason".
Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending on whether the element is a number or a string.”
"""
```

The prompt is intended to elicit responses from our LLM that can be easily compared directly against Gaia's `final_answer` format. This style of well defined prompt creation is often referred to as 'Prompt Engineering', ensuring to give the LLM as much relevant context as possible in a succinct fashion to increase the likelihood of the outcome you are targeting.

* * *

## 🏎️ Managing API rate limits

For this agent, I plan to utilise both OpenAI LLMs and Anthropic LLMs in order to measure the effects they have on our agent when tasked with some Gaia problems. Different providers impose different rate limits on API request, they also depend on your API tier and usage history. We will therefore create a separate semaphore for each LLM provider, this will prevent a burst of requests to one provider from blocking requests to another. (see [Basic concepts - Asynchronous calls for a recap](https://ai-notebook.uk/basic-concepts-when-building-ai-agents))

```python
PROVIDER_SEMAPHORES = {
    "openai": asyncio.Semaphore(30),
    "anthropic": asyncio.Semaphore(10),
}

def get_provider(model: str) -> str:
    """Extract provider name from model string."""
    return "anthropic" if model.startswith("anthropic/") else "openai"
```

These semaphore values (30 for OpenAI, 10 for Anthropic) are conservative starting points that should work for most API tiers.

* * *

## Core `solve_problem` function

Our `solve_problem` function handles a single API call with rate limiting and error handling. It acquires the appropriate semaphore for the model it has been passed before making the request.

```python
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
```

Our function uses `async with` to acquire and release the semaphore automatically. We call Litellm's `acompletion` with our system prompt and the problem question that will originate from our Gaia dataset. The `response_format=GaiaOutput` parameter is us leveraging structured output via our Pydantic data model. (see [Basic concepts - Structured output](https://ai-notebook.uk/basic-concepts-when-building-ai-agents) for a recap). The `num-retries=2` handles transient failures automatically.

Some LLM models may refuse to answer our user's question for safety reasons, returning a "refusal" finish reason. We handle this case by capturing this as an "unsolvable problem" with an appropriate reason from the LLM as opposed to raising an exception.

* * *

## 🧪 Runner and Test framework

I want to separate the logic of my runner code, test code and agent itself.

To do so , I have opted for the current project structure:

```shell
ai-agent-from-scratch/
│
├── src/
|   ├── agents/
|       ├── __init__.py
|       ├── agent_1.py
|   ├── evaluation/
|       ├── __init__.py
|       ├── runner.py
|       ├── reporting.py
│...
```

My agent core logic will reside in `agents/`[`agent-1.py`](http://agent-1.py). My runner will reside in `evaluation/runner.py`and be resposible for the `run_experiment`function that runs a series of Gaia problems to my agent and assess the "correctness" of it's response. Finally the`evaluation/`[`reporting.py`](http://reporting.py) will generate reports to the terminal with a summarisation of results of the experiment.

* * *

### Runner implementation

We start by defining a simple `is_correct` function to compare our agents final answer to that provided in the Gaia dataset for the given question.

```python
def _is_correct(prediction: str | None, answer: str) -> bool:
    """Check exact match between prediction and answer (case-insensitive)."""
    if prediction is None:
        return False
    return prediction.strip().lower() == answer.strip().lower()
```

We then define a `evaluate_gaia_single` function that takes a dictionary representation of the Gaia problem, our LLM model and reference to our agents solve\_function and returns an object summarising the outcome:

```python
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
```

Finally the `run_experiment` function with an argument that takes a list of Gaia problems, a list of LLM models to plug into the agent, and a reference to the agent's `solve_problem` function. This intentional decoupling should allow us to re-use this runner with multiple, Gaia problem sets, any LLM models and an iteration of our agent.

```python
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
```

The final version of our `evaluation/runner.py` looks like this:

```python
## runner.py

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
```

* * *

### 📝 Reporting implementation

When we run an "experiment" with the above runner, it will iterate over a list of Gaia problems we provide, passing each one to our agent, configured with an LLM model, gather data about the output of our agent and assess if it successfully resolved the problem.

I intend to run the same test with my first agent, using the following closed LLMs as the "🧠 brain" of my agent:

*   "gpt-5" from OpenAI
    
*   "gpt-5-mini" from OpenAI
    
*   "claude-sonnet-4-5" from Anthropic
    
*   "claude-haiku-4-5" from Anthropic
    

> Note: A "closed LLM" is one that can only be accessed through an API, examples being OpenAI's GPT, Anthropic's Claude or Google's Gemini. An "Open LLM" are models whose weights can be downloaded, run locally and fine-tuned, examples include Meta's Llama, Mistral AI's Mistral, Alibaba's Qwen and Deepseek. For the scope of my initial agent learning I will only be looking at Closed LLM's while I explore AI Agents. The model is effectively a black box. \\

I therefore want to create some quick reporting functionality in order to capture and display the results of my runner. I capture this in the module `evaluation/reporting.py` and use the popular Python Pandas library. The code in my `reporting.py` module has no AI Agent specific code and is pure Python, therefore feel free to define your own or copy this as is:

```python
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
         
```

* * *

## 🤖 Our first Agent

Pulling this all together, we can have our experiment entry point be in `agents/agent_1.py` module in the form of a asynchronous `run` function. This will load our environment variables, select 20 level 1 questions for the Gaia dataset and orchestrate the runner and reporting.

The final code for our first AI agent is as follows:

```python
## src/agents/agent_1.py

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
```

This can be run by navigating to our `src` directory and running the command:

```shell
uv run python -m agents.agent_1
```

This will run our agent for each of our four provided LLM's, each answering 20 questions from the Gaia dataset, a total 80 api calls. Be aware this monetary cost will be taken from your OpenAI and Anthropic accounts. Our summary table will be output to the console and will resemble the following.

```shell
============= Accuracy Table =============
                         Model Judged Accuracy Judged Solvable
0                        gpt-5      7/20 (35%)     10/20 (50%)
1                   gpt-5-mini      6/20 (30%)      8/20 (40%)
2   anthropic/claude-haiku-4-5      2/20 (10%)      6/20 (30%)
3  anthropic/claude-sonnet-4-5       1/20 (5%)      7/20 (35%)
```

The '**Model**' column states the LLM that was used, the '**Judged Accuracy**' is the count of correct answers provided by the agent/model combination. E.g. Whether our agent provided a `final_answer` that matched that provided in the Gaia dataset for the particular questions. The '**Judged Solvable**' column shows the number of questions, out of the 20 we provided that our agent/model deemed solvable with it's current capabilities.

An interesting observation is that the models differ in judging whether they can solve a problem. One model was conservative, judging only six problems solvable with it's current capabilities, however, only actually answered two correctly according to our Gaia measure. Contrast this to another model, which judged it could solve 10 of the problems, but only managed to solve seven. This calibration of the models ability to assess whether it could accurately highlights the importance of selecting the most suitable model for the task at hand.

A possible explanation to this variance in judged solvability might be explained is the training data used to train the model. Modern LLMs are trained on vast amounts of web content, including Wikipedia articles and reference materials. If our Gaia questions asks about a well documented fact, the model *may* have encountered this information during training.

However, this "knowledge" isn't fully reliable for agent development. The model cannot distinguish between information it knows accurately versus information it is confabulating.

The entire code for this example can be found in my accompanying [GitHub repository.](https://github.com/rob212/ai-notebook)

* * *

### ✋ Model refusal

Another observation is that some models may refuse to answer certain problems entirely and will not even attempt an answer.

The Gaia dataset contains a problem (task\_id: 2d83110e-a098-4ebb-9987-066c06fa42d0) with the following question:

> .rewsna eht sa "tfel" drow eht fo etisoppo eht etirw ,ecnetnes siht dnatsrednu uoy fI

When reversed, this simply asks to write the opposite of "left" as the answer. However, some models can flag this as a potential attempt to bypass safety filters through obfuscation and refused to engage.

* * *

## 🤔 Unsolved questions

Out of our 20 Gaia problems, a number of them were deemed unsolvable by our agent, why is this?

We can analyse the output of our agent, which through our structured output, we asked the LLM's final response to include an 'unsolvable\_reason'.

These include explanations highlighting that our agent does not have access to search the web for content that may be pertinent to the problem that is not included in it's training data.

Other reasons include, the ability to read files, access a database or spreadsheet etc.

This reveals that LLMs have reasonable self-awareness of their limitations. When properly prompted, models can often identify when they cannot solve a problem. This is valuable because an agent that knows what it cannot do can use appropriate tools we can provide to it instead.

It also highlights that training data alone is not sufficient for answering some typical "real world" questions. Even when the models "know" information from training, this knowledge can be unreliable for precise, current or verifiable answers.

In our sample, even the best results reveals that 65% of even the "easiest" Gaia problems required tools. For an agent in this context, must be able to access the web, read files, perform calculations etc.

* * *

## Next steps

Now we have experimented with our first agent, our learnings indicate we should explore introducing "tools" to their capabilities.

We will do this by learning how about [Tool definitions](https://ai-notebook.uk/llm-tools).