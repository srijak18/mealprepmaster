from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm
from flask import session



bp = Blueprint('auth', __name__)
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask_login import login_user

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            diet_type=form.diet_type.data,
            cuisine=form.cuisine.data
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)  # ✅ make sure this is present
        flash('Registration successful! Welcome.', 'success')

        return redirect(url_for('dashboard.home'))  # ✅ ensures redirect

    # ✅ Optional: log form errors to debug failed validation
    print(form.errors)

    return render_template('register.html', form=form)



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard.home'))  # ✅ Go to dashboard
        flash('Invalid login. Please register first.', 'warning')
        return redirect(url_for('auth.register'))

    return render_template('login.html', form=form)



@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
