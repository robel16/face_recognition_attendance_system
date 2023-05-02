from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
from attendance.models import Stuff


class RegisterForms(FlaskForm):

    def validate_username(self, username_to_check):
        user = Stuff.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('username already exists please try different username ')

    def validate_email(self, email_to_check):
        email_address = Stuff.query.filter_by(email_address=email_to_check.data).first()
        if email_address:
            raise ValidationError('Email address already exists please try different email address')

    username = StringField(label='User name:', validators=[Length(min=2, max=30), DataRequired()])
    email = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create account')


class LoginForms(FlaskForm):
    username = StringField(label='user name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class TakAttendForm(FlaskForm):
    submit = SubmitField(label='Take attendance')


class AttendReportForm(FlaskForm):
    submit = SubmitField(label='Generate report')
