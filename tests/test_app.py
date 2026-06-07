import sys
import os
from types import SimpleNamespace

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import App, State


def test_login_request_success(mocker):
    state = State({'server_url': 'http://test'})
    # provide simple stand-ins for contacts and conversations with required methods
    class DummyContacts:
        def delete_contact(self, username: str):
            return True
        def view_contacts(self):
            return None
        def add_contact(self, username: str, name: str):
            return None

    class DummyConversations:
        def messages(self, count: int):
            return None
        def sync_messages(self):
            return None
        def send_message(self, msg_text: list[str]):
            return None

    app = App(state, DummyContacts(), DummyConversations())

    fake_resp = SimpleNamespace(status_code=200, json=lambda: {'auth_token': 'tok'})
    mocker.patch('app.rq.post', return_value=fake_resp)

    token = app._login_request('u', 'p')
    assert token == 'tok'
