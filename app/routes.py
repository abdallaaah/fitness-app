from flask import render_template, request, Response, redirect, url_for, flash, jsonify
from app import app, db
from .forms import BmiForm, UserLoginForm, RegisterUser
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app.models import User


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    form = BmiForm()
    data = {}
    users = [{'id': 1, 'username': 'Alice'}, {'id': 2, 'username': 'Bob'}]
    if request.method == 'POST':
        if form.validate_on_submit():
            bmi = (form.weight.data / ((form.height.data / 100) ** 2))
            if form.gender.data == 'male':
                bmr = 66.47 + (13.75 * form.weight.data) + (5.003 *  form.height.data) - (6.755 * form.age.data)    
            else:
                bmr = 655.1 + (9.563 * form.weight.data) + (1.850 *  form.height.data) - (6.755 * form.age.data)
            
            amr = bmr * activity_calc(form.activity.data)
            
            protein = [round((amr * 20) / 100, 2), round((amr * 40) / 100, 2)] 
            carb = [round((amr * 40) / 100, 2), round((amr * 60) / 100, 2)]
            fats = [round((amr * 20) / 100, 2), round((amr * 35) /100, 2)]
            water_intake = form.weight.data * 0.033
                
            data = {
                'bmi': bmi,
                'amr': amr,
                'protein': protein,
                'carb': carb,
                'fats': fats,
                'water': water_intake
            }
                # Response.content_type = 'plain/text'
    return render_template('bmi.html', form=form, data=data), 200
    # return jsonify(users, status=200, mimetype='application/json')

@app.route('/api/users')
def get_users():
    users = [{'id': 1, 'username': 'sweety'},
             {'id': 2, 'username': 'pallavi'}]
    return jsonify({'users': users})
def activity_calc(activity_level):
    activity = {
        'sedentary': 1.2,
        'lightly-active': 1.375,
        'moderately-active': 1.55,
        'active': 1.725,
        'extremely-active': 1.9
    }
    return activity.get(activity_level, 1.2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = {}
    if current_user.is_authenticated:
        print('from hereeeeeeeeeeeeeeeeeeeeee')
        return redirect(url_for('index'))
    LoginForm = UserLoginForm()
    if request.method == 'POST':
        print('i am inside the posttttttttttttttttttttt')
        print(LoginForm.username.data)
        user = db.session.scalar(sa.select(User).where(User.username == LoginForm.username.data))
        print('xxxxxxxx there is user', user)
        if user is None or not user.check_password(LoginForm.password.data):
            flash('invalid username or password')
        else:
            login_user(user, LoginForm.remember_me.data)
            return redirect(url_for('index'))
        if LoginForm.validate_on_submit():
            print(f"zzzzzzzzzzzzz the username is {LoginForm.username.data}")
    return render_template('login.html',form=LoginForm)

@app.route('/register', methods=['GET', 'POST'])
def register():
    data = {}
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterUser()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congraltualtions you registered')
            return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
