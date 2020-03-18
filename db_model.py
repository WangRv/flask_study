from datetime import datetime
from . import db

# generates database column functions
id_column = lambda **kwargs: db.Column(db.Integer, primary_key=True,
                                       **kwargs)
bool_column = lambda **kwargs: db.Column(db.Boolean, **kwargs)
str_column = lambda length, **kwargs: db.Column(db.String(length=length), **kwargs)
text_column = lambda **kwargs: db.Column(db.TEXT, **kwargs)
timestamp_column = lambda **kwargs: db.Column(db.DateTime,
                                              default=datetime.utcnow, index=True, **kwargs)

foreignkey_column = lambda foreign_name, **kwargs: db.Column(db.Integer, db.ForeignKey(foreign_name))
relationship_column = lambda model_name, **kwargs: db.relationship(model_name, **kwargs)


class MessageTable(db.Model):
    id = id_column()
    body = str_column(200)
    name = str_column(30)
    timestamp = timestamp_column()


class Admin(db.Model):
    """administrator model of blog project"""
    id = id_column()
    username = str_column(30)
    password_hash = str_column(128)
    blog_title = str_column(60)
    blog_sub_title = str_column(100)
    name = str_column(30)
    about = text_column()

    def set_password(self,password):
        """use password to convert hash password and to save  db"""
        pass
class Category(db.Model):
    """blog item category model"""
    id = id_column()
    name = str_column(30, unique=True)
    posts = relationship_column("Post", back_populates="category")


class Post(db.Model):
    """blog article mode"""
    id = id_column()
    title = str_column(60)
    body = text_column()
    timestamp = timestamp_column()
    # foreign key column
    category_id = foreignkey_column("category.id")
    # back reference
    category = relationship_column("Category", back_populates="posts")

    # the comment into post
    comments = relationship_column("Comment", back_populates="post", cascade="all")


class Comment(db.Model):
    """blog comment of post mode"""
    id = id_column()
    author = str_column(30)
    email = str_column(254)
    site = str_column(255)
    body = text_column()
    from_admin = bool_column(default=False)
    reviewed = bool_column(default=False)
    timestamp = timestamp_column()
    # foreign key
    post_id = foreignkey_column("post.id")
    post = relationship_column("Post", uselist=False, back_populates="comments")
    # relationship it to self
    replied_id = foreignkey_column("comment.id")
    replied = relationship_column("Comment", back_populates="replies", remote_side=[id])
    replies = relationship_column("Comment", back_populates="replied", cascade="all")
