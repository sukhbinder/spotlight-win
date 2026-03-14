import click
import sys
import signal

from .spotlight import run
from .config import init_config

@click.command()
def cli():
    """Spotlight for Windows - A quick launcher for files, commands, and more."""
    def signal_handler(sig, fname):
        print("Received interupt signal, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        config = init_config()
        run(config)
    except KeyboardInterrupt:
        sys.exit(0)

