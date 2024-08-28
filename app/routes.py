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
            bmi = round((form.weight.data / ((form.height.data / 100) ** 2)), 2)
            if form.gender.data == 'male':
                bmr = 66.47 + (13.75 * form.weight.data) + (5.003 *  form.height.data) - (6.755 * form.age.data)    
            else:
                bmr = 655.1 + (9.563 * form.weight.data) + (1.850 *  form.height.data) - (6.755 * form.age.data)
            
            bmr = int(bmr * activity_calc(form.activity.data))
            
            protein = [int((bmr * 20) / 100), int((bmr * 40) / 100)] 
            carb = [int((bmr * 40) / 100), int((bmr * 60) / 100)]
            fats = [int((bmr * 20) / 100), int((bmr * 35) /100)]
            water_intake = round(form.weight.data * 0.033, 1)
                
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
        bmr = None
        rows = db.session.query(Body).filter_by(user_id = current_user.id).all()
        if form.validate_on_submit():
            totalWeight = round(form.total_body_water.data + form.protein.data + form.minerals.data + form.body_fat.data, 1)
            body = Body(user_id=current_user.id, total_body_water=form.total_body_water.data, protein=form.protein.data, minerals=form.minerals.data, body_fat=form.body_fat.data)
                    ## i need to update user weight every time
            user = User.query.get(current_user.id)
            user.weight = totalWeight
            db.session.add(body, user)
            user.calculate_bmr()

            db.session.commit()
            bmr = body.calculate_bmr()
            rows = db.session.query(Body).filter_by(user_id = current_user.id).all()
            return redirect(url_for('profile'))


    return render_template('user.html', user=user, form=form, body_records=rows, bmr=bmr)


@app.route('/goal', methods=['GET', 'POST'])
def goal():
    form = GoalForm()
    goal = {}
    seperate = {}
    user = get_user_data()
    goal = db.session.scalar(sa.select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.id.desc()).limit(1))
    # print('seeeeeeeeeeee goalss', goal.fats_cal_per_day)
    if form.validate_on_submit(): 
        ########################################################################
        egg = Food(name="egg", category="protein", calories=50)
        bread = Food(name="bread", category="carb", calories=200)   
        chicken = Food(name="chicken", category="protein", calories=150)   
        ########################################################################
        goal = Goal(user_id=current_user.id, goal=form.goal.data, level=form.level.data)
        db.session.add_all([goal, egg, bread, chicken])
        db.session.commit()
        caliories = goal.cal_per_day_after_goal(form.goal.data, form.level.data, form.activity.data)
        goal.total_claories_per_day = caliories
        seperate = goal.seprate_cal_need(caliories)
        goal.update_user_daily_goal_cal(caliories, seperate)
        print('555555555555555555555555555555555', goal.fats_cal_per_day, goal.carb_cal_per_day)
    if request.args.get('?qq'):
        food_name = request.args.get('?qq')
        food = db.session.query(Food).filter(Food.name.like(f'%{food_name}%')).first()
        return jsonify({
        'name': food.name,
        'calories': food.calories
    })
        
    return render_template('goal.html', user=user, form=form, data=goal)

@app.route('/search_food')
def search_food():
    if request.args.get('?qq'):
        food_name = request.args.get('?qq')
        food = db.session.query(Food).filter(Food.name.like(f'%{food_name}%')).first()
        return jsonify({
        'name': food.name,
        'calories': food.calories,
        'category': food.category
    })

@app.route('/update_cal')
def update_user_current_cal():
    # Retrieve query parameters without the '?'
    fetch = request.args.get('fetch', default=False, type=bool)
    if request.args.get('name') and request.args.get('name') and int(request.args.get('calories')) and request.args.get('category'):
        food_name = request.args.get('name')
        calories = int(request.args.get('calories'))
        category = request.args.get('category')
        goal = db.session.scalar(sa.select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.id.desc()).limit(1))
        total_claories_per_day, current_protein_cal, current_carb_cal, current_fat_cal = goal.update_user_current_cal(calories, category)

        # Print the retrieved parameters for debugging
        print('Food Name:', food_name)
        print('Calories:', calories)
        print('Category:', category)

        # You can use these parameters as needed
        # For demonstration, let's return them as JSON
        return jsonify({
            'total_claories_per_day': total_claories_per_day,
            'current_protein_cal': current_protein_cal,
            'current_carb_cal': current_carb_cal,
            'current_fat_cal': current_fat_cal,
        })
    
    if fetch:
        if fetch:
        # Retrieve the current state of the user's calorie data
            goal = db.session.scalar(sa.select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.id.desc()).limit(1))
            user_calories = {
                'total_claories_per_day': goal.total_claories_per_day,
                'current_protein_cal': goal.current_protein_cal,
                'current_carb_cal': goal.current_carb_cal,
                'current_fat_cal': goal.current_fat_cal
            }
            return jsonify(user_calories)




