from app import App, State


def main() -> None:
    settings = App._load_settings()
    state = State(settings)
    app = App(state)
    app._login()
    app._parse_loop()
    print('exiting application')

if __name__ == '__main__':
    main()
