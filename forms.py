from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

string_filed = lambda name, *validators: StringField(name, validators=[*validators])
text_area_filed = lambda name, *validators: TextAreaField(name, validators=[*validators])
submit_filed = lambda : SubmitField()


class HelloForm(FlaskForm):
    """form settings"""
    name = string_filed("Name", DataRequired(), Length(1, 30))
    body = text_area_filed("Message",DataRequired(),Length(1,200))
    submit = submit_filed()
