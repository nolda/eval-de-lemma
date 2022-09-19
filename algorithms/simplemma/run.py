import simplemma
import sys
import itertools
import json
import pandas as pd
import time
import tracemalloc

sys.path.append("../..")
from src.loader import load_data
from src.metrics import metrics_by_pos

DATASETSPATH = "../../datasets"

import warnings
warnings.filterwarnings("ignore")


# (A) Run all benchmarks
results = []
# store different lemmatizations
df = pd.DataFrame(columns=['corpus', 'token', 'pos', 'lemma_gold', 'lemma_pred'])

for x_test, y_test, z_test, dname in load_data(DATASETSPATH):
    try:
        # (A.1) encode labels and flatten sequences
        y_test = list(itertools.chain(*y_test))
        z_test = list(itertools.chain(*z_test))
        # (A.2) predict labels
        tracemalloc.start()
        t = time.time()
        y_pred = [[simplemma.lemmatize(t, lang='de') for t in sent]
                  for sent in x_test]
        elapsed = time.time() - t
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        y_pred = list(itertools.chain(*y_pred))
        x_test = list(itertools.chain(*x_test))
        # output incorrect lemmatizations
        for i in range(len(y_test)):
            if y_test[i] != y_pred[i]:
                df.loc[i] = [dname, x_test[i], z_test[i], y_test[i], y_pred[i]]
        # (A.3) Compute metrics
        metrics = metrics_by_pos(y_test, y_pred, z_test)
        # Save results
        results.append({
            'dataset': dname, 'sample-size': len(y_test),
            'lemmatizer': 'simplemma', 'metrics': metrics,
            'elapsed': elapsed, 'memory_current': current,
            'memory_peak': peak})
    except Exception as err:
        print(err)


# store results
with open("../../nbs/results-simplemma.json", "w") as fp:
    json.dump(results, fp, indent=4)
# output mis-lemmatizations
df.to_csv("../../nbs/lemmata-simplemma.csv")
