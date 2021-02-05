# dayone2notion

Import content from Day One into Notion.

## Requirements

This script uses several helper libraries.  Install using `pip`:

```
python3 -m pip install -r requirements.txt
```

Advanced users may want to use `venv` to manage these dependencies.

## Usage

First, you'll need to export the content from Day One:

1. Export a journal from Day One in JSON format.
2. Unzip the archive.

Now, run the script, supplying your user token and top-level archive page:

```
dayone2notion.py --token TOKEN_V2 --page URL <json_file>
```

It's possible to import multiple files at the same time.

```
dayone2notion.py --token TOKEN_V2 --page URL <json_file1> <json_file2> ...
```

Additionally, the `--raw` parameter will include a raw copy of the entry data in the import.

### Obtaining your user token

You'll need to inspect cookie values using a browser.  After you have logged into Notion,
You should be able to check for a cookie called `token_v2` in your session.  This is the
value we need in order to access your pages.  Note that this is only used to access Notion
and is never in any way made visible to others.

## Known Issues

- The script is slow due to interactions with the Notion API server.

