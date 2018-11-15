from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.validators import Optional, Length
from blog.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')        


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    access_level = TextField('If you have key, enter here to register a admin account',
        validators=[Optional()])
    phone = StringField('Phone number', validators=[DataRequired(),
        Length(min=10, max=10)])
    fullname = StringField('Fullname', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone_number=phone.data).first()
        if user is not None:
            raise ValidationError('Please use a different phone number.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[Optional()])
    fullname = StringField('Fullname', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Password', validators=[Optional()])
    phone = StringField('Phone number', validators=[Optional(),
        Length(min=10, max=10)])
    submit = SubmitField('Confirm')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone_number=phone.data).first()
        if user is not None:
            raise ValidationError('Please use a different phone number.')


class UploadFile(Form):
    file = FileField(validators=[FileRequired()])
    submit = SubmitField("Submit")


class Messages(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))
        