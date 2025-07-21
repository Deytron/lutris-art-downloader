# Lutris Cover Art Downloader
Downloads Cover art,banners and icons for games in lutris

## Usage

1. Clone the repository
2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Run the script

```bash
python3 main.py
```

> You need a SteamGridDB API key. You can get one [here](https://www.steamgriddb.com/profile/preferences/api).

## Screenshots

Your library will go from this:

![No covers](https://i.imgur.com/GcyWlHA.png)

To this:

![Covers downloaded](https://i.imgur.com/SWYWqoy.png)

In a matter of seconds.

## How it works and warnings

What the script does is that it fetches the list of games from Lutris at `/home/$USER/.cache/lutris`, then it fetches the first cover art from SteamGridDB. It then saves the cover art in the Lutris cache folder.

## Credits

- Big thanks to the Lutris team!
- Big thanks to SteamGridDB for their API and their resources!
- Obvious thanks to StackOverflow!