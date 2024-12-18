

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from flask_migrate import Migrate
# After initializing `db`
migrate = Migrate(app, db)

# Models
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer)
    image = db.Column(db.String)
    categories = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String)
    recipes = db.relationship('Recipe', backref='category', lazy=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database initialization/Create tables before the app runs
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/wish-list')
def wish():  
    return render_template('wish.html')

@app.route('/basket')
def basket():  
    return render_template('basket.html')

@app.route('/user')
def user():  
    return render_template('user.html')

@app.route('/orders')
def order():  
    return render_template('order.html')

@app.route('/products')
def products():  
    return render_template('products.html')

# @app.route('/recipe', methods=['POST', 'GET'])
# def recipe():  

#     data = request.form
#     new_recipe = Recipe(
#         title=data['title'], ingredients=data['ingredients'], steps=data['steps'])
#     db.session.add(new_recipe)
#     db.session.commit()
#     # return jsonify({"message": "Recipe added successfully!"})
        
#     return render_template('crud/save_recipe.html', message="Recipe added successfully!")


# =================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, username=username, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('crud/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password.', 'danger')

    return render_template('crud/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/recipes', methods=['GET', 'POST'])
@login_required
def new_recipe():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        image = request.form['image']
        categories = request.form['categories']
        category_id = request.form['category_id']
        ingredients = request.form['ingredients']
        steps = request.form['steps']

        recipe = Recipe(
            title=title, price=price, image=image, categories=categories,
            category_id=category_id, ingredients=ingredients, steps=steps
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('crud/save_recipe.html', categories=categories)

@app.route('/recipes/<int:id>')
def view_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('view_recipe.html', recipe=recipe)

@app.route('/recipes/<int:id>/delete', methods=['POST'])
@login_required
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('index'))

    
if __name__ == '__main__':
    app.run(debug=True)
