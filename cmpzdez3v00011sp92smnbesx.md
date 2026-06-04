---
title: "Evaluation: Measuring our Agents capabilities with Gaia"
seoTitle: "AI Evaluation: measuring our agents capabilities"
seoDescription: "A blog post outlining an AI Agent evaluation technique using the Gaia dataset to measure the capability of an AI Agent built from scratch."
datePublished: 2026-06-04T10:46:58.369Z
cuid: cmpzdez3v00011sp92smnbesx
slug: evaluation-measuring-our-agents-capabilities-with-gaia
tags: ai, python, evaluation, gaia

---

When working with the non-deterministic nature of LLMs (the same prompt will return different responses each time, due to the probabilistic nature of LLMs) traditional means of software testing are not appropriate. How do we know if our agent is actually getting better? We need a benchmark in place we can measure our agent against to allow us to assess whether each tweak we make to our prompts and logic we are actually making progress.

I intend to make a 'Research Agent', a system that can gather information from multiple sources, analyse findings and produce comprehensive answers. Therefore we need test cases that have clear, verifiable answers, represent realistic user requests and cover a range of difficulty levels.

Gaia (General AI Assistants) is a dataset that includes a range of a questions that ranges in complexity based on it's level (1, 2, or 3). Level 1 questions generally require no tools, or at most one tool, with no more that n5 steps. Level 2 questions involve more steps, roughly between 5 and 10 and the combination of different tools. Level 3 questions are designed for a near-perfect general assistant, requiring arbitrarily long sequences of actions. An example of a potential Level 1 question is this:

> "If Eliud Kipchoge could maintain his marathon pace indefinitely, how long would it take to run to the Moon?"

As a user, for us to answer this question might comprise of the following steps:

1.  Google search to determine who 'Eliud Kipchoge' is.
    
2.  Once we have determined Eluid is a Olympian long-distance runner, we may look up Wikipedia to find his marathon pace.
    
3.  We then perform a web search to find the distance from the earth to the moon.
    
4.  We then discover due to the elliptical path of the moon, the distance varies and we need to decide on which measurement(s) to use.
    
5.  We perform a calculation using these numbers to determine the time it would take Eliud to run to the moon.
    

To solve this our agent would need the ability to call tools to perform calculations, potentially the ability to access the web if it does not possess this information in its initial training data. Our agent also needs to be able to reason over a number of steps.

> The answer by the way, rounded to the nearest 1000 hours is 17,000 hours.

By using a subset of these Gaia questions we can assess the capability of our agent and measure it's accuracy as we iterate our implementation.

* * *

### Loading the Gaia dataset

We can obtain the Gaia dataset from [HuggingFace](https://huggingface.co/) (*oversimplification*: think of HuggingFace as the GitHub of AI models). You will need a HuggingFace account and must accept the dataset's terms of use before accessing it.

Visit [https://huggingface.co/datasets/gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) and click the "Agree and access repository" button to accept the dataset's terms of use. You will then need to create an Access Token in your HuggingFace account and add this in your `.env` file under `HF_TOKEN` so that your code can retrieve the dataset.

You will need the `datasets` library from HuggingFace in your dependencies:

```shell
uv add datasets
```

The following code will load the Level 1 problems from the Gaia dataset in Python code which we can use in our agent for evaluating their ability to solve them:

```python
from datasets import load_dataset

level1_problems = load_dataset("gaia-benchmark/GAIA", "2023_level1", split="validation")
print(f"Number of Level 1 problems: {len(level1_problems)}")
print(f" problems: {level1_problems.features}")
```

Examining the output of these, allows us to find the "Eluid Kipchoge" marathon problem:

```json
{
    "task_id": "e1fc63a2-da7a-432f-be78-7c4a95598703",
    "question": (
        "If Eliud Kipchoge could maintain his record-making marathon pace "
        "indefinitely, how many thousand hours would it take him to run the "
        "distance between the Earth and the Moon at its closest approach? "
        "Please use the minimum perigee value on the Wikipedia page for the Moon "
        "when carrying out your calculation. Round your result to the nearest "
        "1000 hours and do not use any comma separators if necessary."
    ),
    "level": 1,
    "final_answer": "17",
    "file_name": "",
    "annotator_metadata": {
        "steps": (
            "1. Googled Eliud Kipchoge marathon pace.\n"
            "2. Found the minimum perigee distance to the Moon.\n"
            "3. Calculated total hours at constant pace.\n"
            "4. Rounded to the nearest 1000 hours."
        ),
        "tools": [
            "Web browser",
            "Search engine",
            "Calculator",
        ],
        "num_tools": 3,
    },
}
```

The `question` field contains what a user would ask our agent. `final_answer` is what we will assert to be the correct answer, in this case simply "17." The `file_name` field indicates whether the problem includes an attached file (empty here means no attachment). The `annotator_metadata` reveals what the problem creators needed to solve it, which includes a web browser, a search engine, and a calculator.

This metadata is particularly revealing. Even though this is a Level 1 problem, the "easiest" category, the annotators needed three different tools to solve it. They had to search for Kipchoge's marathon pace, look up the Earth-Moon perigee distance on Wikipedia, and perform calculations.

* * *

## Building our first agent

Now we have explored a number of concepts, we can create our first agent utilising these. We then test our agent using some Level 1 questions from the Gaia dataset.

I document this in [Building Your First Agent](https://rob212.github.io/rob-agent/building-your-first-agent/).