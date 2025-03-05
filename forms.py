from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField ,SubmitField ,FileField,TelField,DateField,SelectField
from wtforms.validators import InputRequired, Length,DataRequired,Email,Regexp

class LoginForm(FlaskForm):
    email = StringField('Email or Username', validators=[DataRequired(),Email(message="Enter a valid email address.")])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8, message="Password must be at least 8 characters long.")])
    submit = SubmitField('Continue')
    
class RegistrationForm(FlaskForm):
        image = FileField('Upload Your Profile Picture',validators=[DataRequired()])
        first_name = StringField('Full Name',validators=[DataRequired(), Length(max=100)])
        phone = TelField('Phone Number',validators=[DataRequired(),Regexp(r'^[0-9]{10}$', message="Enter a valid 10-digit phone number")])
        email = StringField('email',validators=[DataRequired(),Email(message="Enter a valid email address")])
        password = PasswordField('Password',validators=[DataRequired(),Length(min=8, message="Password must be at least 8 characters long")])
        dob = DateField('Date of Birth',validators=[DataRequired()], format='%Y-%m-%d')
        qualification = SelectField('Select Your Qualification',choices=[('pre-matriculation','Pre-Matriculation'),('matriculation','Matriculation'),('intermediate','Intermediate'),('graduate','Graduate'),('post-graduate','Post-Graduate'),('phd','PhD')],validators=[DataRequired()])
        submit = SubmitField('Submit')