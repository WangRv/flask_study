from models import User, Role
from forms.auth import EditProfileForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import ValidationError


class EditProfileAdminForm(EditProfileForm):
    email = StringField("Email", validators=[DataRequired(), Length(6, 64), Email()])
    role = SelectField("Role", coerce=int)
    active = BooleanField("Active")
    confirmed = BooleanField("Confirmed")
    submit = SubmitField()

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, filed):
        if filed.data != self.user.email and User.query.filter_by(email=filed.data).first():
            raise ValidationError("The email is already in use.")
