import logging
from pathlib import Path

import pandas as pd
import numpy as np
import folium

from pubextract.author_locations import _guessing_locations


_STEP_NAME = "extract_author_locations"
_STEP_DESCRIPTION = "Extract author locations from studies' text."
_LOG = logging.getLogger(_STEP_NAME)


def _create_map(df, output_dir):
    df = df.dropna(subset="lng")
    counts = df["country"].value_counts()
    data = pd.DataFrame(columns=["country", "count"])
    data["country"] = list(counts.index)
    data["count"] = list(counts.values)

    m = folium.Map(tiles="cartodb positron", zoom_start=2)
    political_countries_url = (
        "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
    )
    folium.Choropleth(
        geo_data=political_countries_url,
        data=data,
        columns=["country", "count"],
        popup=data["country"],
        key_on="feature.properties.name",
    ).add_to(m)

    for ind, row in df.iterrows():
        df.loc[ind, "str_coords"] = "%f, %f" % (row["lat"], row["lng"])
    RADIUS = .01
    for str_coords, group in df.groupby("str_coords"):
        row = group.iloc[0]
        LNG = row["lng"]
        LAT = row["lat"]
        n = len(group)
        T = np.linspace(0, 2*np.pi, n, endpoint=False)
        popup = f"{row.city}, {row.entities}"
        for (i, row), t in zip(group.iterrows(), T):
            radius = RADIUS * n
            lng = LNG + radius * np.sin(t)
            lat = LAT + radius * np.cos(t)
            if n == 1:
                lng = LNG
                lat = LAT
            folium.CircleMarker(
                [lat, lng],
                popup=popup,
                radius=.1,
                color="#f9190076",
                fill_color="#f9190076",
            ).add_to(m)
    m.save(output_dir / "author_locations_map.html")


def _extract_from_articles_dir(articles_dir, output_dir=None):
    if output_dir is None:
        output_dir = articles_dir.parent / "subset_allArticles_authorLocations"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    if articles_dir.name == "subset_allArticles_extractedData":
        articles_dir = articles_dir.parent / "articles"
    _LOG.info(f"Extracting author locations to {output_dir}")
    ids = []
    locations = []
    entss = []
    article_paths = list(articles_dir.glob("**/article.xml"))
    for i_article, article_path in enumerate(article_paths):
        print("Processing article %d/%d" % (i_article, len(article_paths)),
              end="\r")
        loc = _guessing_locations.LocationGuesser(article_path)
        loc.get_location()
        if not pd.isna(loc.location):
            ids.append(loc.id)
            entss.append("; ".join(loc.entities))
            locations.append(loc.location)

    df = pd.DataFrame.from_records(locations)
    if not df.empty:
        df["entities"] = entss
        df["id"] = ids
        df.to_csv(output_dir / "author_locations.csv")
        _LOG.info(f"Done extracting author locations to {output_dir}")
        _LOG.info("Creating map of author locations")
        _create_map(df, output_dir)
        _LOG.info(f"Done creating map of author locations in {output_dir}")
    return output_dir, 0


class AuthorLocationsStep:
    name = _STEP_NAME
    short_description = _STEP_DESCRIPTION

    def edit_argument_parser(self, argument_parser) -> None:
        argument_parser.add_argument(
            "--author_locations",
            action="store_true",
            help="Extract the location from the first affiliation",
        )

    def run(self, args, previous_steps_output):
        if not args.author_locations:
            return None, 0
        author_locations_dir = (
            previous_steps_output.get("extract_author_locations_data")
        )
        if author_locations_dir is None:
            author_locations_dir, _ = _extract_from_articles_dir(
                previous_steps_output["extract_data"]
            )
        return _extract_from_articles_dir(author_locations_dir)


class AuthorLocationsCommand:
    name = _STEP_NAME
    short_description = _STEP_DESCRIPTION

    def edit_argument_parser(self, argument_parser) -> None:
        argument_parser.add_argument(
            "author_locations_dir",
            help="Directory containing author locations. "
            "It is a directory created by pubget with the '--author_locations'"
            " option, whose name ends with 'authorLocations'."
        )

    def run(self, args):
        return _extract_from_articles_dir(Path(args.author_locations_dir))[1]


def get_pubget_actions():
    return {
        "pipeline_steps": [AuthorLocationsStep()],
        "commands": [AuthorLocationsCommand()]
    }
