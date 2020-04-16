from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, SubmitField, PasswordField,
                     BooleanField, HiddenField, TextAreaField)
from wtforms.validators import (DataRequired, Length, Email,
                                Regexp, EqualTo, Optional)
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


class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 30)])
    user_name = StringField("Username", validators=[DataRequired(), Length(1, 20),
                                                    Regexp("^[a-zA-Z]+[a-zA-Z0-9]*", message="The "
                                                                                             "username should "
                                                                                             "begin with a-z letter "
                                                                                             "or only contain a-z "
                                                                                             "and 0-9 letter.")])
    bio = TextAreaField("Bio", validators=[Optional(), Length(0, 120)])

    def validate_username(self, filed):
        # validate if username reused.
        if filed.data != current_user.username and User.query.filter_by(usname=filed.data).first():
            raise ValidationError("The username is already in use.")


class UploadAvatarForm(FlaskForm):
    image = FileField("Upload (<=3M)", validators=[FileRequired(),
                                                   FileAllowed(["jpg", "png"],
                                                               "The file format should be .jpg or .png")])
    submit = SubmitField()


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField("Crop and update")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    password = PasswordField("New Password", validators=[DataRequired(), Length(8, 128), EqualTo("password2")])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField()


class ChangeEmailForm(FlaskForm):
    old_email = StringField("Old Email", validators=[DataRequired(), Email()], render_kw={"readonly": True})
    new_email = StringField("New email", validators=[DataRequired(), Email()])


class NotificationSettingForm(FlaskForm):
    receive_comment_notification = BooleanField("New comment")
    receive_follow_notification = BooleanField("New follower")
    receive_collect_notification = BooleanField("New collector")


class PrivacySettingForm(FlaskForm):
    public_collections = BooleanField("Public my collection")
    submit = SubmitField()


class DeleteAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username:
            raise ValidationError("Wrong username")
