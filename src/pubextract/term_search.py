from pathlib import Path

import pandas as pd
import numpy as np

from neuroquery.tokenization import TextVectorizer


WORD_PATTERN = r"(?:(?:\p{L}|\p{N})+|[=<>]|\p{Math_Operators})"


class SimpleTermSearch:
    def __init__(self):
        pass

    def fit(self, terms):
        self.terms = terms
        # self.label = label

    def termsearch(self, docs):
        results = pd.DataFrame(index=docs.index, columns=["pmcid"] + self.terms)
        for index, row in docs.iterrows():
            results.loc[index, "pmcid"] = row.pmcid
            for term in self.terms:
                if term in row.text:
                    results.loc[index, term] = True

        results = results.fillna(value=False)
        results = results.set_index("pmcid", drop=True)
        return results


class NeuroQueryTermSearch:
    def __init__(self):
        pass

    def fit(self, original_terms):
        self.original_terms = original_terms
        self.text_vectorizer = TextVectorizer.from_vocabulary(
            self.original_terms, token_pattern=WORD_PATTERN
        )
        self.terms = self.text_vectorizer.get_vocabulary()
        # self.text_vectorizer = TextVectorizer(self.original_terms)
        # self.terms = self.text_vectorizer.from_vocabulary(voc=self.original_terms)

    def termsearch(self, docs):
        texts = list(docs.text)
        results_ar = self.text_vectorizer.transform(docs=texts).toarray()
        results = pd.DataFrame(
            data=results_ar, index=list(docs.pmcid), columns=self.terms
        )
        results = results.replace(to_replace=0.0, value=False)
        results = results.replace(to_replace=1.0, value=True)
        return results


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
