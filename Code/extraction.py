from bs4 import BeautifulSoup
import requests as req
import re

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

    print(res)
    return res

class SCP_item:
    def __init__(self, number: int, containment_class: str):
        self.number = number
        self.containment_class = containment_class
        self.connections: dict[int, int] = []
        self.tags = []



def get_SCP_items(lower_bound: int, upper_bound: int) -> dict[int, SCP_item]:
    SCPs = {}

    # Aux memory for connections between SCPs mentioned in the same entry
    SCP_neighbours = {}

    for scp in range(lower_bound, upper_bound+1):
        candidate = process_scp(scp)
        if candidate is None:
            print(f"SCP #{scp} is invalid / does not exist")
            continue

        print(f"SCP #{scp} processed - {scp}/{upper_bound}")
        SCPs[scp] = candidate

    return SCPs

def get_containment_class(soup: BeautifulSoup) -> str:
    containment_element = soup.find_all("strong")[1].parent.text
    return containment_element.split()[-1]


def get_neighbouring_scps(soup: BeautifulSoup):
    div = soup.find( "div", {"id" : "page-content"})

    return div.find_all("a", href=re.compile("^/scp-"))

def clean_neighbours(scp: int, neighbours: list[BeautifulSoup]) -> set[int]:
    res = {}

    for neigh in neighbours:
        code = int(neigh.text.split("-")[1])

        if code != scp:
            res[code] = res.get(code, 0) + 1
    return res

def get_other_connections(scp: int, neighbours: list[BeautifulSoup], aux: dict[int, dict[int, int]]) -> None:

    parent_paragraphs = {}

    for neigh in neighbours:
        parent = neigh.parent

        if parent not in parent_paragraphs:
            parent_paragraphs[parent] = set()

        parent_paragraphs[parent].add(neigh.text.split("-")[1])

    for items in parent_paragraphs.values():
        itemsa = list(items)
        for i, item in enumerate(itemsa):
            for j in range(i+1, len(itemsa)):
                other = itemsa[j]

                if other in aux and item in aux[other]:
                    aux[other][item] += 1

                elif item in aux and other in aux[item]:
                    aux[item][other] += 1
                else:

                    if item not in aux:
                        aux[item] = {}

                    aux[item][other] = 1

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
    
    return None