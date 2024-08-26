from flask import render_template, request, Response, redirect, url_for, flash, jsonify
from app import app, db
from .forms import BmiForm, UserLoginForm, RegisterUser, UserBodyForm, GoalForm
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app.models import User, Body, Food, Goal


def get_user_data():

    user = {
            'username': current_user.username,
            'email': current_user.email,
            'age': current_user.age,
            'gender': current_user.gender,
            'height': current_user.height,
            'weight': current_user.weight
        }
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    """"sumary_line
    
    route to calculate:
    BMI (Body Mass Index)
    BMR (basal metabolic rate) and caliroies number of protein and carb and fats
    """
    form = BmiForm()
    data = {}
    if request.method == 'POST':
        if form.validate_on_submit():
            bmi = (form.weight.data / ((form.height.data / 100) ** 2))

            if form.gender.data == 'male':
                bmr = 66.47 + (13.75 * form.weight.data) + (5.003 *  form.height.data) - (6.755 * form.age.data)    
            else:
                bmr = 655.1 + (9.563 * form.weight.data) + (1.850 *  form.height.data) - (6.755 * form.age.data)
            
            bmr = bmr * activity_calc(form.activity.data)
            
            protein = [round((bmr * 20) / 100, 2), round((bmr * 40) / 100, 2)] 
            carb = [round((bmr * 40) / 100, 2), round((bmr * 60) / 100, 2)]
            fats = [round((bmr * 20) / 100, 2), round((bmr * 35) /100, 2)]
            water_intake = form.weight.data * 0.033
                
            data = {
                'bmi': bmi,
                'bmr': bmr,
                'protein': protein,
                'carb': carb,
                'fats': fats,
                'water': water_intake
            }

    return render_template('bmi.html', form=form, data=data), 200
    # return jsonify(users, status=200, mimetype='application/json')

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
            user = User(username=form.username.data, email=form.email.data, age=form.age.data, gender=form.gender.data, height=form.height.data, weight=form.weight.data)
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_user_data()
    if current_user.is_authenticated:
        form = UserBodyForm()
        body_records = {}
        rows = {}
        rows = db.session.query(Body).filter_by(user_id = current_user.id).all()
        if form.validate_on_submit():
            totalWeight = round(form.total_body_water.data + form.protein.data + form.minerals.data + form.body_fat.data, 1)
            body = Body(user_id=current_user.id, total_body_water=form.total_body_water.data, protein=form.protein.data, minerals=form.minerals.data, body_fat=form.body_fat.data)
                    ## i need to update user weight every time
            user = User.query.get(current_user.id)
            user.weight = totalWeight
            bmr = body.calculate_bmr()
            db.session.add(body, user)
            db.session.commit()
            rows = db.session.query(Body).filter_by(user_id = current_user.id).all()
            return redirect(url_for('profile'))


    return render_template('user.html', user=user, form=form, body_records=rows)


@app.route('/goal', methods=['GET', 'POST'])
def goal():
    form = GoalForm()
    seperate = {}
    if form.validate_on_submit():
        caliories = cal_per_day_after_goal(form.goal.data, form.level.data)
        seperate = seprate_cal_need(caliories)
        goal = Goal(user_id=current_user.id, goal=form.goal.data, level=form.level.data, 
                    fats_cal_per_day=seperate.get('fats')[1], protein_cal_per_day=seperate.get('protein')[1], 
                    carb_cal_per_day=seperate.get('carbs')[1])
        db.session.add(goal)
        db.session.commit()
        print('xxxxxxxxxxx')
        print(seperate)
        # return jsonify({'caliories_needed': seperate})
    user = get_user_data()
    x = request.args.get('?qq')
    result = db.session.query(Food).filter(Food.name.like(f'%{x}%'))
    for row in result:
        print(row)
        print("name :", row.calories)
        return jsonify({'name': row.name, 'calories': row.calories, 'calories_needed': seperate})
    return render_template('goal.html', user=user, form=form, data=seperate)


def seprate_cal_need(caliories):

    """calculate every factor or body need protein, fats, carbs
        Args: caliories per day
        Return: dict contain all factors needed
    """
    protein_g = 2.5 * current_user.weight
    protein_cal = protein_g * 4
    fat_cal = caliories * (25 / 100)
    fat_g = fat_cal / 9
    carb_cal = caliories - (protein_cal + fat_cal)
    carb_g = carb_cal / 4
    caliories_needed = {
        "protein": [protein_g, protein_cal],
        "fats": [fat_g, fat_cal],
        "carbs": [carb_g, carb_cal],
    }
    return caliories_needed


def cal_per_day_after_goal(goal, level):
    """calculate caliories needed per day based on level from the form
    
    Keyword arguments:
    argument -- goal: gain or lost weight
             -- level: level bases on long,balanced,shot term 

    Return: caliroies needed per day
    """
    

    user = User.query.get(current_user.id)
    bmr = user.calculate_bmr()
    bmr = bmr * activity_calc(level)
    if goal == 'Gain weight':
        if level == 'Long Term':
            caliories = bmr + 200
        elif level == 'Balanced':
            caliories = bmr + 500
        else:
            caliories = bmr + 700
    
    if goal == 'Lose weight':
        if level == 'Long Term':
            caliories = bmr - 200

        elif level == 'Balanced':
            caliories = bmr - 500
        else:
            caliories = bmr - 700
    
    print('zzzzzzzzzzzzzzzzzz', caliories)
    return caliories

