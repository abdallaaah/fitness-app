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
        age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=7, max=100, message="Age Must Be Between 7 and 100")])
        activity = SelectField(u'Current Level Of Activity', choices=[('sedentary', 'Little - no Exercise'), ('lightly-active', '1-3'), ('moderately-active', '3-5'), ('active', '6-7'), ('extremely-active', 'Hard Exercise 6-7')], validators=[DataRequired()])
        calculate_submit = SubmitField('Calculate')



class UserLoginForm(FlaskForm):
        
        username = StringField('User Name', [DataRequired()])
        password = PasswordField('Password', [DataRequired()])
        remember_me = BooleanField('Remember Me')
        submit = SubmitField('Sign In')

class RegisterUser(FlaskForm):
        username = StringField('User Name', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), email()])
        age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=7, max=100, message="Age Must Be Between 7 and 100")])
        gender = SelectField(u'Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
        weight = FloatField('weight', validators=[DataRequired()])
        height = FloatField('Height', validators=[DataRequired()])
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
                
class UserBodyForm(FlaskForm):
        # weight = FloatField('Weight', validators=[DataRequired(), NumberRange(min=15, max=300, message="Height Must Be Between 15 and 300")])
        # height = FloatField('Height', validators=[DataRequired(), NumberRange(min=54, max=250, message="Height Must Be Between 54 and 150")])
        total_body_water = FloatField('Total Body Water', validators=[DataRequired()])
        protein = FloatField('Protein', validators=[DataRequired()])
        minerals = FloatField('Minerals', validators=[DataRequired()])
        body_fat = FloatField('Body Fat', validators=[DataRequired()])
        submit = SubmitField('Add Record')

class GoalForm(FlaskForm):
        goal = SelectField(u'Goal', choices=[('Gain weight', 'Gain weight'), ('Lose weight', 'Lost weight')], validators=[DataRequired()])
        level = SelectField(u'Level', choices=[('Long Term', 'Long Term'), ('Balanced', 'Balanced (Recommended)'), ('Short Term','Short Term')], validators=[DataRequired()])
        activity = SelectField(u'Current Level Of Activity', choices=[('sedentary', 'Little - no Exercise'), ('lightly-active', '1-3'), ('moderately-active', '3-5'), ('active', '6-7'), ('extremely-active', 'Hard Exercise 6-7')], validators=[DataRequired()])
        submit = SubmitField('Set Goal')





                
