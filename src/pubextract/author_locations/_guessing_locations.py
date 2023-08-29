from pathlib import Path
import re

from unidecode import unidecode
import pandas as pd
import numpy as np
import en_core_web_sm

from pubextract.author_locations import _reading_xml


cities_path = Path(__file__).parent / "_data" / "worldcities.csv"
WC = pd.read_csv(cities_path)
WC = WC.dropna()
COUNTRIES = set(WC["country"])
CITIES = set(WC["city_ascii"])
LOCATIONS = COUNTRIES.union(CITIES)
COUNTRY_MAPPING = {
    "UK": "United Kingdom",
    "USA": "United States",
    "South Korea": "Korea, South",
}


def _preprocess_text(text):
    to_remove = [
        "org/1999",
        "/addr-line",
        "/aff",
        "/Affiliation"
        "University",
        "College",
        "Center"
    ]
    text = re.sub(r'[,.;@#?!&$><:="-]+\ *', " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    text = unidecode(text)
    for item in to_remove:
        text = text.replace(item, "")
    return text


def _get_entities(article_path):
    aff = _reading_xml._get_first_affiliation(article_path)
    aff = _preprocess_text(aff)
    nlp = en_core_web_sm.load()
    doc = nlp(aff)
    items = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    unigrams = aff.split(" ")
    items = items + unigrams
    for i, unigram in enumerate(unigrams[:-1]):
        bigram = " ".join([unigram, unigrams[i+1]])
        items.append(bigram)
    entities = [x for x in items if x in LOCATIONS]
    entities = [x.strip() for x in entities]
    entities = list(set(entities))
    return entities


def _get_location(ents):
    ents = [COUNTRY_MAPPING[x] if x in COUNTRY_MAPPING else x for x in ents]
    cities = CITIES.intersection(set(ents))
    countries = COUNTRIES.intersection(set(ents))
    i_ci = WC[WC["city_ascii"].isin(cities)].index
    i_co = WC[WC["country"].isin(countries)].index
    i = i_ci.intersection(i_co)
    if not countries:
        i = i_ci
    if len(i) > 0:
        # the [0] is to take the first match
        location = WC.loc[i[0]].to_dict()
    else:
        location = np.nan
    return location

# class Locations:
#     def __init__(self, article_path):
#         self.article_path = article_path
#         self.id = _reading_xml._get_id(article_path)
#         self.affiliation = _reading_xml._get_first_affiliation(article_path)
#         # self.tree = _reading._get_tree(article_path)
#         self.entities = self._get_entities()
#         self.locations = self._get_locations()
