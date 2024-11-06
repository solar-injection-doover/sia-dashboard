import logging

from pydoover.cli import CLI

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    CLI().main()
