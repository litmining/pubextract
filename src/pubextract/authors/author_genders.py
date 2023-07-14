from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import gender_guesser.detector as gender_detector


def add_author_genders_to_csv(csv_path):
    detect_gender = gender_detector.Detector(case_sensitive=False)
    df = pd.read_csv(csv_path)
    df = df.dropna()
    for i, row in df.iterrows():
        name = row["given-names"]
        if name is not np.nan:
            if name.find(" ") > 0:
                name = name.split(" ")[0]
            gender = detect_gender.get_gender(name)
            df.loc[i, "gender"] = gender
    new_csv_path = str(csv_path)[:-4] + "_with_genders.csv"
    df.to_csv(new_csv_path, index=False)
    return new_csv_path


def prep_data_for_author_gender_figures(csv_path):
    new_csv_path = add_author_genders_to_csv(csv_path)
    df = pd.read_csv(new_csv_path)

    # get first and last authors
    r = pd.DataFrame().astype(object)
    i = -1
    for pmcid, group in df.groupby("pmcid"):
        i = i + 1
        r.loc[i, "pmcid"] = pmcid
        r.loc[i, "first_given-names"] = group.iloc[0]["given-names"]
        r.loc[i, "first_gender"] = group.iloc[0]["gender"]
        r.loc[i, "last_given-names"] = group.iloc[-1]["given-names"]
        r.loc[i, "last_gender"] = group.iloc[-1]["gender"]
    # simplify gender options
    gender_mapping = {
        "female": "female",
        "mostly_female": "female",
        "andy": "androgenous",
        "mostly_male": "male",
        "male": "male",
        "unknown": "unknown",
    }
    for i, row in r.iterrows():
        r.loc[i, "first_gender"] = gender_mapping[row["first_gender"]]
        r.loc[i, "last_gender"] = gender_mapping[row["last_gender"]]

    # categorize papers as MM, MW, WM, or WW
    r["category"] = ""
    for ind, row in r.iterrows():
        first, last = row["first_gender"], row["last_gender"]
        if first == "female":
            if last == "female":
                r.loc[ind, "category"] = "Woman-\nWoman"
            if last == "male":
                r.loc[ind, "category"] = "Woman-\nMan"
        if first == "male":
            if last == "female":
                r.loc[ind, "category"] = "Man-\nWoman"
            if last == "male":
                r.loc[ind, "category"] = "Man-\nMan"
        if r.loc[ind, "category"] == "":
            r.loc[ind, "category"] = "Unknown"
    return r, new_csv_path


def make_author_gender_figure_and_csv(csv_path):
    r, new_csv_path = prep_data_for_author_gender_figures(csv_path)
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    category_counts = r["category"].value_counts(normalize=True)
    category_counts.plot(kind="bar", ax=axs[0])
    axs[0].set_ylabel("Proportion of papers with given author category")
    axs[0].set_xlabel("Author-gender category\n(gender of first and last authors)")
    axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=0)

    df = pd.read_csv(new_csv_path)
    gender_mapping = {
        "female": "Female",
        "mostly_female": "Female",
        "andy": "Androgenous",
        "mostly_male": "Male",
        "male": "Male",
        "unknown": "Unknown",
    }
    for i, row in df.iterrows():
        df.loc[i, "gender"] = gender_mapping[row.gender]
    gender_counts = df["gender"].value_counts(normalize=True)
    gender_counts.plot(kind="bar", ax=axs[1])
    axs[1].set_ylabel("Proportion of authors with given gender\n(all authors)")
    axs[1].set_xlabel("Category of guessed gender")
    axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=0)

    fig.tight_layout()
    fig_path = str(csv_path)[:-4] + "_gender_figure.png"
    fig.savefig(fig_path)
