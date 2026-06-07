Client — Letter CLI
=====================

Command-line client for the Letter server.

Setup
-----
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Before running, set the server URL in `src/settings.txt`:

```json
{
    "server_url": "http://localhost:8000",
    "expiration": null
}
```

Run from the `src/` directory:

```bash
cd src
python client.py
```

Commands
--------
- `get` — fetch unread messages from the server
- `select <username>` — select who you're messaging
- `send <message>` — send a message to the selected contact
- `messages <count>` — show the last N local messages with the selected contact
- `add <username> <name>` — add a contact
- `delete <username>` — remove a contact

Local files
-----------
The client stores everything locally in `src/`:

- `settings.txt` — server URL and expiration config
- `contacts.txt` — your contact list
- `messages.txt` — message history (one JSON object per line)
- `names.txt` — maps usernames to conversation IDs

Files
-----
- `client.py` — entry point
- `app.py` — command loop and login
- `conversations.py` — message sync and local persistence
- `contacts.py` — contact management
- `parser.py` — CLI argument parsing
