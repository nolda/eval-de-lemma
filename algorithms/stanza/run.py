import json
import logging
import sys

import stanza

sys.path.append("../..")
from src.loader import load_data
from src.run import run_algorithm


# logging settings
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="../../logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)

DATASETSPATH = "../../datasets"

import warnings
warnings.filterwarnings("ignore")


# load stanza model
model = stanza.Pipeline(
    lang='de', processors='tokenize,pos,lemma',
    tokenize_pretokenized=True)


def predict(x_test, y_test, z_test, z_test_xpos, dname):
    """Performs lemmatization on a nested list of tokens using Stanza."""
    docs = model(x_test)
    return [[t.lemma for t in sent.words] for sent in docs.sentences]


# run all benchmarks
results = []

for x_test, y_test, z_test, z_test_xpos, dname in load_data(DATASETSPATH):
    try:
        results.append(run_algorithm(predict, x_test, y_test, z_test,
                                     z_test_xpos, dname, 'stanza'))
    except Exception as err:
        logger.error(err)


# store results
with open("../../nbs/results-stanza.json", "w") as fp:
    json.dump(results, fp, indent=4)


# run with PoS tags in input
# load stanza model
model = stanza.Pipeline(
    lang='de', processors='tokenize,lemma',
    lemma_pretagged=True, tokenize_pretokenized=True)


def predict(x_test, y_test, z_test, z_test_xpos, dname):
    """Performs lemmatization on a PoS-tagged list of tokens using Stanza."""
    lemmata = []
    for j, sent in enumerate(x_test):  # lemmatize by sentence
        doc = stanza.models.common.doc.Document([[{'id': i, 'text': token,
                                                   'upos': z_test[j][i]} for i,
                                                  token in enumerate(sent)]])
        doc_lemmatised = model(doc)
        lemmata += [[t.lemma for t in sent.words]
                    for sent in doc_lemmatised.sentences]
    return lemmata


# run all benchmarks
results = []

for x_test, y_test, z_test, z_test_xpos, dname in load_data(DATASETSPATH):
    try:
        results.append(run_algorithm(predict, x_test, y_test, z_test,
                                     z_test_xpos, dname, 'stanza-pretagged'))
    except Exception as err:
        logger.error(err)


# store results
with open("../../nbs/results-stanza-pretagged.json", "w") as fp:
    json.dump(results, fp, indent=4)
