## Importing the GAIA dataset from HuggingFace to use to evaulate our agent.
## It consists of a collection of level 1, 2 and 3 tasks, each requiring more complexity in an agent
## and it's available tolling to solve. The dataset contains questions with expected answers with to assess our agent's
## response against.

from datasets import load_dataset

level1_problems = load_dataset("gaia-benchmark/GAIA", "2023_level1", split="validation")
print(f"Number of Level 1 problems: {len(level1_problems)}")
print(f" problems: {level1_problems.features}")