from pathlib import Path

import pandas as pd
import numpy as np

from neuroquery.tokenization import TextVectorizer

WORD_PATTERN = r"(?:(?:\p{L}|\p{N})+|[=<>]|\p{Math_Operators})"


# list of terms to search for
terms_path = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "pubextract"
    / "cluster_inference"
    / "cluster_inference_terms.csv"
)
TERMS = list(pd.read_csv(terms_path)["term"])
TERMS.sort()

anns_path = (
    Path(__file__).resolve().parent / "data" / "annotations" / "test_annotations.jsonl"
)
anns_dense = pd.read_json(anns_path, lines=True)
anns = anns_dense.explode("annotations").reset_index(drop=True)
for index, row in anns.iterrows():
    anns.loc[index, "pmcid"] = row.metadata["pmcid"]

docs_path = (
    Path(__file__).resolve().parent / "data" / "documents" / "test_documents.jsonl"
)
docs = pd.read_json(docs_path, lines=True)
for index, row in docs.iterrows():
    docs.loc[index, "pmcid"] = row.metadata["pmcid"]


answers = {
    1: {
        "n_participants": 50,
        "smoothing_kernel": 5,
        "cluster_inference_used": True,
    },
    2: {
        "n_participants": 15,
        "smoothing_kernel": 6,
        "cluster_inference_used": False,
    },
    3: {
        "n_participants": 395,
        "smoothing_kernel": 2,
        "cluster_inference_used": True,
    },
}


class SimpleTermSearch:
    def __init__(self):
        pass

    def fit(self, terms):
        self.terms = terms
        # self.label = label

    def termsearch(self, docs):
        results = pd.DataFrame(index=docs.index, columns=['pmcid'] + self.terms)
        for index, row in docs.iterrows():
            results.loc[index, 'pmcid'] = row.pmcid
            for term in self.terms:
                if term in row.text:
                    results.loc[index, term] = True
                    
        results = results.fillna(value=False)
        results = results.set_index('pmcid', drop=True)
        return results


simple_term_search = SimpleTermSearch()
simple_term_search.fit(terms=TERMS)
results = simple_term_search.termsearch(docs=docs)

# The first doc contains 'cluster-defining threshold'.
# It shouldn't match the term because of the dash
assert not results.iloc[0]['cluster defining threshold']

# The second document does not use cluster inference.
# So none of the terms should match
assert results.iloc[1].sum() == 0

# The third doc contains 'minimum volume'.
# This term should match
assert results.iloc[2]['minimum volume']


class NeuroQueryTermSearch:
    def __init__(self):
        pass

    def fit(self, original_terms):
        self.original_terms = original_terms
        self.text_vectorizer = TextVectorizer(self.original_terms)
        self.terms = self.text_vectorizer.tokenizer

    def termsearch(self, docs):
        texts = list(docs.text)
        results_ar = self.text_vectorizer(docs=texts).to_array()
        results = pd.DataFrame(data=results_ar, index=list(docs.pmcid), columns=self.terms)

        ################# working here ##########
        return results

nq_term_search = NeuroQueryTermSearch()
nq_term_search.fit(original_terms=TERMS)
nq_results = nq_term_search.termsearch(docs=docs)


# The first doc contains 'cluster-defining threshold'.
# It shouldn't match the term because the neuroquery preprocessing would
# get rid of the dash
assert results.iloc[0]['cluster defining threshold']

# The second document does not use cluster inference.
# So none of the terms should match
assert results.iloc[1].sum() == 0

# The third doc contains 'minimum volume'.
# This term should match
assert results.iloc[2]['minimum volume']



d = 1


# def get_excerpts(anns, docs, label):
#     anns_docs = pd.merge(anns, docs, on='pmcid', how='inner').reset_index(drop=True)
#     cols = [
#         'pmcid',
#         'label_name',
#         'selected_text',
#         'surrounding_text',
#     ]
#     df = pd.DataFrame(index=anns_docs.index, columns=cols)
#     addon = 100
#     for index, row in anns_docs.iterrows():
#         df.loc[index, 'pmcid'] = row['pmcid']
#         df.loc[index, 'selected_text'] = row.text[row.start_char:row.end_char]
#         df.loc[index, 'label_name'] = row.label_name
#         df.loc[index, 'surrounding_text'] = row.text[row.start_char - addon : row.end_char + addon]
#     return df
# get_excerpts(anns, docs, label='n_participants')


# def return_text_around_words(pmcid, word, text, n_chars_before_and_after=100):
#     starts = np.array([m.start() for m in re.finditer(word, text)])
#     ends = np.array([m.end() for m in re.finditer(word, text)])
#     i_befores = starts - n_chars_before_and_after
#     i_afters = ends + n_chars_before_and_after
#     texts_to_save = [text[b:a] for b, a in zip(i_befores, i_afters)]
#     text_around_words_dict = {
#         "pmcid": [pmcid] * len(starts),
#         "term": [word] * len(starts),
#         "start_char": starts,
#         "end_char": ends,
#         "surrounding_text": texts_to_save,
#     }
#     df = pd.DataFrame.from_dict(text_around_words_dict)
#     return df


# def wordsearch(pmcid, text, word, n_chars_before_and_after=100):
#     if word in text:
#         wordsearch_result = True
#         surrounding_texts_df = return_text_around_words(
#             pmcid, word, text, n_chars_before_and_after
#         )
#     else:
#         wordsearch_result = False

#     return wordsearch_result, surrounding_texts_df,
