from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from ..extensions import db
from .models import Users, UserRole, UserStatus


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class CreateUserForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    role = SelectField('Role', choices=[])
    chat_id = StringField('Chat_id')
    status = SelectField('Status', choices=[])
    submit = SubmitField('Save')
    user_id = StringField('User_id')

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role, role) for role in UserRole.get_new_user_role_list()]
        self.status.choices = [(status, status) for status in UserStatus.get_new_user_status_list()]

    def validate(self):
        initial_validation = super(CreateUserForm, self).validate()
        if not initial_validation:
            return False

        user = db.session.query(Users).filter_by(login=self.login.data.lower()).first()
        if user:
            self.login.errors.append("User with the same login already exists.")
            return False

        if self.chat_id.data:
            try:
                int(self.chat_id.data)
            except ValueError:
                self.chat_id.errors.append("Invalid chat_id.")
                return False

        return True


class EditUserForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)], render_kw={'readonly': True})
    password = PasswordField('Password')
    role = SelectField('Role', choices=[])
    chat_id = StringField('Chat_id')
    status = SelectField('Status', choices=[])
    submit = SubmitField('Save')
    user_id = StringField('User_id')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role, role) for role in UserRole.get_new_user_role_list()]
        self.status.choices = [(status, status) for status in UserStatus.get_new_user_status_list()]

    def validate(self):
        initial_validation = super(EditUserForm, self).validate()
        if not initial_validation:
            return False

        if self.password.data and (len(self.password.data) < 6 or len(self.password.data) > 20):
            self.password.errors.append("Field must be between 6 and 20 characters long.")
            return False

        if self.chat_id.data:
            try:
                int(self.chat_id.data)
            except ValueError:
                self.chat_id.errors.append("Invalid chat_id.")
                return False

        return True


class ResetPasswordForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)], render_kw={'readonly': True})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm = PasswordField('Verify password',
                            validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(ResetPasswordForm, self).validate()
        if not initial_validation:
            return False
        return True
