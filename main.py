# Import necessary modules
import requests, sqlite3, os, inquirer, base64

# Vars
user = ''
dbpath = ''
auth = ''

# Main function
def main():
    global user, dbpath, auth
    print("Welcome " + user + " to Lutris Cover Art Downloader!\n")
    user = GetUser()
    dbpath = '/home/' + user + '/.local/share/lutris/pga.db'
    auth = GetAPIKey()
    print("Getting API Key...\n")

    if auth == '':
        SetAPIKey()

    co = DBConnect()
    
    # Handle multiple cover types
    for dim, covpath in GetCoverType(user):
        print(f"Processing {dim} covers...")
        GetGamesList(co, covpath, dim)


####### FUNCTIONS


def GetUser():
    try:
        return os.getlogin()
    except:
        print("Could not get session username")
        exit(1)

def GetCoverType(user):
    cover_types = list()
    questions = [
        inquirer.List(
            'type',
            message="Would you like to download Steam banners or Steam vertical covers?",
            choices=['Banner (460x215)', 'Vertical (600x900)', 'Both'],
        ),
    ]
    ans = inquirer.prompt(questions)["type"]
    print('Cover type set to ' + ans + '\n')
    
    if ans in ('Banner (460x215)', 'Both'):
        covpath = '/home/' + user + '/.cache/lutris/banners/'
        dim = '460x215'
        cover_types.append((dim, covpath))

    if ans in ('Vertical (600x900)', 'Both'):
        covpath = '/home/' + user + '/.cache/lutris/coverart/'
        dim = '600x900'
        cover_types.append((dim, covpath))

    return cover_types

def SaveAPIKey(key):
    with open('./apikey.txt', 'w') as f:
        f.write(key)

def GetAPIKey():
    if os.path.isfile('./apikey.txt'):
        with open('./apikey.txt', 'r') as f:
            key = f.read()
            auth = {'Authorization': 'Bearer ' + key}
            return auth
    else:
        return ''

def SetAPIKey():
    print("Could not find API key")
    print('You need a SteamGriDB API key to use this script.')
    print('You can get one by using your Steam account and heading here: https://www.steamgriddb.com/profile/preferences/api\n')
    api = input("Enter your SteamGridDB API key: ")
    auth = {'Authorization': 'Bearer ' + api}
    TestAPI(auth, api)

def TestAPI(key, api):
    r = requests.get('https://www.steamgriddb.com/api/v2/grids/game/1?dimensions=600x900', headers=key)

    if r.status_code == 200:
        print("API key is valid, saving...")
        SaveAPIKey(api)
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

# Search for a game by name via Lutris database, then get the grid data
def SearchGame(game):
    res = requests.get('https://www.steamgriddb.com/api/v2/search/autocomplete/' + game, headers=auth).json()

    if len(res["data"]) == 0:
        print("Could not find a cover for game " + game)
    else:
        print("Found game " + game.replace('-', ' ').title())
        id = res["data"][0]["id"]
        return id

# Download cover by searching for the game via its name, then via its SteamGriDB's ID
def DownloadCover(name, covpath, dim):
    gameid = SearchGame(name)
    print("Downloading cover for " + name.replace('-', ' ').title())
    grids = requests.get('https://www.steamgriddb.com/api/v2/grids/game/' + str(gameid) + '?dimensions=' + dim, headers=auth).json()

    try:
        url = grids["data"][0]["url"]
    except:
        print("Could not find a cover for game " + name)
        return

    r = requests.get(url)

    with open(covpath + name + '.jpg', 'wb') as f:
        f.write(r.content)

# Get all games and for each game, check if it already has a cover
def GetGamesList(co, covpath, dim):
    c = co.execute('SELECT slug FROM games')
    games = c.fetchall()

    for entry in games:
        title = entry[0]

        if not os.path.isfile(covpath + title + '.jpg'):
            # If not, download it
            DownloadCover(title, covpath, dim)
        else:
            print("Cover for " + title.replace('-', ' ').title() + " already exists")

    print('All done ! Restart Lutris for the changes to take effect')

if __name__ == '__main__':
    main()
