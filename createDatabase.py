import sqlite3
import csv
import re

# Function to format the string
def format_string(input_string):
    # Convert uppercase letters to lowercase
    lowercase_string = input_string.lower()
    # Replace spaces with underscores
    formatted_string = re.sub(r'\s+', '_', lowercase_string)
    formatted_string=formatted_string.replace("'", "")
    return formatted_string

# Create a SQLite database connection
conn = sqlite3.connect('mod_database.db')
cursor = conn.cursor()

# Create the Mod table
cursor.execute('''CREATE TABLE IF NOT EXISTS Mod (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    url_name TEXT UNIQUE,
                    Price48hs REAL,
                    Price90d REAL
                )''')

# Create the Faction table
cursor.execute('''CREATE TABLE IF NOT EXISTS Faction (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )''')

# Create the Mod_Faction relationship table
cursor.execute('''CREATE TABLE IF NOT EXISTS Mod_Faction (
                    mod_id INTEGER,
                    faction_id INTEGER,
                    PRIMARY KEY (mod_id, faction_id),
                    FOREIGN KEY (mod_id) REFERENCES Mod(id),
                    FOREIGN KEY (faction_id) REFERENCES Faction(id)
                )''')

# Read data from CSV file and insert into Mod and Faction tables
with open('./data/mod_prices.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    for row in reader:
        mod_name, faction_name, price48hs, price90d = row
        formatted_name = format_string(mod_name)
        cursor.execute('''INSERT OR IGNORE INTO Mod (name, url_name) VALUES (?, ?)''', (mod_name, formatted_name))
        cursor.execute('''INSERT OR IGNORE INTO Faction (name) VALUES (?)''', (faction_name,))
        cursor.execute('''SELECT id FROM Mod WHERE name = ?''', (mod_name,))
        mod_id = cursor.fetchone()[0]
        cursor.execute('''SELECT id FROM Faction WHERE name = ?''', (faction_name,))
        faction_id = cursor.fetchone()[0]
        cursor.execute('''INSERT OR IGNORE INTO Mod_Faction (mod_id, faction_id) VALUES (?, ?)''', (mod_id, faction_id))

#FIX FACTION ID
# cursor.execute("UPDATE Mod_Faction SET mod_id =194 WHERE mod_id = 20")
# cursor.execute("DELETE FROM Mod WHERE id = 20")

# Commit changes and close connection
conn.commit()
conn.close()
