from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import requests
import os
from app import db
from app.models import MealPlan, Recipe, NutritionTip

bp = Blueprint('ai', __name__, url_prefix='/ai')

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RESTRICTED_INGREDIENTS = {
    "vegetarian": ["chicken", "meat", "beef", "mutton", "fish", "prawns", "egg", "eggs", "bacon", "lamb", "sausage"],
    "vegan": ["chicken", "meat", "beef", "fish", "egg", "milk", "cheese", "butter", "yogurt", "cream", "honey"],
    "non_vegetarian": [],
    "keto": ["sugar", "bread", "rice", "pasta", "potato", "banana", "mango", "sweet", "cake", "soda", "juice",
             "soft drinks", "ice cream", "corn", "wheat", "oats", "beans", "lentils", "chickpeas"],
    "paleo": ["bread", "pasta", "rice", "dairy", "cheese", "butter", "yogurt", "cream", "sugar", "processed",
              "soy", "beans", "lentils", "peanuts", "corn", "refined", "grains"]
}

def call_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GOOGLE_API_KEY}", json=data, headers=headers)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error from Gemini API: {e}"

@bp.route('/suggest', methods=['GET', 'POST'])
@login_required
def suggest():
    suggestions = ""
    error = None
    ingredients = ""
    recipe_name = ""
    generated = False

    # Prepare weekly plan
    mealplans = MealPlan.query.filter_by(user_id=current_user.id).all()
    weekly_plan = {day: {"breakfast": None, "lunch": None, "snack": None, "dinner": None} for day in
                   ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    for plan in mealplans:
        recipe = Recipe.query.get(plan.recipe_id)
        if recipe:
            weekly_plan[plan.day][plan.meal_type] = recipe.title

    if request.method == 'POST':
        ingredients = request.form.get('ingredients', '').lower().strip()
        recipe_name = request.form.get('recipe_name', '').lower().strip()
        meal_type = request.form.get('meal_type', '').lower()
        user_diet = (current_user.diet_type or "").lower()
        banned = RESTRICTED_INGREDIENTS.get(user_diet, [])

        input_text = ingredients if ingredients else recipe_name

        # Validate against restricted ingredients for both input methods
        if any(word in input_text for word in banned):
            found = [word for word in banned if word in input_text]
            error = f"As a {user_diet}, your input includes restricted items: {', '.join(found)}"
        else:
            if ingredients:
                prompt = (
                    f"Generate 1 healthy {meal_type} recipe using these ingredients: {ingredients}. "
                    f"Respond in this format:\n"
                    f"Title: ...\nIngredients: ...\nInstructions: ...\n"
                    f"Exclude restricted items for a {user_diet} diet."
                )
            elif recipe_name:
                prompt = (
                    f"Generate a healthy {meal_type} recipe titled '{recipe_name}'. "
                    f"Respond in this format:\n"
                    f"Title: ...\nIngredients: ...\nInstructions: ...\n"
                    f"Ensure it follows a {user_diet} diet and avoids restricted foods."
                )
            else:
                error = "Please provide ingredients or a recipe name."

            if not error:
                suggestions = call_gemini(prompt)
                generated = True

    return render_template(
        'suggestions.html',
        suggestions=suggestions,
        error=error,
        weekly_plan=weekly_plan,
        ingredients=ingredients,
        recipe_name=recipe_name,
        generated=generated
    )


@bp.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '')

    ingredients = ""
    instructions = ""

    # Parse ingredients and instructions from Gemini content
    if "Ingredients:" in content and "Instructions:" in content:
        try:
            parts = content.split("Ingredients:")
            after_ingredients = parts[1].split("Instructions:")
            ingredients = after_ingredients[0].strip()
            instructions = after_ingredients[1].strip()
        except IndexError:
            flash("Failed to parse recipe. Please try again manually.", "danger")
            return redirect(url_for('ai.suggest'))
    else:
        flash("Recipe format not recognized. Please regenerate.", "danger")
        return redirect(url_for('ai.suggest'))

    new_recipe = Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        user_id=current_user.id,
        cuisine=current_user.cuisine or '',
        diet_type=current_user.diet_type or ''
    )

    db.session.add(new_recipe)
    db.session.commit()
    flash("Recipe saved successfully!", "success")
    return redirect(url_for('recipes.view_recipes'))




@bp.route('/tips')
@login_required
def nutrition_tips():
    mealplans = MealPlan.query.filter_by(user_id=current_user.id).all()
    combined_ingredients = []

    # Weekly meal structure for template display
    weekly_plan = {
        day: {'breakfast': None, 'lunch': None, 'dinner': None, 'snack': None}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }

    for plan in mealplans:
        recipe = Recipe.query.get(plan.recipe_id)
        if recipe:
            weekly_plan[plan.day][plan.meal_type] = recipe.title
            combined_ingredients.append(recipe.ingredients)

    if not combined_ingredients:
        flash("No recipes found in your meal plan to analyze.", "warning")
        return render_template('nutrition_tips.html', tips="", weekly_plan=weekly_plan)

    prompt = f"""
    Analyze the following weekly meal plan and give nutrition tips:
    Ingredients: {', '.join(combined_ingredients)}.
    Highlight deficiencies, excesses, and suggest improvements based on a {current_user.diet_type} diet.
    """
    tips = call_gemini(prompt)

    # ✅ Save as a NutritionTip object
    new_tip = NutritionTip(user_id=current_user.id, content=tips)
    db.session.add(new_tip)
    db.session.commit()

    return render_template('nutrition_tips.html', tips=tips, weekly_plan=weekly_plan)
