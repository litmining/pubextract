from lxml import etree


def _get_tree(article_path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(article_path, parser)
    return tree


def _get_id(tree):
    try:
        pmcid = (
            tree.find("front/article-meta/article-id[@pub-id-type='pmc']").text
        )
        id_ = f"PMC{pmcid}"
    except Exception:  # make error more specific
        pmid = tree.xpath("//PMID/text()")[0]
        id_ = f"Pubmed{pmid}"
    return id_


def _get_first_affiliation(tree):
    affiliation = ""
    element = tree.find("//aff")
    if element == -1:
        element = tree.find("//Affiliation")
    if element is not None:
        affiliation = etree.tostring(
            element, with_tail=False, encoding="unicode"
            )
    else:
        affiliation = ""
    return affiliation
