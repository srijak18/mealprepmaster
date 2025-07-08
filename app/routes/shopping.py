from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import MealPlan, Recipe, ShoppingItem
from app import db

bp = Blueprint('shopping', __name__, url_prefix='/shopping')

@bp.route('/generate')
@login_required
def generate_list():
    mealplans = MealPlan.query.filter_by(user_id=current_user.id).all()
    all_ingredients = []

    for plan in mealplans:
        recipe = Recipe.query.get(plan.recipe_id)
        if recipe and recipe.ingredients:
            ingredients = [item.strip() for item in recipe.ingredients.split(',')]
            all_ingredients.extend(ingredients)

    # ✅ Weekly shopping grouped by day/meal
    weekly_shopping = {}
    for plan in mealplans:
        recipe = Recipe.query.get(plan.recipe_id)
        if not recipe or not recipe.ingredients:
            continue

        ingredients = [item.strip() for item in recipe.ingredients.split(',')]
        day = plan.day
        meal = plan.meal_type

        if day not in weekly_shopping:
            weekly_shopping[day] = {}
        if meal not in weekly_shopping[day]:
            weekly_shopping[day][meal] = []

        weekly_shopping[day][meal].extend(ingredients)

    categories = {
        "produce": ["tomato", "onion", "potato", "carrot", "spinach", "lettuce", "apple", "banana", "cucumber"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "paneer", "cream"],
        "protein": ["chicken", "egg", "eggs", "tofu", "beef", "mutton", "fish", "lentils", "beans", "chickpeas"],
        "grains": ["rice", "bread", "wheat", "pasta", "flour", "semolina", "oats", "corn"],
        "spices & condiments": ["salt", "pepper", "turmeric", "oil", "vinegar", "soy sauce", "chili", "garlic", "ginger"],
        "others": []
    }

    grouped = {cat: [] for cat in categories}

    for item in all_ingredients:
        item_lower = item.lower()
        matched = False
        for cat, keywords in categories.items():
            if any(word in item_lower for word in keywords):
                grouped[cat].append(item)
                matched = True
                break
        if not matched:
            grouped["others"].append(item)

        # Save item in DB if not present
        if not ShoppingItem.query.filter_by(user_id=current_user.id, name=item).first():
            db.session.add(ShoppingItem(user_id=current_user.id, name=item))

    db.session.commit()

    # Checked status mapping
    checked_map = {
        item.name: item.checked
        for item in ShoppingItem.query.filter_by(user_id=current_user.id).all()
    }

    return render_template("shopping_list.html", grouped_items=grouped, checked_map=checked_map)


# ✅ Toggle checked status via AJAX
@bp.route('/toggle_check', methods=['POST'])
@login_required
def toggle_check():
    data = request.get_json()
    item_name = data.get('item')
    is_checked = data.get('checked', False)

    item = ShoppingItem.query.filter_by(user_id=current_user.id, name=item_name).first()
    if item:
        item.checked = is_checked
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Item not found"}), 404

# Clear all checked items for current user
@bp.route('/clear_checked', methods=['POST'])
@login_required
def clear_checked():
    items = ShoppingItem.query.filter_by(user_id=current_user.id, checked=True).all()
    for item in items:
        item.checked = False
    db.session.commit()
    return jsonify({"cleared": True})
