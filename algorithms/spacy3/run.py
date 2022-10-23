import sys
import json
import spacy

sys.path.append("../..")
from src.loader import load_data
from src.run import run_algorithm

DATASETSPATH = "../../datasets"

import warnings
warnings.filterwarnings("ignore")

# (A) Instanciate SpaCy model
model = spacy.load('de_dep_news_trf')
model.disable_pipes(["parser"])


def predict(x_test, y_test, z_test):
    lemmatizer = model.pipeline[4][1]
    docs = [lemmatizer(spacy.tokens.doc.Doc(model.vocab, words=sequence))
            for sequence in x_test]
    return [[w.lemma_ for w in doc] for doc in docs]


# (B) Run all benchmarks
results = []

for x_test, y_test, z_test, dname in load_data(DATASETSPATH):
    try:
        results.append(run_algorithm(predict, x_test, y_test, z_test, dname,
                                     'spacy3'))
    except Exception as err:
        print(err)


# store results
with open("../../nbs/results-spacy3.json", "w") as fp:
    json.dump(results, fp, indent=4)
