import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('mod_database.db')
cursor = conn.cursor()


#alter table
# cursor.execute("ALTER TABLE Mod ADD COLUMN amount48 INTEGER;")
# cursor.execute("ALTER TABLE Mod ADD COLUMN amount48 INTEGER;")

# Retrieve mods sorted by price in descending order
cursor.execute("""
    SELECT Mod.name, MAX(Price48hs, Price90d) AS MaxAvgSold,offerPrice,mostRepeatedOffer, GROUP_CONCAT(Faction.name), Mod.url_name, amount48, amount90 
    FROM Mod 
    JOIN Mod_Faction ON Mod.id = Mod_Faction.mod_id 
    JOIN Faction ON Mod_Faction.faction_id = Faction.id 
    GROUP BY Mod.name 
    ORDER BY amount48 DESC
""")

mods = cursor.fetchall()

# Define the file path
output_file = 'mods_by_demand.txt'

# Write mods information to the text file
with open(output_file, 'w') as file:
    for mod in mods:
        name, MaxAvgSold,offerPrice,mostRepeatedOffer, factions, url_name, amount48, amount90 = mod
        url = f"https://warframe.market/items/{url_name}"
        file.write(f"{'Name:':<25} {name}\n")
        file.write(f"{'Max Average Sold:':<25} {MaxAvgSold.__round__(2)} pl\n")
        file.write(f"{'Online Avg Offer Price:':<25} {offerPrice.__round__(2)} pl\n")
        file.write(f"{'Most Repeated Price:':<25} {mostRepeatedOffer} pl\n")
        file.write(f"{'Amount Sold 48Hs:':<25} {amount48} units\n")
        file.write(f"{'Amount Sold 90days:':<25} {amount90} units\n")
        file.write(f"{'Factions:':<25} {factions}\n")
        file.write(f"{'URL:':<25} {url}\n\n")

# Close connection
conn.close()

print(f"Mods information has been written to {output_file}")
