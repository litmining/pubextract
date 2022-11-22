from pathlib import Path

import pandas as pd

from pubextract.methods_finder import methods_finder


docs_path = (
    Path(__file__).resolve().parent / "data" / "documents" / "test_documents.jsonl"
)
DOCS = pd.read_json(docs_path, lines=True)
for index, row in DOCS.iterrows():
    DOCS.loc[index, "pmcid"] = row.metadata["pmcid"]

answers = {"cluster_inference": [1, 0, 1], "smoothing_kernel": [5, 6, 2]}


def test_method_yn_from_search_term():
    method = "cluster_inference"
    CI_results = methods_finder.method_yn_from_term_search(
        docs=DOCS, methods_labels=[method]
    )
    assert list(CI_results[method].values) == answers[method]


def test_method_values_from_search_term():
    method = "smoothing_kernel"
    ss_results = methods_finder.method_value_from_term_search(
        docs=DOCS, methods_labels=[method]
    )
    assert list(ss_results[method].values) == answers[method]
