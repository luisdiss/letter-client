import sys
import os
from types import SimpleNamespace
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import App, State


class DummyContacts:
    def delete_contact(self, username): return True
    def view_contacts(self): return None
    def add_contact(self, username, name): return None

class DummyConversations:
    def messages(self, count): return None
    def sync_messages(self): return None
    def send_message(self, msg_text): return None


@pytest.fixture(autouse=True)
def reset_app_singleton():
    App._instance = None
    App._is_init = False
    yield
    App._instance = None
    App._is_init = False


@pytest.fixture
def app():
    state = State({'server_url': 'http://test'})
    return App(state)


def test_login_request_success(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=200, json=lambda: {'auth_token': 'tok'}))
    assert app._login_request('u', 'p') == 'tok'


def test_login_request_wrong_password(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=401, json=lambda: {}))
    assert app._login_request('u', 'p') is None


def test_login_request_no_account(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=403, json=lambda: {}))
    assert app._login_request('u', 'p') is None


def test_register_request_success(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=201))
    assert app._register_request('alice', 'password') is True


def test_register_request_username_taken(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=409))
    assert app._register_request('alice', 'password') is False


def test_register_request_invalid(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=400))
    assert app._register_request('alice', 'password') is False


def test_register_request_server_unreachable(app, mocker):
    mocker.patch('app.rq.post', return_value=SimpleNamespace(status_code=500))
    assert app._register_request('alice', 'password') is False


def test_exit_command_in_parse_loop(app, mocker):
    app.dispatch_table = {"exit": app.exit}
    app.state.username = "alice"
    app.state.selected_username = None
    mocker.patch('builtins.input', return_value="exit")
    with pytest.raises(SystemExit):
        app._parse_loop()
