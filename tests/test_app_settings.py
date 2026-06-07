import sys
import os
import json
import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import App


def test_load_settings_success(tmp_path, monkeypatch):
    # create settings file in tmp dir and chdir into it
    settings_path = tmp_path / 'settings.txt'
    settings = {'server_url': 'http://x', 'expiration': 60}
    settings_path.write_text(json.dumps(settings))

    monkeypatch.chdir(tmp_path)

    loaded = App._load_settings()
    assert loaded == settings


def test_load_settings_missing(monkeypatch):
    tmp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # ensure no settings file
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        App._load_settings()
