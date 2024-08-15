from flask import Flask
from flask.cli import with_appcontext
import click
from seed import seed_db  # Replace with the actual import path to your seeding function
from config import db, create_app

app = create_app('production')

@click.command('seed-db')
@with_appcontext
def seed_command():
    """Seed the database with initial data."""
    seed_db()
    click.echo('Database seeded successfully.')

# Register the command with the Flask CLI
app.cli.add_command(seed_command)

if __name__ == '__main__':
    app.run()
    