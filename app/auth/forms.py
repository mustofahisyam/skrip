from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), 
                        Length(min=1, max=64),
                        Email()])
    password = PasswordField('Password', 
                        validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

