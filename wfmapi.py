from collections import Counter
from datetime import datetime
from typing import List
import sqlite3
from flask_socketio import emit
import pywmapi as wm
from pywmapi.common import Platform, OrderType
from pywmapi.auth import UserShort
from pywmapi.statistics.models import StatisticClosed
from models.ModDTO import ModDTO

def calculate_average_avg_price(statistics: List[StatisticClosed]) -> float:
    total_avg_price = sum(stat.avg_price for stat in statistics)
    return total_avg_price / max(len(statistics), 1)

def most_repeated_number(numbers):
    counts = Counter(numbers)
    try:
        most_common_number, count = counts.most_common(1)[0]
    except IndexError:
        most_common_number, count = None, None
    return most_common_number

def print_item(mod: ModDTO):
    print("Name: ", mod.name.upper())
    print(f"{'48hs avg:':<20} {round(mod.avg_48h, 2):<10} {'pl':<10}")
    print(f"{'48hs amount:':<20} {mod.amount_48:<10} {'units':<10}")
    print(f"{'90days avg:':<20} {round(mod.avg_90d, 2):<10} {'pl':<10}")
    print(f"{'90days amount:':<20} {mod.amount_90:<10} {'units':<10}")
    print(f"{'avgOffer:':<20} {round(mod.avg_offer, 2):<10} {'pl':<10}")
    print(f"{'mostRepeatedOffer:':<20} {round(mod.most_repeated_offer, 2):<10} {'pl':<10}")
    print('-' * 40)

def update_mod_prices(mod: ModDTO):
    offers = wm.orders.get_orders(mod.url_name, Platform.pc)
    offers_online = [offer for offer in offers if offer.order_type == OrderType.sell and (offer.user.status == UserShort.Status.online or offer.user.status == UserShort.Status.ingame)]
    offers_online = sorted(offers_online, key=lambda x: x.platinum)[:20]

    mod.avg_offer = sum(offer.platinum for offer in offers_online) / max(len(offers_online), 1)
    mod.most_repeated_offer = most_repeated_number([offer.platinum for offer in offers_online])

    stats = wm.statistics.get_statistic(mod.url_name)
    mod.avg_48h = calculate_average_avg_price(stats.closed_48h)
    mod.amount_48 = len(stats.closed_48h)
    mod.avg_90d = calculate_average_avg_price(stats.closed_90d)
    mod.amount_90 = len(stats.closed_90d)

def update_database():
    conn = sqlite3.connect('mod_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, url_name FROM Mod")
    mod_tuples = cursor.fetchall()

    mods = [ModDTO(id, url_name) for id, url_name in mod_tuples]
    index=1
    for mod in mods:
        update_mod_prices(mod)
        print(f"Progress: {index}/{len(mods)}")
        print_item(mod)
        progress={'index': index, 'total': len(mods), 'percent': round(index / len(mods) * 100,2)}
        index+=1
        emit('task_progress', progress)
        cursor.execute(
            "UPDATE Mod SET Price48hs = ?, Price90d = ?, offerPrice = ?, mostRepeatedOffer = ?, amount48 = ?, amount90 = ?, lastUpdated = ? WHERE id = ?", 
            (mod.avg_48h, mod.avg_90d, mod.avg_offer, mod.most_repeated_offer, mod.amount_48, mod.amount_90, datetime.now(), mod.id)
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database()
