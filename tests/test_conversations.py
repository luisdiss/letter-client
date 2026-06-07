import sys
import os
from types import SimpleNamespace

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from conversations import Conversations


def make_state():
    return SimpleNamespace(auth_token='token', settings={'server_url': 'http://test'})


def test_get_messages_success(tmp_path, mocker):
    state = make_state()
    conv = Conversations(state)
    conv.name_path = tmp_path / 'names.txt'
    conv.messages_path = tmp_path / 'messages.txt'

    fake_resp = SimpleNamespace(status_code=200, json=lambda: [{
        'conversation_id': 1,
        'author': 'bob',
        'sent_at': 1,
        'content': 'hi',
        'expiration': 0
    }])

    mocker.patch('conversations.rq.get', return_value=fake_resp)

    res = conv._get_messages('http://test')
    assert isinstance(res, list)
    assert res[0]['author'] == 'bob'
