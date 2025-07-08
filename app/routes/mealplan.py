from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.models import User, MealPlan, Recipe, NutritionTip
from app import db

bp = Blueprint('mealplan', __name__, url_prefix='/mealplan')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def plan():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    # ✅ Fetch recipes filtered by diet type & user ownership, most recent first
    recipes = Recipe.query.filter(
        and_(
            or_(
                Recipe.user_id == current_user.id,
                Recipe.user_id == None
            ),
            Recipe.diet_type == current_user.diet_type
        )
    ).order_by(Recipe.created_at.desc()).all()  # ✅ Most recent recipes first

    if request.method == 'POST':
        for day in days:
            for meal in meal_types:
                field_name = f'{day}_{meal}'
                recipe_id = request.form.get(field_name)
                if recipe_id:
                    recipe_id = int(recipe_id)
                    existing = MealPlan.query.filter_by(user_id=current_user.id, day=day, meal_type=meal).first()
                    if existing:
                        existing.recipe_id = recipe_id
                    else:
                        db.session.add(MealPlan(user_id=current_user.id, day=day, meal_type=meal, recipe_id=recipe_id))
        db.session.commit()
        flash('Meal plan updated!', 'success')
        return redirect(url_for('dashboard.home'))

    mealplans = MealPlan.query.filter_by(user_id=current_user.id).all()
    selected_recipes = {(plan.day, plan.meal_type): str(plan.recipe_id) for plan in mealplans}

    # ✅ Fetch user's nutrition tips (most recent first)
    nutrition_tips = NutritionTip.query.filter_by(user_id=current_user.id).order_by(NutritionTip.created_at.desc()).all()

    return render_template(
        'mealplanner.html',
        days=days,
        meal_types=meal_types,
        recipes=recipes,
        selected_recipes=selected_recipes,
        nutrition_tips=nutrition_tips
    )
