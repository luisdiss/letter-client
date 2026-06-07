from .app import App, State
from .contacts import Contacts
from .conversations import Conversations


def main() -> None:
    settings = App._load_settings()
    state = State(settings)
    contacts = Contacts(state)
    conversations = Conversations(state)

    app = App(state, contacts, conversations)

    app._login()
    app._parse_loop()
    print('exiting application')


if __name__ == '__main__':
    main()
