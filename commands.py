import click
from . import app, db, MessageTable


@app.cli.command()
@click.option("--count", default=20, help="Quantity of messages,default is 20.")
def forge(count):
    """generate fake messages"""
    db.drop_all()
    db.create_all()

    # called fake generate messages
    from faker import Faker
    fake = Faker("zh_CN")
    click.echo("Working")
    for i in range(count):
        message = MessageTable(name=fake.name(),
                               body=fake.sentence(), timestamp=fake.date_time_this_year())
        db.session.add(message)
    db.session.commit()
    click.echo(f"Created {count} fake messages.")
