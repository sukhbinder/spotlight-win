import click

from .spotlight import run
from .config import init_config

@click.command()
def cli():
    """Spotlight for Windows - A quick launcher for files, commands, and more."""
    init_config()
    run()
