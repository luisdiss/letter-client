import sys
import os
from types import SimpleNamespace

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from contacts import Contacts, Contact


def test_save_contacts_permission_error(tmp_path, mocker, capsys):
    obj = Contacts.__new__(Contacts)
    obj.state = SimpleNamespace()
    obj.contacts_filename = str(tmp_path / 'contacts.txt')
    obj.name_to_contact = {'a': Contact(name='A', username='a')}

    # simulate PermissionError when trying to open for writing
    mocker.patch('builtins.open', side_effect=PermissionError())

    res = obj._save_contacts()
    assert res is False
    out = capsys.readouterr().out
    assert 'permission error' in out
