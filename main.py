# Import necessary modules
import requests, sqlite3, os, inquirer, base64

# Vars
user = ''
dbpath = ''
dims = []
auth = ''
covpaths = {}
iconpath = ''

def main():
    global user, dbpath, dims, auth
    print("Welcome to Lutris Cover Art & Icon Downloader!\n")
    user = GetUser()
    dbpath = f'/home/{user}/.local/share/lutris/pga.db'
    dims = GetCoverType()
    auth = GetAPIKey()
    print("Getting API Key...\n")
    if auth == '':
        SetAPIKey()
    PrepareDirectories()
    co = DBConnect()
    GetGamesList(co)

####### FUNCTIONS

def GetUser():
    try:
        return os.getlogin()
    except:
        print("Could not get session username")
        exit(1)

def GetCoverType():
    global covpaths, iconpath
    questions = [
        inquirer.List('type',
            message="Which artwork would you like to download?",
            choices=['Banner (920x430)', 'Vertical (600x900)', 'Both'],
        ),
    ]
    ans = inquirer.prompt(questions)["type"]
    print('Cover type set to ' + ans + '\n')
    userhome = f'/home/{user}'
    covpaths = {
        'banner': f'{userhome}/.cache/lutris/banners/',
        'vertical': f'{userhome}/.cache/lutris/coverart/'
    }
    iconpath = f'{userhome}/.cache/lutris/icons/'

    if ans == 'Banner (920x430)':
        return [('banner', '920x430')]
    elif ans == 'Vertical (600x900)':
        return [('vertical', '600x900')]
    else:
        return [
            ('banner', '920x430'),
            ('vertical', '600x900')
        ]

def PrepareDirectories():
    for p in covpaths.values():
        os.makedirs(p, exist_ok=True)
    os.makedirs(iconpath, exist_ok=True)

def SaveAPIKey(key):
    with open('./apikey.txt', 'w') as f:
        f.write(key)

def GetAPIKey():
    if os.path.isfile('./apikey.txt'):
        with open('./apikey.txt', 'r') as f:
            key = f.read().strip()
            return {'Authorization': 'Bearer ' + key}
    else:
        return ''

def SetAPIKey():
    global auth
    print("Could not find API key")
    print('You need a SteamGridDB API key to use this script.')
    print('You can get one by using your Steam account and heading here: https://www.steamgriddb.com/profile/preferences/api\n')
    api = input("Enter your SteamGridDB API key: ")
    auth = {'Authorization': 'Bearer ' + api.strip()}
    TestAPI(auth, api)

def TestAPI(key, api):
    r = requests.get('https://www.steamgriddb.com/api/v2/grids/game/1?dimensions=600x900', headers=key)
    if r.status_code == 200:
        print("API key is valid, saving...\n")
        SaveAPIKey(api.strip())
    else:
        print("API key is invalid")
        exit(1)

def DBConnect():
    try:
        conn = sqlite3.connect(dbpath)
    except:
        print("Could not find Lutris database 'pga.db'. You can manually edit script's path if necessary")
        exit(1)
    return conn

def SearchGame(game):
    res = requests.get('https://www.steamgriddb.com/api/v2/search/autocomplete/' + game, headers=auth).json()
    if len(res["data"]) == 0:
        print(f"[!] Could not find SGDB entry for '{game}'")
        return None
    else:
        print(f"[+] Found SGDB entry for: {game.replace('-', ' ').title()}")
        return res["data"][0]["id"]

def DownloadCover(name, dimension, subpath):
    gameid = SearchGame(name)
    if gameid is None:
        return
    print(f"[*] Downloading {dimension} cover for {name.replace('-', ' ').title()}")
    grids = requests.get(
        f'https://www.steamgriddb.com/api/v2/grids/game/{gameid}?dimensions={dimension}', headers=auth).json()
    url = None
    try:
        url = grids["data"][0]["url"]
    except (KeyError, IndexError):
        if dimension == '920x430':
            grids = requests.get(
                f'https://www.steamgriddb.com/api/v2/grids/game/{gameid}?dimensions=460x215', headers=auth).json()
            try:
                url = grids["data"][0]["url"]
            except (KeyError, IndexError):
                print(f"[!] No cover found for {name} at 920x430 or 460x215")
                return
        else:
            print(f"[!] No cover found for {name}")
            return

    filename = os.path.join(covpaths[subpath], name + '.jpg')
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

def DownloadIcon(name):
    gameid = SearchGame(name)
    if gameid is None:
        return
    print(f"[*] Downloading icon for {name.replace('-', ' ').title()}")
    icons = requests.get(f'https://www.steamgriddb.com/api/v2/icons/game/{gameid}', headers=auth).json()
    try:
        url = icons["data"][0]["url"]
    except (KeyError, IndexError):
        print(f"[!] No icon found for {name}")
        return
    r = requests.get(url)
    with open(os.path.join(iconpath, name + '.png'), 'wb') as f:
        f.write(r.content)

def GetGamesList(co):
    c = co.execute('SELECT slug FROM games')
    games = c.fetchall()
    for entry in games:
        title = entry[0]
        for subpath, dim in dims:
            cover_file = os.path.join(covpaths[subpath], title + '.jpg')
            if not os.path.isfile(cover_file):
                DownloadCover(title, dim, subpath)
            else:
                print(f"[✓] {dim} Cover for {title} already exists")
        icon_file = os.path.join(iconpath, title + '.png')
        if not os.path.isfile(icon_file):
            DownloadIcon(title)
        else:
            print(f"[✓] Icon for {title} already exists")

    print('\nAll done! Restart Lutris for the changes to take effect.')

if __name__ == '__main__':
    main()
