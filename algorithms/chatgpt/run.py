import json
import logging
import openai
import os
import sys
import time

sys.path.append("../..")
from src.loader import load_data
from src.run import run_algorithm


# logging settings
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="../../../logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)

DATASETSPATH = "../../datasets"

import warnings
warnings.filterwarnings("ignore")


# bash command: export OPEN_AI_KEY=INSERT_KEY_HERE
openai.api_key = os.environ["OPEN_AI_KEY"]


def predict(x_test, y_test, z_test, z_test_xpos):
    lemmata = []
    tokens = 0
    with open('../../nbs/openai_responses.txt', 'w', encoding='utf-8') as f:
        for sent in x_test:
            prompt = f"Lemmatisiere die Tokenliste: {sent}"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=len(prompt)
            )
            answer = response["choices"][0]["text"]
            tokens += response['usage']['total_tokens']
            # response structure:
            # \n\nDie Tokenliste wird lemmatisiert zu: ['lemma1', '...']
            try:
                lemmata.append(lemma.strip("'[]") for lemma in
                               answer.split(': ')[1].split("', "))
            except Exception as e:
                logger.error(e, answer)
            f.write(answer+'\n')
            time.sleep(3.)  # prevent rate limit errors
            # see https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
    print(f"{tokens} tokens used.")
    return lemmata


# (A) Run all benchmarks
results = []

for x_test, y_test, z_test, z_test_xpos, dname in load_data(DATASETSPATH):
    try:
        results.append(run_algorithm(predict, x_test, y_test, z_test,
                                     z_test_xpos, dname, 'chatgpt'))
    except Exception as err:
        logger.error(err)


# store results
with open("../../nbs/results-chatgpt.json", "w") as fp:
    json.dump(results, fp, indent=4)
