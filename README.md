Client — Letter CLI
=====================

A small command-line client for interacting with the Letter server. Focused on a clear UX for demos and local development.

Highlights
----------
- Lightweight CLI with subcommands (parser-based)
- Local persistence of messages (`messages.txt`) and conversation name mapping (`names.txt`)
- Simple sync model: `get` fetches unread messages from the server

Quickstart
----------
1. Create and activate a virtualenv (optional):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (if any):

```bash
pip install -r requirements.txt
```

3. Run the client:

```bash
python client.py
```

Basic commands
--------------
- `get` — fetch new messages from the server and persist locally
- `select <username>` — select a contact to send messages to
- `send <message words...>` — send a message to the selected contact
- `messages <count>` — show the last `<count>` local messages for the selected contact
- `add <username> <name>` — add a contact mapping
- `delete <username>` — remove a contact

Files of interest
-----------------
- `client.py` — CLI entry and main loop
- `conversations.py` — message model, local persistence and sync
- `contacts.py` — contact management
- `parser.py` — CLI argument parsing

Next improvements
-----------------
- Add interactive TUI/web UI for demoing real-time features
- Add unit tests for message parsing and persistence
- Add a development `requirements.txt` and a README section describing settings

Usage example
-------------
After login, select a user and send a message:

```bash
select alice
send hi alice how are you
get
messages 10
```

