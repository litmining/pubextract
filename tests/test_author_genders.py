from pathlib import Path

import pandas as pd

from pubextract.authors import author_genders


CSV_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "pubget_data"
    / "query_a63e5571ad90a97b9ac76dc0684e2fcf"
    / "subset_allArticles_extractedData"
    / "authors.csv"
)


def test_add_author_genders_to_csv():
    new_csv_path = author_genders.add_author_genders_to_csv(CSV_PATH)
    df = pd.read_csv(new_csv_path)
    assert df.iloc[-1]['gender'] == 'male'
    assert Path(new_csv_path).exists()
 
   
def test_prep_data_for_author_gender_figures():
    r, new_csv_path = (
        author_genders.prep_data_for_author_gender_figures(CSV_PATH)
    )
    n_unknown = len(r[r['category'] == 'Unknown'])
    n_wm = len(r[r['category'] == 'Woman-\nMan'])
    assert n_unknown > n_wm
    df = pd.read_csv(new_csv_path)
    assert df.iloc[-1]['gender'] == 'male'
    assert Path(new_csv_path).exists()

def test_make_author_gender_figure_and_csv():
    fig, r, df, new_csv_path, fig_path = (
        author_genders.make_author_gender_figure_and_csv(CSV_PATH)
    )
    n_unknown = len(r[r['category'] == 'Unknown'])
    n_wm = len(r[r['category'] == 'Woman-\nMan'])
    assert n_unknown > n_wm
    assert df.iloc[-1]['gender'] == 'Male'
    assert Path(fig_path).suffix == '.png'
    assert Path(fig_path).exists()
    assert Path(new_csv_path).exists()
