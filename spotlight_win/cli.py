import click

from .spotlight import run


@click.command()
def cli():
    """Spotlight for Windows - A quick launcher for files, commands, and more."""
    run()
