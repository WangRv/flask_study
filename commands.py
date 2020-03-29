import click
from extension import db
from models import Role


def register_commands(app):
    @app.cli.command(help="Init roles")
    def init_role():
        click.echo("Initializing the roles and permissions...")
        Role.init_role()
        click.echo("Done.")
