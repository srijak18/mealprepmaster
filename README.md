# 🍽️ MealPrepMaster

MealPrepMaster is a smart meal planning web application built using **Flask**, **Bootstrap**, and **SQLAlchemy**. It provides users with features like recipe management, AI-powered suggestions, nutrition tips, smart shopping lists, and a personalized dashboard experience.

---

## 🚀 Features

- 👤 User authentication & profile management
- 🍛 Recipe generation based on preferences (via Gemini AI)
- 🧠 Weekly meal planner with dropdown-based selection
- 📋 Grouped smart shopping list with checkbox tracking
- 📝 Nutrition tips & note archive
- 🧾 PDF download & clipboard copy for shopping lists
- 🌙 Dark mode toggle (persistent using `localStorage`)
- 📱 Mobile-friendly responsive layout

---

## 📁 Project Structure
app/
│
├── templates/ # HTML templates (Jinja2)
│ ├── base.html
│ ├── home.html
│ ├── profile.html
│ ├── mealplanner.html
│ ├── change_password.html
│ ├── dashboard.html
│ ├── edit_preferences.html
│ ├── favorites.html
│ ├── login.html
│ ├── nutrition_tips.html
│ ├── register.html
│ ├── search_recipe.html
│ ├── shopping_list.html
│ ├── suggestions.html
│ ├── view_recipes.html
│ └── add_recipe.html
│
├── static/
│ ├── css/
│ │ └── styles.css
│ ├── images/
│ │ └── chef-thinking.png
│ └── uploads/ # User-uploaded profile images
│
├── models.py # SQLAlchemy models
├── routes/
│ ├── auth.py
│ ├── dashboard.py
│ ├── mealplan.py
│ ├── shopping.py
│ ├── home.py
│ ├── recipes.py
│ └── ai.py
│
├── utils/
│ ├── gemini.py
│ 
├── init.py # App initialization
├── docker-compose.yml
├── config.py
├── forms.py
├── default_recipe_seed.py
├── .env #have your API key
└── run.py

#To initiate your postgresql
docker-compose up -d
docker ps

# To run 
python run.py
