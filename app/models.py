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
    weight: so.Mapped[int] = so.mapped_column(sa.Float, nullable=False)
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
        
        return bmr


class Body(db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
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
    
    def calculate_bmr(self):

        bmr = self.user.calculate_bmr()
        self.bmr = bmr


class Food(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    calories: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)


class Goal(db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=True)
    goal: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    level: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    fats_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    protein_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    carb_cal_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    total_claories_per_day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    user_id: so.Mapped[int] =  so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='goal')
    created_at: so.Mapped[str] = so.mapped_column(sa.DateTime, default=func.now(), nullable=False)

