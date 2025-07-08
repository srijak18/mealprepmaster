from app import create_app
from app.default_recipe_seed import seed_default_recipes  # adjust if your seed file is inside /app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        seed_default_recipes()  # ✅ this now runs inside the Flask app context
    app.run(debug=True)
