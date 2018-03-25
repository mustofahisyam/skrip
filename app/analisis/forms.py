from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User


class KlusterForm(FlaskForm):
	nama = StringField('Nama Model', 
                        validators=[DataRequired()])
	jumlah = StringField('Jumlah Kluster', 
                        validators=[DataRequired()])
	submit = SubmitField('Analyze')
		