import argparse
from collections import Counter
from datetime import datetime
from typing import List
import sqlite3
import pywmapi as wm
from pywmapi.common import *
from pywmapi.auth import *
from pywmapi.statistics.models import *
from models.ModDTO import ModDTO
from wfmapi import update_mod_prices,print_item

def main(item_url_name):
    mod = ModDTO(0,url_name=item_url_name)
    update_mod_prices(mod)
    print_item(mod)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and display Warframe market statistics.")
    parser.add_argument("item_url_name", type=str, help="The URL name of the item to fetch statistics for.")
    args = parser.parse_args()
    
    main(args.item_url_name)
