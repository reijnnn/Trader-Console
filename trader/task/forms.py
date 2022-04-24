from flask_wtf import FlaskForm
# noinspection PyPackageRequirements
from wtforms.validators import DataRequired
# noinspection PyPackageRequirements
from wtforms import TextAreaField, SubmitField, SelectField, StringField

from ..user.users_service import get_controlled_users


class ModifyTaskForm(FlaskForm):
    task_id = StringField('Task_id')
    task_name = StringField('Task_name')
    task_params = TextAreaField('Task_params', validators=[DataRequired()])
    user = SelectField('User', choices=[], validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ModifyTaskForm, self).__init__(*args, **kwargs)
        self.user.choices = [(user.id, user.login) for user in get_controlled_users() if user.telegram_id]

    def validate(self):
        initial_validation = super(ModifyTaskForm, self).validate()
        if not initial_validation:
            return False

        return True
