from bs4 import BeautifulSoup
import requests as req
import re

import time


# TO-DO
# Fix up containment class, use regex?

PRESET="https://scp-wiki.wikidot.com/scp-"

def pad_number(num: int) -> str:
    pad_length = 0

    if num < 10:
        pad_length = 2
    elif num < 100:
        pad_length = 1

    parts = ["0" for _ in range(pad_length)]
    parts.append(str(num))
    res = "".join(parts)

    return res

class SCP_item:
    def __init__(self, number: int, containment_class: str):
        self.number = number
        self.containment_class = containment_class
        self.connections: dict[int, int] = {}
        self.tags = []



def get_SCP_items(lower_bound: int, upper_bound: int) -> dict[int, SCP_item]:
    SCPs = {}

    # Aux memory for connections between SCPs mentioned in the same entry
    SCP_neighbours = {}

    for scp in range(lower_bound, upper_bound+1):
        candidate = process_scp(scp, SCP_neighbours)
        if candidate is None:
            print(f"SCP #{scp} is invalid / does not exist")
            continue

        print(f"SCP #{scp} processed - {scp}/{upper_bound}")
        SCPs[scp] = candidate

    return SCPs

def get_containment_class(soup: BeautifulSoup) -> str | None:
    if len(soup.find_all("strong")) < 2:
        return None

    containment_element = soup.find_all("strong")[1].parent.text
    return containment_element.split()[-1]


def get_neighbouring_scps(soup: BeautifulSoup):
    div = soup.find( "div", {"id" : "page-content"})

    res = div.find_all("a", href=re.compile("^/scp-"))

    for neigh in res.copy():
        if len(neigh.find_parents("div", {"class": "footer-wikiwalk-nav"})) > 0:
          res.remove(neigh)

        if len(neigh.find_parents("table", {"class": "wiki-content-table"})) > 0:
          res.remove(neigh)

    return res

def clean_neighbours(scp: int, neighbours: list[BeautifulSoup]) -> set[int]:
    res = {}

    for neigh in neighbours:
        code = int(neigh['href'].split("-")[1])

        if code != scp:
            res[code] = res.get(code, 0) + 1
    return res

def get_other_connections(scp: int, neighbours: set[BeautifulSoup], aux: dict[int, dict[int, int]]) -> None:

    parent_paragraphs = {}

    for neigh in neighbours:
        parent = neigh.parent

        if parent not in parent_paragraphs:
            parent_paragraphs[parent] = set()

        parent_paragraphs[parent].add(neigh['href'].split("-")[1])

    for items in parent_paragraphs.values():
        itemsa = list(items)
        for i, item in enumerate(itemsa):
            for j in range(len(itemsa)):
                other = itemsa[j]

                if i == j:
                    continue

                if item not in aux:
                    aux[item] = {}

                aux[item][other] = aux[item].get(other, 0) + 1


def process_scp(scp: int, aux: dict[int, set[int]]) -> SCP_item  | None:
    link = "".join((PRESET, pad_number(scp)))
    req_result = req.get("".join(link))

    if req_result.status_code != 200:
        return None
    
    soup = BeautifulSoup(req_result.content, "html.parser")
    
    neighbours_links = get_neighbouring_scps(soup)

    containment_class = get_containment_class(soup)
    neighbours = clean_neighbours(scp, neighbours_links)

    scp_object = SCP_item(scp, containment_class)
    scp_object.connections = neighbours

    get_other_connections(scp, neighbours_links, aux)
    
    return scp_object

get_SCP_items(2, 200)