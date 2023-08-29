import logging
from pathlib import Path

import pandas as pd

from pubextract.author_locations import _guessing_locations, _reading_xml


_STEP_NAME = "extract_author_locations"
_STEP_DESCRIPTION = "Extract author locations from studies' text."
_LOG = logging.getLogger(_STEP_NAME)


def _extract_from_articles_dir(articles_dir, output_dir=None):
    if output_dir is None:
        output_dir = articles_dir.parent / "subset_allArticles_authorLocations"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    ids = []
    locations = []
    entss = []
    article_paths = list(articles_dir.glob("**/article.xml"))
    for i_article, article_path in enumerate(article_paths):
        print("Processing article %d/%d" % (i_article, len(article_paths)), end="\r")
        ents = _guessing_locations._get_entities(article_path)
        location = _guessing_locations._get_location(ents)
        
        if not pd.isna(location):
            ids.append(_reading_xml._get_id(article_path))
            entss.append("; ".join(ents))
            locations.append(location)
        d = 1
    df = pd.DataFrame.from_records(locations)
    df["entities"] = entss
    df["id"] = ids
    df.to_csv(output_dir / "author_locations.csv")
