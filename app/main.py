from app.bootstrap import bootstrap
from app.cli import run


def main() -> None:
    bootstrap()
    run()


if __name__ == "__main__":
    main()
