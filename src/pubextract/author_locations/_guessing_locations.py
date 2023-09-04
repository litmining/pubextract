from pathlib import Path
import re

from unidecode import unidecode
import pandas as pd
import numpy as np
# import en_core_web_sm

from pubextract.author_locations import _reading_xml


def _define_locations():
    cities_path = Path(__file__).parent / "_data" / "worldcities.csv"
    WORLD_CITIES = pd.read_csv(cities_path)
    COUNTRIES = set(WORLD_CITIES["country"])
    CITIES = set(WORLD_CITIES["city_ascii"])
    LOCATIONS = COUNTRIES.union(CITIES)
    COUNTRY_MAPPING = {
        "UK": "United Kingdom",
        "USA": "United States",
        "South Korea": "Korea, South",
    }
    return {
        'WORLD_CITIES': WORLD_CITIES,
        "COUNTRIES": COUNTRIES,
        "CITIES": CITIES,
        "LOCATIONS": LOCATIONS,
        "COUNTRY_MAPPING": COUNTRY_MAPPING,
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


def _get_entities(affiliation):
    aff = _preprocess_text(affiliation)
    # nlp = en_core_web_sm.load()
    # doc = nlp(aff)
    # items = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    items = []
    unigrams = aff.split(" ")
    items = items + unigrams
    for i, unigram in enumerate(unigrams[:-1]):
        bigram = " ".join([unigram, unigrams[i+1]])
        items.append(bigram)
    locs = _define_locations()
    CM = locs["COUNTRY_MAPPING"]
    items = [CM[x] if x in CM else x for x in items]
    entities = [x for x in items if x in locs["LOCATIONS"]]
    entities = [x.strip() for x in entities]
    entities = list(set(entities))
    return entities


def _get_location(ents):
    locs = _define_locations()
    cities = locs["CITIES"].intersection(set(ents))
    countries = locs["COUNTRIES"].intersection(set(ents))
    WC = locs["WORLD_CITIES"]
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


class LocationGuesser:
    def __init__(self, article_path):
        self.article_path = article_path
        self.tree = _reading_xml._get_tree(article_path)
        self.id = _reading_xml._get_id(self.tree)
        # self.metadata =

    def get_location(self):
        self.affiliation = _reading_xml._get_first_affiliation(self.tree)
        self.entities = _get_entities(self.affiliation)
        self.location = _get_location(self.entities)
