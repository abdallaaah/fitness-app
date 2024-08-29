from typing import Optional
from sqlalchemy.sql import func
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    age: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    gender: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    height: so.Mapped[int] = so.mapped_column(sa.Float, nullable=False)
    weight: so.Mapped[int] = so.mapped_column(sa.Float, nullable=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    body_analysis: so.WriteOnlyMapped['Body'] = so.relationship(back_populates=('user'))
    goal: so.WriteOnlyMapped['Goal'] = so.relationship(back_populates=('user'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(str(password))
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login.user_loader
    def load_user(id):
        return db.session.get(User, int(id))
    
    def __repr__(self):
        return f"<User {self.username} {self.password_hash}>"
    
    def calculate_bmr(self):

        if self.gender == 'male':

            bmr = 66.47 + (13.75 * self.weight) + (5.003 *  self.height) - (6.755 * self.age)
        else:
            bmr = 655.1 + (9.563 * self.weight) + (1.850 *  self.height) - (6.755 * self.age)
        # bmi = (self.weight / ((self.height / 100) ** 2))
        
        return bmr
    
    def calculate_bmi(self):
        bmi = (self.weight / ((self.height / 100) ** 2))
        return round(bmi, 2)




class Body(db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    bmi: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    bmr: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    total_body_water: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    protein: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    minerals: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    body_fat: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    total_weight: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='body_analysis')
    created_at: so.Mapped[str] = so.mapped_column(sa.DateTime, default=func.now(), nullable=False)


    def __init__(self, user_id, total_body_water, protein, minerals, body_fat):

        self.user_id = user_id
        self.total_body_water = total_body_water
        self.protein = protein
        self.minerals = minerals
        self.body_fat = body_fat
        self.total_weight = round(total_body_water + protein + minerals + body_fat, 2)
        # self.bmi = round((self.user.weight / ((self.user.height / 100) ** 2)), 2)
    
    def calculate_bmr(self):

        bmr = self.user.calculate_bmr()
        self.bmi = self.user.calculate_bmi()
        print('bmiiiiiiiiiii', self.bmi)
        self.bmr = round(bmr, 2)
        db.session.add(self)
        db.session.commit()


class Food(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    calories: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    category: so.Mapped[str] = so.mapped_column(sa.String, nullable=True)


class Goal(db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=True)
    goal: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    level: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    fats_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    protein_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    carb_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    current_protein_cal: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    current_carb_cal: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    current_fat_cal: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    total_claories_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    user_id: so.Mapped[int] =  so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='goal')
    created_at: so.Mapped[str] = so.mapped_column(sa.DateTime, default=func.now(), nullable=False)

    def __init__(self, user_id, goal, level):

        self.user_id = user_id
        self.goal = goal
        self.level = level
        self.total_claories_per_day = 0
        self.fats_cal_per_day = 0
        self.protein_cal_per_day = 0
        self.carb_cal_per_day = 0
        self.current_carb_cal = 0
        self.current_fat_cal = 0
        self.current_protein_cal = 0

    def activity_calc(self, activity_level):
        activity = {
            'sedentary': 1.2,
            'lightly-active': 1.375,
            'moderately-active': 1.55,
            'active': 1.725,
            'extremely-active': 1.9
        }
        return activity.get(activity_level, 1.2)

    def seprate_cal_need(self, caliories):

        """calculate every factor or body need protein, fats, carbs
            Args: caliories per day
            Return: dict contain all factors needed
        """
        protein_g = 2.5 * self.user.weight
        protein_cal = protein_g * 4
        fat_cal = caliories * (25 / 100)
        fat_g = fat_cal / 9
        print('issue caaaaal', caliories)
        carb_cal = caliories - (protein_cal + fat_cal)
        carb_g = carb_cal / 4
        ###############################################
        self.protein_cal_per_day = round(protein_cal, 2)
        self.carb_cal_per_day = round(carb_cal, 2)
        self.fats_cal_per_day = round(fat_cal, 2)
        print('issssssssssssssue', self.carb_cal_per_day)
        db.session.add(self)
        db.session.commit()
        ###############################################
        caliories_needed = {
            "protein": [protein_g, protein_cal],
            "fats": [fat_g, fat_cal],
            "carbs": [carb_g, carb_cal],
        }
        #self.total_claories_per_day = protein_cal + fat_cal + carb_cal
        return caliories_needed
    
    def cal_per_day_after_goal(self, goal, level, activity):

        user = User.query.get(self.user_id)
        bmr = user.calculate_bmr()
        print('before errrrrrorrr', activity)
        bmr = bmr * self.activity_calc(activity)
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
        self.total_claories_per_day = caliories
        db.session.add(self)
        db.session.commit()
        return caliories
    
    def calculate_currnet_cal(self, food_name):
        print(food_name)

        food = db.session.query(Food).filter(Food.name.like(f'%{food_name}%')).first()
        if food:
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx', food.calories)

            if self.current_protein_cal is None:
                self.current_protein_cal = 0
            if self.current_carb_cal is None:
                self.current_carb_cal = 0
            if self.current_fat_cal is None:
                self.current_fat_cal = 0

            if food.category == 'protein':
                self.current_protein_cal += int(food.calories)
            elif food.category == 'carb':
                self.current_carb_cal += int(food.calories)
            else:
                self.current_fat_cal += int(food.calories)
            return self.current_protein_cal, self.current_carb_cal, self.current_fat_cal
        else:
            return None
        
    def update_user_daily_goal_cal(self, calories, seperate):
        
        self.total_claories_per_day = calories
        self.protein_cal_per_day = round(seperate.get('protein')[1],2)
        self.fats_cal_per_day = round(seperate.get('fats')[1],2)

        self.carb_cal_per_day = round(seperate.get('carbs')[1],2)
        print('updateeeeeeeeeeeeeeeeeeeeeeeed')
        db.session.add(self)
        db.session.commit()
        print(self.carb_cal_per_day)

    def update_user_current_cal(self, calories, category):
        self.total_claories_per_day -= calories
        if category == 'protein':
            self.current_protein_cal += calories
        elif category == 'carb':
            self.current_carb_cal += calories
        else:
            self.current_fat_cal += calories
        
        db.session.add(self)
        db.session.commit()
        return int(self.total_claories_per_day), self.current_protein_cal, self.current_carb_cal, self.current_fat_cal






