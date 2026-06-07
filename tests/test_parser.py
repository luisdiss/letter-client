import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from parser import parser


def test_parse_valid_view():
    ns = parser.parse_args(['view'])
    assert ns is not None
    assert ns.command == 'view'


def test_parse_invalid_commands():
    # unknown command
    assert parser.parse_args(['unknown']) is None
    # empty input
    assert parser.parse_args([]) is None
