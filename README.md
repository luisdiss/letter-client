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

Before running, set your server URL in `src/settings.txt`:

```json
{
    "server_url": "http://localhost:8000",
    "expiration": null
}
```

Use `http://localhost:8000` for a local server. If the server is running behind Caddy, use `https://yourdomain.com`.

Run from the `src/` directory:

```bash
cd src
python client.py
```

On startup you'll be asked to login or register. Multiple accounts can be used on the same device — each account's data is stored separately.

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
- `src/settings.txt` — server URL and expiration config
- `src/data/<username>/contacts.txt` — contact list, scoped per account
- `src/data/<username>/messages.txt` — message history (one JSON object per line)
- `src/data/<username>/names.txt` — maps usernames to conversation IDs

Known limitations
-----------------
- Message history is stored in plain text on disk.
- The server marks messages as read the moment they are fetched. If the client crashes before saving them to disk, those messages are permanently lost.

Files
-----
- `client.py` — entry point
- `app.py` — command loop, login, and registration
- `conversations.py` — message sync and local persistence
- `contacts.py` — contact management
- `network.py` — shared HTTP timeout and connection error handling
- `parser.py` — CLI argument parsing
