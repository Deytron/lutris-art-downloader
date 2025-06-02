# Import necessary modules
import requests
import sqlite3
import os
import inquirer
import base64

# Variables
user = ''
db_path = ''
auth = ''


def main():
    """Main function to run the Lutris Cover Art Downloader."""

    global user, db_path, auth
    print(f"Welcome {user} to Lutris Cover Art Downloader!\n")
    user = get_user()
    db_path = f'/home/{user}/.local/share/lutris/pga.db'
    auth = get_api_key()
    print("Getting API Key...\n")

    if auth == '':
        set_api_key()
    co = db_connect()
    
    # Handle multiple cover types
    for dim, cov_path in get_cover_type(user):
        print(f"Processing {dim} covers...")
        get_games_list(co, cov_path, dim)


# Functions


def get_user():
    """Get the current user's login name."""

    try:
        return os.getlogin()
    except Exception:
        print("Could not get session username")
        exit(1)


def get_cover_type(user):
    """Get the cover type preference from user and return corresponding paths."""

    cover_types = list()
    questions = [
        inquirer.List(
            'type',
            message="Would you like to download Steam banners or Steam vertical covers?",
            choices=['Banner (460x215)', 'Vertical (600x900)', 'Both'],
        ),
    ]
    ans = inquirer.prompt(questions)["type"]
    print(f'Cover type set to {ans}\n')
    
    if ans in ('Banner (460x215)', 'Both'):
        cov_path = f'/home/{user}/.cache/lutris/banners/'
        dim = '460x215'
        cover_types.append((dim, cov_path))

    if ans in ('Vertical (600x900)', 'Both'):
        cov_path = f'/home/{user}/.cache/lutris/coverart/'
        dim = '600x900'
        cover_types.append((dim, cov_path))

    return cover_types


def save_api_key(key):
    """Save the API key to a file."""

    with open('./apikey.txt', 'w') as f:
        f.write(key)


def get_api_key():
    """Get the API key from file if it exists."""

    if os.path.isfile('./apikey.txt'):
        with open('./apikey.txt', 'r') as f:
            key = f.read()
            auth_header = {'Authorization': f'Bearer {key}'}
            return auth_header
    else:
        return ''


def set_api_key():
    """Prompt user for API key and save it."""

    print("Could not find API key")
    print('You need a SteamGriDB API key to use this script.')
    print('You can get one by using your Steam account and heading here: '
          'https://www.steamgriddb.com/profile/preferences/api\n')
    api = input("Enter your SteamGridDB API key: ")
    auth_header = {'Authorization': f'Bearer {api}'}
    test_api(auth_header, api)


def test_api(key, api):
    """Test if the provided API key is valid."""

    url = 'https://www.steamgriddb.com/api/v2/grids/game/1?dimensions=600x900'
    r = requests.get(url, headers=key)

    if r.status_code == 200:
        print("API key is valid, saving...")
        save_api_key(api)
    else:
        print("API key is invalid")
        exit(1)


def db_connect():
    """Connect to the Lutris database."""

    try:
        conn = sqlite3.connect(db_path)
    except Exception:
        print("Could not find Lutris database 'pga.db'. "
              "You can manually edit script's path if necessary")
        exit(1)
    return conn


def search_game(game):
    """Search for a game by name via Lutris database, then get the grid data."""

    url = f'https://www.steamgriddb.com/api/v2/search/autocomplete/{game}'
    res = requests.get(url, headers=auth).json()

    if len(res["data"]) == 0:
        print(f"Could not find a cover for game {game}")
    else:
        print(f"Found game {game.replace('-', ' ').title()}")
        game_id = res["data"][0]["id"]
        return game_id


def download_cover(name, cov_path, dim):
    """Download cover by searching for the game via its name, then via its SteamGridDB's ID."""

    game_id = search_game(name)
    print(f"Downloading cover for {name.replace('-', ' ').title()}")
    url = f'https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions={dim}'
    grids = requests.get(url, headers=auth).json()

    try:
        image_url = grids["data"][0]["url"]
    except Exception:
        print(f"Could not find a cover for game {name}")
        return
    
    # Create the directory if it doesn't exist
    os.makedirs(cov_path, exist_ok=True)
    
    r = requests.get(image_url)
    
    with open(f'{cov_path}{name}.jpg', 'wb') as f:
        f.write(r.content)


def get_games_list(co, cov_path, dim):
    """Get all games and for each game, check if it already has a cover."""
    
    c = co.execute('SELECT slug FROM games')
    games = c.fetchall()

    for entry in games:
        title = entry[0]

        if not os.path.isfile(f'{cov_path}{title}.jpg'):
            # If not, download it
            download_cover(title, cov_path, dim)
        else:
            print(f"Cover for {title.replace('-', ' ').title()} already exists")

    print('All done! Restart Lutris for the changes to take effect')


if __name__ == '__main__':
    main()
