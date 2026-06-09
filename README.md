Client — Letter CLI
====================

Command-line messaging client. Connects to `https://lettermessaging.com` by default.

Setup
-----
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

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

Using a different server
------------------------
Change `server_url` in `src/settings.txt` to point at your own server:

```json
{
    "server_url": "https://yourdomain.com",
    "expiration": null
}
```
