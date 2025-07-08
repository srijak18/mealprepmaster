from app import db
from sqlalchemy import Boolean
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    diet_type = db.Column(db.String(50))
    cuisine = db.Column(db.String(50))
    last_nutrition_feedback = db.Column(db.Text, nullable=True)  # ✅ Add this line


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cuisine = db.Column(db.String(50))
    diet_type = db.Column(db.String(50))
    meal_type = db.Column(db.String(50))  # ✅ Add this line
    is_favorite = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    day = db.Column(db.String(20), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # Already supports "snack"
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))


class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item = db.Column(db.String(100))
    category = db.Column(db.String(100))
    checked = db.Column(db.Boolean, default=False)


class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    checked = db.Column(db.Boolean, default=False)

    day = db.Column(db.String(20), nullable=True)         # Monday, etc.
    meal_type = db.Column(db.String(20), nullable=True)   # breakfast, lunch, etc.

    def __repr__(self):
        return f"<ShoppingItem {self.name} ({self.day}-{self.meal_type})>"


from datetime import datetime
from app import db

class NutritionTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='nutrition_tips')
