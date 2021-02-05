# dayone2notion

Import content from Day One into Notion.

## Requirements

This script uses the notion-py client library.  Install using pip:

```
python3 -m pip install notion-py
```

## Usage

First, open the `main.py` script and edit the configuration details for your Notion account.

1. Export a journal from Day One in JSON format.
2. Unzip the archive.
3. Pass the `.json` file to script, e.g.:

```
python3 main.py export/Journal.json
```

### Obtaining your user token

You'll need to inspect cookie values using a browser.  After you have logged into Notion,
You should be able to check for a cookie called `token_v2` in your session.  This is the
value we need in order to access your pages.  Note that this is only used to access Notion
and is never in any way made visible to others.

## Known Issues

- The script is slow due to interactions with the Notion API server.
- Photos and videos are not handled correctly.
- Markup is not being handled correctly.

