from flask_wtf import FlaskForm
from wtforms import *

class Register_form(FlaskForm):
	fname = TextField("First Name ",[validators.Required("Please enter your first name.")])
	lname = TextField("Lirst Name ",[validators.Required("Please enter your last name.")])
	email = TextField("Email",[validators.Required("Please enter your email address."),validators.Email("Please enter your email address.")])
	pwd   = PasswordField('New Password',[validators.Required(), validators.EqualTo('cpwd', message='Passwords must match')])
	cpwd  = PasswordField('Repeat Password')
	mob 	= IntegerField("Mobile Number",[validators.Required("Please enter your Mobile Number"),validators.NumberRange(0,100000000000)])
	submit = SubmitField("Send")

	
