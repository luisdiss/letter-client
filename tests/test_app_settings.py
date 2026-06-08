import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import app as app_module
from app import App


def test_load_settings_success(tmp_path, monkeypatch):
    settings_path = tmp_path / 'settings.txt'
    settings = {'server_url': 'http://x', 'expiration': 60}
    settings_path.write_text(json.dumps(settings))

    monkeypatch.setattr(App, '_settings_path', settings_path)

    loaded = App._load_settings()
    assert loaded == settings


def test_load_settings_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(App, '_settings_path', tmp_path / 'nonexistent.txt')
    with pytest.raises(SystemExit):
        App._load_settings()
