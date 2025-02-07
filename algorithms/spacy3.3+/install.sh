#!/usr/bin/env bash

SRCDIR=$(dirname "$0")

# install venv
python3 -m venv "${SRCDIR}/.venv"
source "${SRCDIR}/.venv/bin/activate"
pip install --upgrade pip
pip install -r "${SRCDIR}/requirements.txt"

# download models
python -m spacy download de_dep_news_trf-3.3.0 --direct
