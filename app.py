# app.py
import sqlite3
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
from wfmapi import update_database, print_item
app = Flask(__name__)
socketio = SocketIO(app)
@app.route('/')
def home():
    # update_database()
    conn = sqlite3.connect('mod_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Faction")
    factions = cursor.fetchall()

    cursor.execute(r"""
    SELECT 
        Mod.name, 
        ROUND(MAX(Price48hs,Price90d), 2) AS MaxAvgSold,
        ROUND(offerPrice, 2) AS offerPrice,
        ROUND(mostRepeatedOffer, 2) AS mostRepeatedOffer,
        GROUP_CONCAT(Faction.name, ', ') AS factionNames, 
        Mod.url_name, 
        amount48, 
        amount90,
        Faction.id as factionId,
        strftime('%Y-%m-%d %H:%M:%S', Mod.lastUpdated) AS lastUpdated

    FROM Mod 
    JOIN Mod_Faction ON Mod.id = Mod_Faction.mod_id 
    JOIN Faction ON Mod_Faction.faction_id = Faction.id 
    GROUP BY Mod.name 
    ORDER BY amount48 DESC
""")
    mods = cursor.fetchall()
    return render_template('index.html',factions=factions,mods=mods)


@app.route('/mods/<faction_id>/<orderType>')
def get_mods_by_faction(faction_id, orderType="demand"):
    
    faction_filter = "" if faction_id == "0" else "WHERE Mod_Faction.faction_id IN ({})".format(faction_id)
    
    queryString = f"""
    SELECT 
        Mod.name, 
        ROUND(MAX(Price48hs, Price90d), 2) AS MaxAvgSold,
        ROUND(offerPrice, 2) AS offerPrice,
        ROUND(mostRepeatedOffer, 2) AS mostRepeatedOffer,
        factionNames,
        Mod.url_name,
        amount48,
        amount90,
        Faction.id as factionId,
        strftime('%Y-%m-%d %H:%M:%S', Mod.lastUpdated) AS lastUpdated
    FROM Mod 
    JOIN 
        (SELECT 
            Mod_Faction.mod_id, 
            GROUP_CONCAT(Faction.name, ', ') as factionNames
        FROM 
            Mod_Faction 
        JOIN 
            Faction ON Mod_Faction.faction_id = Faction.id 
        GROUP BY 
            Mod_Faction.mod_id) AS factionsSubquery
        ON Mod.id = factionsSubquery.mod_id
    JOIN Mod_Faction ON Mod.id = Mod_Faction.mod_id 
    JOIN Faction ON Mod_Faction.faction_id = Faction.id 
    {faction_filter}
    GROUP BY Mod.name
    """
    
    if orderType == "price":
        queryString += " ORDER BY offerPrice DESC"
    else:
        queryString += " ORDER BY amount48 DESC"
    
    conn = sqlite3.connect('mod_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(queryString)
    
    mods = cursor.fetchall()
    mod_list = [dict(mod) for mod in mods]
    
    conn.close()
    
    return jsonify(mod_list)

# def updateMods(faction_id,orderType="demand"):
# @app.route('/updateMods')
# def updateMods():
#     try:
#         update_database()
#         return "ok"
#     except Exception as e:
#         return str(e), 500

@socketio.on('start_updateMods')
def handle_start_task():
    try:
        update_database()
        return "ok"
    except Exception as e:
        print("error: ",e)
        emit('error', e.with_traceback())
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
    
