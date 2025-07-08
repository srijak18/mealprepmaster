from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
import os
from datetime import datetime
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.models import MealPlan, Recipe, User


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def home():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meal_types = ['breakfast', 'lunch', 'snack', 'dinner']
    weekly_plan = {day: {meal: None for meal in meal_types} for day in days}
    weekly_favorites = {}

    mealplans = MealPlan.query.filter_by(user_id=current_user.id).all()

    for plan in mealplans:
        recipe = Recipe.query.get(plan.recipe_id)
        if recipe:
            weekly_plan[plan.day][plan.meal_type] = recipe.title
            weekly_favorites[(plan.day, plan.meal_type)] = recipe.is_favorite

    flagged_keywords = ["high in sugar", "low in fiber", "too much sodium"]
    highlighted = []

    if current_user.last_nutrition_feedback:
        for kw in flagged_keywords:
            if kw in current_user.last_nutrition_feedback.lower():
                highlighted.append(kw)

# Then in the template, flag meals with 💡 or ⚠️

    return render_template('dashboard.html',
                           weekly_plan=weekly_plan,
                           highlighted=highlighted,
                           weekly_favorites=weekly_favorites)


@bp.route('/edit_preferences', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    if request.method == 'POST':
        current_user.diet_type = request.form['diet_type']
        current_user.cuisine = request.form['cuisine']
        db.session.commit()
        flash("Preferences updated!", "success")
        return redirect(url_for('dashboard.home'))

    return render_template('edit_preferences.html',
                           selected_diet=current_user.diet_type,
                           selected_cuisine=current_user.cuisine)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        password = request.form['password']
        if not check_password_hash(current_user.password, password):
            flash("Incorrect password. Changes not saved.", "danger")
            return redirect(url_for('dashboard.profile'))

        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.diet_type = request.form['diet_type']
        current_user.cuisine = request.form['cuisine']

        if 'profile_image' in request.files:
            image = request.files['profile_image']
            if image and image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join('app/static/uploads', filename))
                current_user.profile_image = filename
                User.profile_image = filename
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard.profile'))

    return render_template('profile.html', user=current_user, timestamp=int(datetime.utcnow().timestamp()))


from werkzeug.security import check_password_hash, generate_password_hash

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form['current_password']
    new_pw = request.form['new_password']
    confirm_pw = request.form['confirm_password']

    if not check_password_hash(current_user.password, current_pw):
        flash("Current password is incorrect", "danger")
    elif new_pw != confirm_pw:
        flash("New passwords do not match", "danger")
    else:
        current_user.password = generate_password_hash(new_pw)
        db.session.commit()
        flash("Password changed successfully!", "success")

    return redirect(url_for('dashboard.profile'))


@bp.route('/mealplan/edit', methods=['GET', 'POST'])
@login_required
def edit_mealplan():
    # Filter recipes based on user preferences
    preferred_recipes = Recipe.query.filter_by(
        diet_type=current_user.diet_type,
        cuisine=current_user.cuisine
    ).all()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_options = {
    day: {'breakfast': '', 'lunch': '', 'dinner': '', 'snack': ''} for day in days
}

    if request.method == 'POST':
        # handle form submission to save meal plan
        flash("Meal plan saved successfully!", "success")
        return redirect(url_for('dashboard.home'))

    return render_template('mealplanner.html', days=days, meal_options=meal_options, recipes=preferred_recipes)
