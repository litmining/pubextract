from pathlib import Path
import re

import pandas as pd

from pubextract import term_search


def method_yn_from_term_search(docs, methods_labels=[]):
    """
    Infers whether a method was used by searching for a list of terms.

    Output
    ------
    results_df
        results dataframe, with the input documents' pmcids as the index,
        and the methods_labels as the columns.
        If the value in a cell is 1, that means we found at least one term for that method (column name) in the document with that pmcid (index).
    """
    terms_path = Path(__file__).resolve().parent / "_data" / "methods_terms.csv"
    terms_df = pd.read_csv(terms_path)

    if len(methods_labels) < 1:
        methods_labels = list(terms_df.columns)
    results_df = pd.DataFrame(index=docs["pmcid"], columns=methods_labels)

    for method in methods_labels:
        terms = list(terms_df.loc[:, method])
        terms.sort()

        # neuroquery object
        nq_term_search = term_search.NeuroQueryTermSearch(original_terms=terms)

        # dataframe: PMCID by terms
        term_search_results = nq_term_search.termsearch(docs=docs)

        # dataframe: PMCID by class (1: used cluster inference; 0: did not)
        classification_results = term_search_results.sum(axis=1)
        results_df.loc[:, method] = classification_results.values

    return results_df


def method_value_from_term_search(docs, methods_labels=[]):
    """
    Infers whether a method was used by searching for a list of terms.
    Then finds the sentence where the term was found.
    Then returns the value of the last number in that sentence.

    Output
    ------
    results_df
        results dataframe, with the input documents' pmcids as the index,
        and the methods_labels as the columns.
        The value in the cell is the last number found in the sentence where we found a term related to the given method (column name) in the document with that pmcid (index).
    """

    terms_path = Path(__file__).resolve().parent / "_data" / "methods_terms.csv"
    terms_df = pd.read_csv(terms_path)

    if len(methods_labels) < 1:
        methods_labels = list(terms_df.columns)

    results_df = pd.DataFrame(index=docs["pmcid"], columns=methods_labels)

    for method in methods_labels:
        terms = list(terms_df.loc[:, method].dropna())
        terms.sort()

        simple_term_search = term_search.SimpleTermSearch(terms=terms)
        ts_results = simple_term_search.termsearch(docs=docs, return_positions=True)

        results = pd.DataFrame(
            index=list(ts_results.index), columns=["sentence", "value"]
        )

        for index, row in docs.iterrows():
            pmcid = row["pmcid"]

            i_term = ts_results.loc[pmcid].sum()
            t = row.text
            text_before = t[:i_term]
            text_after = t[i_term:]
            i_period_before = text_before.rfind(". ") + 2
            i_period_after = text_after.find(". ") + i_term
            sentence = t[i_period_before:i_period_after]
            # results.loc[pmcid, 'sentence'] = sentence

            results_df.loc[pmcid, method] = int(re.findall(r"\b\d+\b", sentence)[-1])

    return results_df


# FOR FINDING THE MATCH CLOSEST TO THE FOUND TERM - NOT DONE
# i_term_in_sentence = i_term - i_period_before
# locs = []
# vals = []
# for match in re.finditer(r'\b\d+\b', sentence):
#     locs.append(match.span()[0])
#     vals.append(match.group())