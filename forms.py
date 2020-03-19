from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    PasswordField,
    BooleanField,
    SelectField,
    HiddenField)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    URL,
    Optional)

from . import Category

string_filed = lambda name, *validators: StringField(name, validators=[*validators])
bool_filed = lambda name, *validators: BooleanField(name, validators=[*validators])
select_filed = lambda name, **kwargs: SelectField(name, **kwargs)
ck_filed = lambda name, *validators: CKEditorField(name, validators=[*validators])
password_filed = lambda name, *validators: PasswordField(name, validators=[*validators])
text_area_filed = lambda name, *validators: TextAreaField(name, validators=[*validators])
submit_filed = lambda name: SubmitField(name)


class HelloForm(FlaskForm):
    """form settings"""
    name = string_filed("Name", DataRequired(), Length(1, 30))
    body = text_area_filed("Message", DataRequired(), Length(1, 200))
    submit = submit_filed(name=None)


# Login Form
class LoginForm(FlaskForm):
    username = string_filed("Username", DataRequired(), Length(6, 20))
    password = password_filed("Password", DataRequired(), Length(8, 128))
    remember = bool_filed("Remember me")
    submit = submit_filed("Log in")


# Post Form
class PostForm(FlaskForm):
    title = string_filed("Title", DataRequired(), Length(1, 60))
    category = select_filed("Category", oerce=int, default=1)
    body = ck_filed("body", DataRequired())
    submit = submit_filed(None)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.oder_by(Category.name).all()]


# Category Form
class CategoryForm(FlaskForm):
    name = string_filed("Name", DataRequired(), Length(1, 30))
    submit = submit_filed(name=None)


# comments Form
class CommentForm(FlaskForm):
    author = string_filed("Name", DataRequired(), Length(1, 30))
    email = string_filed("Email", Email(), Length(1, 254))
    site = string_filed("Site", Optional(), URL(), Length(0, 255))
    body = text_area_filed("Comment", DataRequired())
    submit = SubmitField()


# admin comment
class AdminCommentForm(FlaskForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()
