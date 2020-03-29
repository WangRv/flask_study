from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

# db model
from models import User


# User registry form
class UserRegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(6, 30)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(6, 64)])
    username = StringField("Username", validators=[DataRequired(), Length(6, 64), Regexp("^[a-zA-Z]+[0-9]*")])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128, ), EqualTo("password2")])
    password2 = PasswordField("Confirm password")
    submit = SubmitField()

    # individual validator
    def validator_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("The email is already in use.")

    def validator_username(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError("The username is already in use.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(6, 64)])

    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128, )])
    remember = BooleanField("Remember me")
    submit = SubmitField()


class ForgetForm(LoginForm):
    """Only necessary email field"""
    password = HiddenField()
    remember = HiddenField()
    submit = SubmitField("Send To Verify Email")


class ResetPasswordForm(ForgetForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(6, 64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128, ), EqualTo("password2")])
    password2 = PasswordField("Confirm password")
    submit = SubmitField("Set your new password")
