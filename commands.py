import click
from . import app, db, MessageTable


@app.cli.command()
@click.option("--count", default=20, help="Quantity of messages,default is 20.")
def forge(count):
    """generate fake messages"""
    from .fakes import fake_messages, MessageTable
    db.metadata.drop_all(db.engine, tables=[MessageTable.__table__])
    db.metadata.create_all(db.engine, tables=[MessageTable.__table__])

    # called fake to generate messages

    click.echo("Working")
    fake_messages(count)
    click.echo(f"Created {count} fake messages.")


@app.cli.command()
@click.option("--category", default=10, help="Quantity of categories,default is 10.")
@click.option("--post", default=50, help="Quantity of posts,default is 50.")
@click.option("--comment", default=500, help="Quantity of comments,default is 500.")
def forge_blog_data(category, post, comment):
    """generate blog data"""
    from .fakes import (db, fake_admin, fake_categories,
                        fake_posts, fake_comments, Admin, Category, Post,
                        Comment)
    db.metadata.drop_all(db.engine, tables=[db.__table__ for db in [Admin, Category, Post, Comment]])
    db.metadata.create_all(db.engine, tables=[db.__table__ for db in [Admin, Category, Post, Comment]])

    # echo help messages
    click.echo("Generating the administrator...")
    fake_admin()

    click.echo(f"Generating {category} categories...")
    fake_categories(category)

    click.echo(f"Generating {post} posts...")
    fake_posts(post)

    click.echo(f"Generating {comment} comments...")
    fake_comments(comment)

    # successfully creating fake data.
    click.echo("Done.")
