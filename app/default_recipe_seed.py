from app import db
from app.models import Recipe

# Define all possible combinations of diet_type, cuisine, and meal_type
combinations = [
    ("vegetarian", "Indian", "breakfast", "Vegetarian Idli", "rice, urad dal, chutney", "Ferment and steam idli batter, serve with chutney."),
    ("vegetarian", "Italian", "lunch", "Margherita Pizza", "flour, tomatoes, mozzarella, basil", "Bake pizza with all toppings."),
    ("vegetarian", "American", "dinner", "Tofu Stir Fry", "tofu, vegetables, soy sauce", "Stir fry tofu and veggies."),
    ("vegetarian", "Mexican", "snack", "Veggie Tacos", "tortilla, beans, veggies", "Stuff tortillas with vegetables and beans."),
    ("vegetarian", "Chinese", "lunch", "Vegetable Chow Mein", "noodles, cabbage, carrots, soy sauce", "Boil noodles, stir-fry with vegetables and sauce."),

    ("vegan", "Indian", "breakfast", "Vegan Poha", "flattened rice, mustard seeds, turmeric", "Cook with spices and veggies."),
    ("vegan", "Italian", "lunch", "Vegan Spaghetti", "spaghetti, tomato, garlic", "Boil spaghetti, sauté with tomato sauce."),
    ("vegan", "American", "dinner", "Vegan Sushi", "rice, nori, avocado", "Roll all and slice."),
    ("vegan", "Mediterranean", "snack", "Vegan Hummus Plate", "hummus, veggies, olives", "Serve as a dip with veggies."),
    ("vegan", "Chinese", "dinner", "Tofu Veg Stir Fry", "tofu, bell pepper, soy sauce", "Stir fry with tofu and Chinese sauce."),

    ("non_vegetarian", "Indian", "breakfast", "Chicken Keema Paratha", "chicken, wheat flour, spices", "Stuff and cook paratha."),
    ("non_vegetarian", "Mexican", "lunch", "Chicken Enchiladas", "chicken, tortillas, cheese", "Roll, bake with sauce."),
    ("non_vegetarian", "Italian", "dinner", "Chicken Alfredo Pasta", "pasta, chicken, cream", "Cook pasta and mix with chicken alfredo."),
    ("non_vegetarian", "American", "snack", "Chicken Satay", "chicken, peanut sauce", "Grill and serve with sauce."),
    ("non_vegetarian", "Chinese", "dinner", "Szechuan Chicken", "chicken, chili sauce, garlic", "Stir fry with Chinese Szechuan sauce."),

    ("keto", "Indian", "breakfast", "Keto Paneer Bhurji", "paneer, spices", "Scramble paneer with spices."),
    ("keto", "Western", "lunch", "Keto Caesar Salad", "lettuce, chicken, parmesan", "Toss and serve cold."),
    ("keto", "Italian", "dinner", "Keto Pizza", "almond flour, cheese, tomato", "Bake pizza with keto crust."),
    ("keto", "Mediterranean", "snack", "Keto Greek Yogurt Dip", "greek yogurt, cucumber, garlic", "Mix and serve chilled."),
    ("keto", "American", "lunch", "Keto Egg Drop Soup", "egg, chicken broth, spring onion", "Whisk egg into boiling broth and stir."),

    ("paleo", "American", "breakfast", "Sweet Potato Pancakes", "sweet potato, eggs", "Mash and cook into pancakes."),
    ("paleo", "American", "lunch", "Paleo Stir Fry", "chicken, veggies, coconut oil", "Stir fry and season."),
    ("paleo", "Mexican", "dinner", "Paleo Taco Bowl", "beef, lettuce, salsa", "Serve ingredients layered in bowl."),
    ("paleo", "Indian", "snack", "Roasted Spiced Nuts", "nuts, spices, ghee", "Roast nuts in ghee with spices."),
    ("paleo", "Chinese", "dinner", "Paleo Ginger Chicken", "chicken, ginger, sesame oil", "Stir fry chicken with ginger and sauce."),
]

def seed_default_recipes():
    for diet_type, cuisine, meal_type, title, ingredients, instructions in combinations:
        exists = Recipe.query.filter_by(title=title, user_id=None).first()
        if not exists:
            db.session.add(Recipe(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                cuisine=cuisine,
                diet_type=diet_type,
                meal_type=meal_type,
                user_id=None  # Global default
            ))
    db.session.commit()
    print("✅ Default recipes seeded with all diet and cuisine combinations.")
