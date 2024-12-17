# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Database initialization/Create tables before the app runs
with app.app_context():
    db.create_all()
    
    
# Routes
@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:id>')
def view_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipe.html', recipe=recipe)

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    data = request.json
    new_recipe = Recipe(name=data['name'], ingredients=data['ingredients'], steps=data['steps'])
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message": "Recipe added successfully!"})

@app.route('/update_recipe/<int:id>', methods=['PUT'])
def update_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    data = request.json
    recipe.name = data['name']
    recipe.ingredients = data['ingredients']
    recipe.steps = data['steps']
    db.session.commit()
    return jsonify({"message": "Recipe updated successfully!"})

@app.route('/delete_recipe/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe deleted successfully!"})

@app.route('/favorite/<int:id>', methods=['POST'])
def toggle_favorite(id):
    recipe = Recipe.query.get_or_404(id)
    recipe.is_favorite = not recipe.is_favorite
    db.session.commit()
    return jsonify({"message": "Favorite status updated!"})

@app.route('/order/<int:id>', methods=['POST'])
def order_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    new_order = OrderHistory(recipe_id=recipe.id)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Recipe ordered successfully!"})

@app.route('/history')
def order_history():
    history = OrderHistory.query.join(Recipe).add_columns(Recipe.name, OrderHistory.timestamp).all()
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)
