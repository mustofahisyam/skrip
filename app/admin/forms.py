from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo


class AddUser(FlaskForm):
	email = StringField('Email', 
                        validators=[DataRequired(), 
                        Length(min=1, max=64),
                        Email()])
	username = StringField('Username',
							validators=[DataRequired()])
	password = PasswordField('Password', 
							validators=[DataRequired()])
	role_id = StringField('Role_id', 
                        validators=[DataRequired()])
	submit = SubmitField('Tambah')
		