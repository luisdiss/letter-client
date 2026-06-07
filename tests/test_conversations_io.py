import sys
import os
import json
from types import SimpleNamespace

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from conversations import Conversations, Message
from bidict import bidict


def make_state():
    return SimpleNamespace(auth_token='token', settings={'server_url': 'http://test', 'expiration': 3600})


def test_load_conversation_id_to_conversation_parsing(tmp_path, capsys):
    msgs = tmp_path / 'messages.txt'
    conversation_id = 1
    # valid line
    msgs.write_text(json.dumps({
        'conversation_id': conversation_id,
        'author': 'alice',
        'sent_at': 1,
        'content': 'hello',
        'expiration': 0
    }) + "\n" + "not a json\n") #tests the handling of decode error

    obj = Conversations.__new__(Conversations)
    obj.messages_path = msgs
    obj.name_path = tmp_path / 'names.txt'
    obj.name_to_conversation_id = bidict()

    convs = obj._load_conversation_id_to_conversation()
    assert conversation_id in convs
    out = capsys.readouterr().out
    assert 'parsing error' in out


def test_append_and_save_messages(tmp_path):
    obj = Conversations.__new__(Conversations)
    obj.messages_path = tmp_path / 'messages.txt'
    obj.name_path = tmp_path / 'names.txt'
    obj.name_to_conversation_id = bidict({'alice': 1})
    obj.conversation_id_to_conversation = {}

    msg = Message(conversation_id=1, author='alice', sent_at=1, content='hi', expiration=0)
    res = obj._append_and_save_messages([msg])
    assert res is True
    content = (tmp_path / 'messages.txt').read_text()
    assert 'hi' in content


def test_send_message_creates_conversation_id(tmp_path, mocker):
    state = make_state()
    obj = Conversations.__new__(Conversations)
    obj.state = state
    obj.messages_path = tmp_path / 'messages.txt'
    obj.name_path = tmp_path / 'names.txt'
    obj.name_to_conversation_id = bidict()
    obj.conversation_id_to_conversation = {}

    state.selected_username = 'alice'

    fake_resp = SimpleNamespace(status_code=200, json=lambda: {'conversation_id': 5})
    mocker.patch('conversations.rq.post', return_value=fake_resp)
    mocker.patch.object(Conversations, '_append_and_save_messages', return_value=True)

    obj.send_message(['hello'])
    assert obj.name_to_conversation_id['alice'] == 5
