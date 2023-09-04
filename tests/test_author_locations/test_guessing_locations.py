from pathlib import Path

from pubextract.author_locations import _reading_xml, _guessing_locations


def example_xml():
    folder = Path(__file__).parent.joinpath("data")
    for path in folder.glob("*.xml"):
        yield path.read_text("utf-8")


def test_define_locations():
    locs = _guessing_locations._define_locations()
    assert len(locs["LOCATIONS"]) > 0
    assert "United Kingdom" in locs["LOCATIONS"]
    assert "Pittsburgh" in locs["CITIES"]


def test_preprocess_text():
    text = (
        "<Affiliation>University of Pittsburgh, New York, PA, USA"
        "</Affiliation>"
    )
    processed = _guessing_locations._preprocess_text(text)
    assert processed == "Affiliation of Pittsburgh New York PA USA"


def test_get_entities():
    affiliation = (
        "<Affiliation>University of Pittsburgh, New York, PA, USA"
        "</Affiliation>"
    )
    ents = _guessing_locations._get_entities(affiliation)
    assert ents == [
        "Affiliation", "Pittsburgh", "Pittsburgh", "New York" "PA", "USA"
    ]


def test_get_location():
    tree = _reading_xml._get_tree(next(example_xml()))
    aff = _reading_xml._get_first_affiliation(tree)
    loc = _guessing_locations._get_location(aff)
    assert loc["city"] == "Pittsburgh"


def test_LocationGuesser():
    article_path = next(example_xml())
    location = _guessing_locations.LocationGuesser(article_path)
    location.get_location()
    assert location.location["city"] == "Pittsburgh"
    assert location.location["country"] == "United States"
    assert location.entities == [
        "Affiliation", "Pittsburgh", "Pittsburgh", "New York" "PA", "USA"
    ]
