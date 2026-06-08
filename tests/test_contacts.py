import sys
import os
from types import SimpleNamespace

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from contacts import Contacts, Contact


def make_state():
    return SimpleNamespace(auth_token='token', settings={'server_url': 'http://test'})


def test_add_contact_success(tmp_path, mocker):
    state = make_state()
    contacts = Contacts(state, tmp_path)
    contacts.name_to_contact = {}

    fake_resp = SimpleNamespace(status_code=200)
    mocker.patch('contacts.rq.head', return_value=fake_resp)
    mocker.patch.object(Contacts, '_save_contacts', return_value=True)

    contacts.add_contact('alice', 'Alice')

    assert 'alice' in contacts.name_to_contact
    c = contacts.name_to_contact['alice']
    assert isinstance(c, Contact)
    assert c.username == 'alice'


def test_add_contact_user_not_exist(tmp_path, mocker, capsys):
    state = make_state()
    contacts = Contacts(state, tmp_path)
    contacts.name_to_contact = {}

    fake_resp = SimpleNamespace(status_code=404)
    mocker.patch('contacts.rq.head', return_value=fake_resp)

    contacts.add_contact('bob', 'Bob')
    out = capsys.readouterr().out
    assert 'user does not exist' in out
