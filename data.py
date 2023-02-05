import json
import pickle

DATAPATH = "gamedata.dat"
SETTINGSPATH = "settings.json"

def get_playerdata():
    try:
        with open(DATAPATH, "rb") as f:
            return pickle.load(f)
    except:
        print("Fejl: Kunne ikke finde gemt data for highscore.")
        return {"high":0}

def update_playerdata(newPlayerdata):
    with open("gamedata.dat", "wb") as f:
        pickle.dump(newPlayerdata, f, protocol=2)

def get_settings():
    with open(SETTINGSPATH, "r") as f: return json.load(f)

def update_settings(newSettings):
    with open(SETTINGSPATH, "w") as f:
        json.dump(newSettings, f, indent=2)
