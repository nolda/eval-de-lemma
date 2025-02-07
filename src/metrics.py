# -*- coding: utf-8 -*-
from typing import List
import logging

from nltk.metrics import edit_distance
import numpy as np
import pandas as pd
from sklearn.metrics import (recall_score, precision_score, f1_score,
                             accuracy_score, balanced_accuracy_score)

from src.reader import pos_dict


# logging settings
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="../logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(lineno)d - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)


def log_levenshtein(y_true: List[str], y_pred: List[str], sub: int = 1) \
        -> float:
    """Compute the logarithmized Levenshtein distance.

    Parameters
    ----------
    y_true : List[str]
        List of gold lemmata.
    y_pred : List[str]
        List of predicted lemmata.
    sub : int, optional
        Cost for a substition (deletion and insertion costs are 1).
        The default is 1.

    Returns
    -------
    float
        Logarithmized Levenshtein distance.
    """
    N = len(y_true)
    try:
        loglev = sum(np.log(edit_distance(y_true[i], y_pred[i],
                                          substitution_cost=sub) + 1)
                     for i in range(N)) / N
        return loglev
    except Exception as e:
        logger.error(e)


def levenshtein(y_true: List[str], y_pred: List[str]) -> float:
    """Compute average Levenshtein distance."""
    N = len(y_true)
    try:
        lev = sum((edit_distance(y_true[i], y_pred[i]))
                  for i in range(N)) / N
        return lev
    except Exception as e:
        logger.error(e)


def levenshtein_wordlen(y_true: List[str], y_pred: List[str]) -> float:
    """Compute average Levenshtein distance normalized by word length."""
    N = len(y_true)
    try:
        lev = sum((edit_distance(y_true[i], y_pred[i])/len(y_true[i]))
                  for i in range(N)) / N
        return lev
    except Exception as e:
        logger.error(e)


def compute_metrics(y_true: List[str], y_pred: List[str]) -> dict:
    """Compute different token-level and character-level metrics."""
    res = {}
    res['number_of_lemmata'] = len(y_true)

    if y_pred:  # prevent 0-division error
        try:
            res['accuracy'] = accuracy_score(y_true, y_pred)
        except Exception as e:
            logger.error(e)

        try:
            res['adj_recall'] = recall_score(y_true, y_pred, average='macro',
                                             zero_division=0)
        except Exception as e:
            logger.error(e)

        try:
            res['adj_precision'] = precision_score(y_true, y_pred,
                                                   average='macro',
                                                   zero_division=0)

        except Exception as e:
            logger.error(e)

        try:
            res['adj_f1'] = f1_score(y_true, y_pred, average='macro',
                                     zero_division=0)
        except Exception as e:
            logger.error(e)

        try:
            res['bal_accuracy'] = balanced_accuracy_score(y_true, y_pred,
                                                          adjusted=True)
        except Exception as e:
            logger.error(e)

        res['log-levenshtein'] = log_levenshtein(y_true, y_pred)
        res['log-levenshtein2'] = log_levenshtein(y_true, y_pred, sub=2)
        res['levenshtein'] = levenshtein(y_true, y_pred)
        res['levenshtein-wordlen'] = levenshtein_wordlen(y_true, y_pred)
        # number of gold and predicted lemma types, ratio gold/predicted
        res['true-pred-types'] = (len(set(y_true)), len(set(y_pred)),
                                  len(set(y_true))/len(set(y_pred)))
    return res


def metrics_by_pos(y_true: List[str], y_pred: List[str], z_upos: List[str],
                   z_xpos, UPOS: set = {'ADJ', 'ADV', 'NOUN', 'PROPN',
                                        'VERB'}) -> dict:
    """Compute metrics overall, by uPoS and xPoS tag."""
    res = {}
    data = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred, 'uPoS': z_upos,
                         'xPoS': z_xpos})
    data_content = data[data['uPoS'].isin(UPOS)]  # content words only
    XPOS = {p[0] for p in pos_dict.items() if p[1] in UPOS}
    # ignore POS tags other than content words for overall metrics
    res['overall'] = compute_metrics(data_content.y_true.tolist(),
                                     data_content.y_pred.tolist())
    for p in UPOS:  # metrics per uPoS tag
        p_entries = data_content[data_content['uPoS'] == p]
        if not p_entries.empty:
            res[p] = compute_metrics(p_entries.y_true.tolist(),
                                     p_entries.y_pred.tolist())
    for p in XPOS:  # metrics per xPoS tag
        p_entries = data_content[data_content['xPoS'] == p]
        if not p_entries.empty:
            res[p] = compute_metrics(p_entries.y_true.tolist(),
                                     p_entries.y_pred.tolist())
    return res
