from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, email, EqualTo, ValidationError, NumberRange
from app import db
import sqlalchemy as sa
from app.models import User

class BmiForm(FlaskForm):
        
        weight = FloatField('Weight', validators=[DataRequired(), NumberRange(min=15, max=300, message="Height Must Be Between 15 and 300")])
        height = FloatField('Height', validators=[DataRequired(), NumberRange(min=54, max=250, message="Height Must Be Between 54 and 150")])
        gender = SelectField(u'Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
        age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=100, message="Age Must Be Between 0 and 100")])
        activity = SelectField(u'Current Level Of Activity', choices=[('sedentary', 'Little - no Exercise'), ('lightly-active', '1-3'), ('moderately-active', '3-5'), ('active', '6-7'), ('extremely-active', 'Hard Exercise 6-7')], validators=[DataRequired()])
        calculate_submit = SubmitField('Calculate')



class UserLoginForm(FlaskForm):
        
        username = StringField('UserName', [DataRequired()])
        password = PasswordField('Password', [DataRequired()])
        remember_me = BooleanField('Remember Me')
        submit = SubmitField('Sign In')

class RegisterUser(FlaskForm):
        username = StringField('UserName', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), email()])
        password = PasswordField('passowrd', validators=[DataRequired()])
        password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Register')

        def validate_username(self, username):
                user = db.session.scalar(sa.select(User).where(User.username==username.data))
                if user is not None:
                        raise ValidationError('The username is alredy exist')
                
        def validate_email(self, email):
                user = db.session.scalar(sa.select(User).where(User.email==email.data))
                if user is not None:
                        raise ValidationError('The email is already registered')
                
