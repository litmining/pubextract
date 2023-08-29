from pathlib import Path

from pubextract.author_locations import _pubget


articles_dir = (
    Path(__file__).resolve().parents[5]
    / "data"
    / "pubget_data"
    / "review-neuro-meta-analyses_2023-06-29"
    / "query_a84b639ed7c2cc2d04c773db7c22905d"
    / "articles"
)

_pubget._extract_from_articles_dir(articles_dir)