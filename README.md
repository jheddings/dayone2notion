# dayone2notion

Import content from Day One into Notion.

## Requirements

This script uses the notion-py client library.  Install using pip:

```
python3 -m pip install notion-py
```

## Usage

1. Export a journal from Day One in JSON format.
2. Unzip the archive.
3. Pass the `.json` file to script, e.g.:

```
python3 dayone2notion.py export/Journal.json
```

## Known Issues

- The script is slow due to interactions with the Notion API server.
- Photos and videos are not handled correctly.
- Markup is not being handled correctly.

