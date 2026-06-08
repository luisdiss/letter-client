from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from network import REQUEST_TIMEOUT, handle_network_errors
import json
import requests as rq
import sys

if TYPE_CHECKING:
    from app import State

class Contact:
    def __init__(self, name: str, username: str):
        self.name = name
        self.username = username

    def __repr__(self):
        return f'{self.name} -> {self.username}'

    @classmethod
    def deserialise(cls, d):
        if "username" in d and "name" in d:
            return Contact(username = d["username"], name = d["name"])
        return d
    
#an object that stores and modifies contacts 
class Contacts:
    def __init__(self, state: State, data_dir: Path):
        self.state = state
        self.contacts_path: Path = data_dir / "contacts.txt"
        self.name_to_contact: dict[str, Contact] = self._load_contacts()

    def _load_contacts(self) -> dict[str, Contact]:
        try:
            with open(self.contacts_path, 'r') as file:
                return json.load(file, object_hook=Contact.deserialise)
        except FileNotFoundError:
            with open(self.contacts_path, "w") as file:
                file.write("{}")
            return {}
        except PermissionError:
            print(f"permission error: could not load contacts at location: {self.contacts_path}")
            sys.exit()

    def _save_contacts(self) -> bool:
        try:
            with open(self.contacts_path, "w") as file:
                json.dump(self.name_to_contact, file, default=lambda o: o.__dict__)
            return True
        except FileNotFoundError:
            print(f"file not found error: could not save contacts at location: {self.contacts_path}")
        except PermissionError:
            print(f"permission error: could not save contacts to location: {self.contacts_path}")
        return False
    
    #adds a contact if contact is not already in contacts and a user with passed username exists in the db.
    @handle_network_errors()
    def add_contact(self, username: str, name: str) -> None:
        if username in self.name_to_contact:
            print(f"{username} already in contacts")
        
        headers = {"Authorization": f"Token {self.state.auth_token}"}
        resp = rq.head(self.state.settings["server_url"] + f"/users/{username}", headers=headers, timeout=REQUEST_TIMEOUT)
        
        if resp.status_code == 200:
            self.name_to_contact[username] = Contact(username=username, name=name)

            if self._save_contacts():
                print(f'added {username}')
            else:
                del self.name_to_contact[username]

        elif resp.status_code == 404:
            print("user does not exist")
        else:
            print("could not contact the server")

    #deletes a contact if (username in contacts and write to disk succeeds)
    def delete_contact(self, username: str) -> bool:
        if username not in self.name_to_contact:
            print(f"no contact with username {username}")
            return True
        
        contact = self.name_to_contact[username]
        del self.name_to_contact[username]
        if not self._save_contacts():
            self.name_to_contact[username] = contact
            print(f"contact could not be deleted")
            return False
        return True
    
    def view_contacts(self) -> None:
        for contact in self.name_to_contact.values(): print(f"  {contact}")
