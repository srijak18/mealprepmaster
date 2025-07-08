from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.models import Recipe


bp = Blueprint('recipes', __name__, url_prefix='/recipes')

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        recipe = Recipe(title=title, ingredients=ingredients, instructions=instructions, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe added!', 'success')
        return redirect(url_for('recipes.view_recipes'))

    return render_template('add_recipe.html')

@bp.route('/view')
@login_required
def view_recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    return render_template('view_recipes.html', recipes=recipes)

@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        results = Recipe.query.filter(Recipe.title.ilike(f'%{query}%'),
                                      Recipe.user_id == current_user.id).all()
    return render_template('search_recipe.html', results=results)

@bp.route('/delete/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.filter_by(id=recipe_id, user_id=current_user.id).first()
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
        flash("Recipe deleted successfully.", "success")
    else:
        flash("Recipe not found or unauthorized.", "danger")
    return redirect(url_for('recipes.view_recipes'))

@bp.route('/toggle_favorite/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Ensure only the owner can toggle favorite status
    if recipe.user_id != current_user.id:
        abort(403)

    # Toggle favorite status
    recipe.is_favorite = not recipe.is_favorite
    db.session.commit()

    # Flash appropriate message
    if recipe.is_favorite:
        flash("Recipe added to favorites.", "success")
    else:
        flash("Recipe removed from favorites.", "info")

    # Redirect back safely
    return redirect(request.referrer or url_for('recipes.view_recipes'))

@bp.route('/favorites')
@login_required
def favorites():
    favs = Recipe.query.filter_by(user_id=current_user.id, is_favorite=True).all()
    return render_template('favorites.html', recipes=favs)

@bp.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    content = request.form.get('content', '')
    title = request.form.get('title')

    # Fallbacks in case parsing fails
    ingredients = ''
    instructions = ''

    # Basic parsing logic from Gemini format
    # Expected format:
    # Title: ...
    # Ingredients: ...
    # Instructions: ...
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.lower().startswith("ingredients:"):
            ingredients = line[len("ingredients:"):].strip()
            # Attempt to include any list below the line
            for j in range(i + 1, len(lines)):
                if lines[j].lower().startswith("instructions:"):
                    break
                ingredients += "\n" + lines[j]
        elif line.lower().startswith("instructions:"):
            instructions = line[len("instructions:"):].strip()
            # Capture multi-line instructions
            for j in range(i + 1, len(lines)):
                instructions += "\n" + lines[j]

    # Store the recipe
    recipe = Recipe(
        user_id=current_user.id,
        title=title,
        ingredients=ingredients.strip(),
        instructions=instructions.strip(),
        diet_type=current_user.diet_type,
        cuisine=current_user.cuisine
    )
    db.session.add(recipe)
    db.session.commit()
    flash("Recipe saved successfully!", "success")
    return redirect(url_for('recipes.view_recipes'))
