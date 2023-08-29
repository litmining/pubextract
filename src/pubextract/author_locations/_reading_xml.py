from pathlib import Path
import re
from typing import List, Optional, Union, Tuple, Any, NewType
import dataclasses

from unidecode import unidecode
from lxml import etree
import pandas as pd
import en_core_web_sm


def _get_tree(article_path):
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.parse(article_path, parser)


def _get_id(article_path):
    tree = _get_tree(article_path)
    try:
        pmcid = tree.find("front/article-meta/article-id[@pub-id-type='pmc']").text
        id = "PMC%s" % pmcid
    except:
        pmid = tree.xpath("//PMID/text()")[0]
        id = "Pubmed%s" % pmid
    return id


def _get_first_affiliation(article_path):
    aff = ""
    for event, element in etree.iterparse(article_path):
        if element.tag == "aff" or element.tag == "Affiliation":
            aff = etree.tostring(element, with_tail=False, encoding="unicode")
            if aff:
                break
    return aff
