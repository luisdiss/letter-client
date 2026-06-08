from contacts import Contacts
from conversations import Conversations
from network import REQUEST_TIMEOUT, handle_network_errors
from parser import parser
from collections.abc import Callable
from pathlib import Path
from typing import Any
import json
import requests as rq
import sys

class State:
    def __init__(self, settings: dict):
        self.auth_token: str | None = None
        self.username: str | None = None
        self.selected_username: str | None = None
        self.settings: dict = settings

_SRC_DIR = Path(__file__).parent

class App:
    _instance = None
    _is_init = False
    _settings_path = _SRC_DIR / "settings.txt"
    _data_dir = _SRC_DIR / "data"

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, state: State) -> None:
        if not App._is_init:
            self.state: State = state
            self.contacts: Contacts | None = None
            self.conversations: Conversations | None = None
            self.dispatch_table: dict[str, Callable] = {}
            App._is_init = True

    def _setup_user_data(self) -> None:
        user_dir = App._data_dir / self.state.username
        user_dir.mkdir(parents=True, exist_ok=True)
        self.contacts = Contacts(self.state, user_dir)
        self.conversations = Conversations(self.state, user_dir)
        self.dispatch_table = self._create_dispatch_table()

    def _login(self) -> None:
        while True:
            choice = input("login or register? ").strip().lower()
            if choice == "login":
                while True:
                    username = input("username: ")
                    password = input("password: ")
                    token = self._login_request(username, password)
                    if token:
                        self.state.username = username
                        self.state.auth_token = token
                        self._setup_user_data()
                        return
                    print("try again or press Ctrl+C to quit\n")
            elif choice == "register":
                username = input("username: ")
                password = input("password: ")
                if self._register_request(username, password):
                    token = self._login_request(username, password)
                    if token:
                        self.state.username = username
                        self.state.auth_token = token
                        self._setup_user_data()
                        return
            else:
                print("type 'login' or 'register'\n")

    @handle_network_errors(default=None)
    def _login_request(self, username: str, password: str) -> str | None:
        resp = rq.post(self.state.settings["server_url"] + "/login", json={"username": username, "password": password}, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            print("login successful\n")
            return resp.json()["auth_token"]
        elif resp.status_code == 401:
            print("wrong password\n")
        elif resp.status_code == 403:
            print(f"no account found for '{username}'\n")
        elif resp.status_code == 400:
            print("invalid username or password\n")
        else:
            print("could not contact the server\n")
        return None

    @handle_network_errors(default=False)
    def _register_request(self, username: str, password: str) -> bool:
        resp = rq.post(self.state.settings["server_url"] + "/users", json={"username": username, "password": password}, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 201:
            print("account created\n")
            return True
        elif resp.status_code == 409:
            print(f"'{username}' is already taken\n")
        elif resp.status_code == 400:
            print("invalid username or password\n")
        else:
            print("could not contact the server\n")
        return False

    @classmethod
    def _load_settings(cls) -> dict:
        try:
            with open(cls._settings_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("file not found error: could not load settings file at location")
        except PermissionError:
            print("permission error: could not load settings file at location")
        sys.exit()

    def _save_settings(self) -> bool:
        try:
            with open(self._settings_path, "w") as file:
                json.dump(self.state.settings, file)
                return True
        except FileNotFoundError:
            print("file not found error: could not save settings file at location")
        except PermissionError:
            print("permission error: could not save settings file at location")
        return False

    def _parse_loop(self) -> None:
        while True:
            to = self.state.selected_username if self.state.selected_username else "nobody"
            prompt = f"{self.state.username}@{to}: "
            command = input(prompt)
            parsed_command = parser.parse_args(command.split(" "))
            if parsed_command:
                func, kwargs = self._dispatch(**vars(parsed_command))
                func(**kwargs)
            print("\n")

    def _dispatch(self, command, **kwargs) -> tuple[Callable, dict[str, Any]]:
        func = self.dispatch_table[command]
        return func, kwargs

    def _create_dispatch_table(self) -> dict[str, Callable]:
        return {
            "select": self.select,
            "delete": self.contacts.delete_contact,
            "view": self.contacts.view_contacts,
            "messages": self.conversations.messages,
            "get": self.conversations.sync_messages,
            "add": self.contacts.add_contact,
            "send": self.conversations.send_message,
        }

    def select(self, username: str) -> None:
        if username in self.contacts.name_to_contact:
            self.state.selected_username = username
        else:
            print(f"{username} not in contacts")
