from bs4 import BeautifulSoup
import requests as req

PRESET="https://scp-wiki.wikidot.com/scp"

class SCP_item:
    def __init__(self, number: int, object_class: str):
        self.number = number
        self.object_class = object_class
        self.connections: list[int | 'SCP_item'] = []

    def get_connections(self) -> None:
        pass



def get_SCP_items(lower_bound: int, upper_bound: int) -> dict[int, SCP_item]:
    SCPs = {}

    for scp in range(lower_bound, upper_bound+1):
        candidate = process_scp(scp)
        if candidate is None:
            print(f"SCP #{scp} is invalid / does not exist")
            continue

        print(f"SCP #{scp} processed - {scp}/{upper_bound}")
        SCPs[scp] = candidate

    return SCPs

def process_scp(scp: int) -> SCP_item:
    pass
