from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import Optional, Length


class DescriptionForm(FlaskForm):
    """Photo description"""
    description = TextAreaField("Description", validators=[Optional(), Length(0, 500)])
    submit = SubmitField()


class TagForm(FlaskForm):
    """Tag of photo Form"""
    tag = StringField("Add Tag (use space to separate)", validators=[Optional(), Length(0, 64)])
    submit = SubmitField()


class CommentForm(FlaskForm):
    """Form for comments"""
    body = TextAreaField("Comment", validators=[Optional(), Length(0, 500)])
    submit = SubmitField()
