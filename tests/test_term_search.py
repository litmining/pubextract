from pathlib import Path

import pandas as pd
import numpy as np

from pubextract import term_search


# list of terms to search for
terms_path = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "pubextract"
    / "methods_terms.csv"
)
TERMS = list(pd.read_csv(terms_path)["cluster_inference"])
TERMS.sort()

docs_path = (
    Path(__file__).resolve().parent / "data" / "documents" / "test_documents.jsonl"
)
DOCS = pd.read_json(docs_path, lines=True)
for index, row in DOCS.iterrows():
    DOCS.loc[index, "pmcid"] = row.metadata["pmcid"]


def test_simple_term_search():
    # SIMPLE TERM SEARCH - i.e., with no text preprocessing or vectorization
    simple_term_search = term_search.SimpleTermSearch(terms=TERMS)
    simple_results = simple_term_search.termsearch(docs=DOCS)

    # The first doc contains 'cluster-defining threshold'.
    # It shouldn't match the term because of the dash
    assert not simple_results.iloc[0]["cluster defining threshold"]

    # The second document does not use cluster inference.
    # So none of the terms should match
    assert simple_results.iloc[1].sum() == 0

    # The third doc contains 'minimum volume'.
    # This term should match
    assert simple_results.iloc[2]["minimum volume"]


def test_neuroquery_term_search():
    # NEUROQUERY TERM SEARCH - i.e., look for terms after preprocessing terms & text
    nq_term_search = term_search.NeuroQueryTermSearch(original_terms=TERMS)
    nq_results = nq_term_search.termsearch(docs=DOCS)

    # The first doc contains 'cluster-defining threshold'.
    # It shouldn't match the term because the neuroquery preprocessing would
    # get rid of the dash
    assert nq_results.iloc[0]["cluster defining threshold"]

    # The second document does not use cluster inference.
    # So none of the terms should match
    assert nq_results.iloc[1].sum() == 0

    # The third doc contains 'minimum volume'.
    # This term should match
    assert nq_results.iloc[2]["minimum volume"]


# anns_path = (
#     Path(__file__).resolve().parent / "data" / "annotations" / "test_annotations.jsonl"
# )
# anns_dense = pd.read_json(anns_path, lines=True)
# anns = anns_dense.explode("annotations").reset_index(drop=True)
# for index, row in anns.iterrows():
#     anns.loc[index, "pmcid"] = row.metadata["pmcid"]

# nq_answers = {
#     1: {
#         "n_participants": 50,
#         "smoothing_kernel": 5,
#         "cluster_inference_used": True,
#     },
#     2: {
#         "n_participants": 15,
#         "smoothing_kernel": 6,
#         "cluster_inference_used": False,
#     },
#     3: {
#         "n_participants": 395,
#         "smoothing_kernel": 2,
#         "cluster_inference_used": True,
#     },
# }
