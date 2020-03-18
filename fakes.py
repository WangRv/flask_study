import random

from sqlalchemy.exc import IntegrityError

from . import Admin, Category, Post, Comment
from . import MessageTable
from . import db
import faker

fake = faker.Faker("zh_CN")


def fake_messages(count):
    for i in range(count):
        message = MessageTable(name=fake.name(),
                               body=fake.sentence(), timestamp=fake.date_time_this_year())
        db.session.add(message)
    db.session.commit()



def fake_admin():
    admin = Admin(
        username="admin",
        blog_title="Blue_log",
        blog_sub_title="No, I'm the real things.",
        name="test name",
        about="about me,it nothing to tell."
    )
    admin.set_password("19930403a")
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    # first to generate default category.
    category_default = Category(name="Default")
    db.session.add(category_default)
    db.session.commit()
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            # rollback affair of database
            db.session.rollback()


def fake_posts(count=200):
    """fake two hundred posts into database"""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(200),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()

        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=50):
    # generate fifty comments into database
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,  # This is allowed showing on the post.
            post=Post.query.get(random.randint(1, Post.query.count()))

        )
        db.session.add(comment)
    salt = int(count * 0.1)

    for i in range(salt):
        # reviewed comments
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,  # This is allowed showing on the post.
            post=Post.query.get(random.randint(1, Post.query.count()))

        )
        db.session.add(comment)
        # administrator
        comment = Comment(
            author="admin",
            email="c269227455@gmail.com",
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,  # This is allowed showing on the post.
            post=Post.query.get(random.randint(1, Post.query.count()))

        )
        db.session.add(comment)
    db.session.commit()
    # reply
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,  # This is allowed showing on the post.
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))

        )
        db.session.add(comment)

    db.session.commit()
