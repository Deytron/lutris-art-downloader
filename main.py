# Import necessary modules
import requests
import sqlite3
import os
import inquirer

# Vars
user = ''
dbpath = ''
dim = ''
auth = ''
covpath = ''

# Main function
def main():
    global user, dbpath, dim, auth
    print(f"Welcome {user} to Lutris Cover Art Downloader!\n")
    user = GetUser()
    dbpath = f'/home/{user}/.local/share/lutris/pga.db'
    dim = GetCoverType()
    auth = GetAPIKey()
    print("Getting API Key...\n")
    if auth == '':
        SetAPIKey()
    co = DBConnect()
    GetGamesList(co)


####### FUNCTIONS


def GetUser():
    try:
        return os.getlogin()
    except OSError:
        print("Could not get session username")
        exit(1)

def GetCoverType():
    global covpath, dim
    questions = [
        inquirer.List('type',
                      message="Would you like to download Steam banners or Steam vertical covers?",
                      choices=['Banner (460x215)', 'Vertical (600x900)'],
                      ),
    ]
    ans = inquirer.prompt(questions)["type"]
    print(f'Cover type set to {ans}\n')
    if ans == 'Banner (460x215)':
        covpath = f'/home/{user}/.local/share/lutris/banners/'
        dim = '460x215'
    else:
        covpath = f'/home/{user}/.cache/lutris/coverart/'
        dim = '600x900'
    return dim

def SaveAPIKey(key):
    with open('./apikey.txt', 'w') as f:
        f.write(key)

def GetAPIKey():
    if os.path.isfile('./apikey.txt'):
        with open('./apikey.txt', 'r') as f:
            key = f.read()
            return {'Authorization': f'Bearer {key}'}
    return ''

def SetAPIKey():
    global auth
    print("Could not find API key")
    print('You need a SteamGriDB API key to use this script.')
    print('You can get one by using your Steam account and heading here: https://www.steamgriddb.com/profile/preferences/api\n')
    api = input("Enter your SteamGridDB API key: ")
    auth = {'Authorization': f'Bearer {api}'}
    TestAPI(auth, api)

def TestAPI(auth, api):
    r = requests.get('https://www.steamgriddb.com/api/v2/grids/game/1?dimensions=600x900', headers=auth)
    if r.status_code == 200:
        print("API key is valid, saving...")
        SaveAPIKey(api)
    else:
        print("API key is invalid")
        exit(1)

def DBConnect():
    try:
        conn = sqlite3.connect(dbpath)
    except sqlite3.Error:
        print("Could not find Lutris database 'pga.db'. You can manually edit script's path if necessary")
        exit(1)
    return conn

# Search for a game by name via Lutris database, then get the grid data
def SearchGame(game):
    res = requests.get(f'https://www.steamgriddb.com/api/v2/search/autocomplete/{game}', headers=auth).json()
    if len(res["data"]) == 0:
        print(f"Could not find a cover for game {game}")
    else:
        print(f"Found game {game.replace('-', ' ').title()}")
        return res["data"][0]["id"]

# Download cover by searching for the game via its name, then via its SteamGriDB's ID
def DownloadCover(name):
    gameid = SearchGame(name)
    if gameid:
        print(f"Downloading cover for {name.replace('-', ' ').title()}")
        grids = requests.get(f'https://www.steamgriddb.com/api/v2/grids/game/{gameid}?dimensions={dim}', headers=auth).json()
        try:
            url = grids["data"][0]["url"]
        except (KeyError, IndexError):
            print(f"Could not find a cover for game {name}")
            return
        r = requests.get(url)
        with open(f'{covpath}{name}.jpg', 'wb') as f:
            f.write(r.content)

# Get all games and for each game, check if it already has a cover
def GetGamesList(co):
    c = co.execute('SELECT slug FROM games')
    games = c.fetchall()
    for entry in games:
        title = entry[0]
        if not os.path.isfile(f'{covpath}{title}.jpg'):
            # If not, download it
            DownloadCover(title)
        else:
            print(f"Cover for {title.replace('-', ' ').title()} already exists")
    print('All done! Restart Lutris for the changes to take effect')


if __name__ == '__main__':
    main()
