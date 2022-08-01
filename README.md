# Lutris Cover Art Downloader

This is an **EXTREMELY DIRTY** script to download cover art for Lutris games. It first started as a personal project, but I'm putting it here in case anyone else wants to use it.

It comes from a long time bug in Lutris. The source used to get cover arts is... unreliable. It's not a big deal, but it's annoying. So I wrote this script to download the cover arts from SteamGridDB.

## Usage

1. Clone the repository

2. Install the dependencies

```bash
pip install -r requirements.txt
```

3. Run the script

```bash
python3 main.py
```

> You need a SteamGridDB API key. You can get one [here](https://www.steamgriddb.com/profile/settings/api).

## Screenshots

Your library will go from this:

![No covers](https://i.imgur.com/GcyWlHA.png)

To this:

![Covers downloaded](https://i.imgur.com/SWYWqoy.png)

In a matter of seconds.

## How it works and warnings

When I said the script dirty, it **IS** dirty. Obvisouly this won't get you any malware, but since I'm not that much into Python, I did what I could.
What the script does is that it fetches the list of games from Lutris at `/home/$USER/.cache/lutris`, then it fetches the first cover art from SteamGridDB. It then saves the cover art in the Lutris cache folder.

## Planned features

- ❕ Argument support (--banner, --cover, --help)
- ❕ Add a simple GUI with console output
- ❕ Add a way to select the cover art you want via the GUI
- Split in multiple files
- Better code
- Encode API Key in file
- A better README?

## Credits

- Big thanks to the Lutris team!
- Big thanks to SteamGridDB for their API and their resources!
- Obvious thanks to StackOverflow!