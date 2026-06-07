from contacts import Contacts
from conversations import Conversations
from parser import parser
from collections.abc import Callable
from typing import Any
import json
import requests as rq
import sys

class State:
    def __init__(self, settings: dict):
        self.auth_token: str | None = None
        self.username: str = None
        self.selected_username: str | None = None
        self.settings: dict = settings

class App:
    _instance = None
    _is_init = False

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, state: State, contacts: Contacts, conversations: Conversations) -> None:
        if not App._is_init:
            self.state: State = state
            self.contacts: Contacts = contacts
            self.conversations: Conversations = conversations
            self.dispatch_table: dict[str, tuple[Callable, dict[str, Any]]] = self._create_dispatch_table()
            App._is_init = True
    
    def _login(self) -> str:
        while True:
            username = input("enter username: ")
            password = input("enter password: ")

            auth_token = self._login_request(username, password)
            if auth_token:
                self.state.username = username
                self.state.auth_token = auth_token
                break

    def _login_request(self, username: str, password: str) -> str | None:
        content = {"username":username, "password":password}
        resp = rq.post(self.state.settings["server_url"]+"/login", json=content)

        if resp.status_code == 200:
            print("login successful\n")
            return resp.json()["auth_token"]
        elif resp.status_code == 401:
            print("not authorised\n")
        elif resp.status_code == 404:
            print(f"no account with username: {username}\n")
        elif resp.status_code == 400:
            print("invalid username or password\n")
        else:
            print("could not contact the server\n")
        return None

    @classmethod
    def _load_settings(self) -> dict:
        try:
            with open("settings.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("file not found error: could not load settings file at location")
        except PermissionError:
            print("permission error: could not load settings file at location")
        sys.exit()

    def _save_settings(self) -> bool:
        try:
            with open("setings.txt", "w") as file:
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
    
    def select(self, username: str):
        if username in self.contacts.name_to_contact: self.state.selected_username = username
        else: print(f"{username} not in contacts")
