# app.py
from flask import (
    Flask, render_template
    )
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


@app.route('/')
def index():  
    return render_template('index.html')

@app.route('/wish-list')
def wish():  
    return render_template('wish.html')

@app.route('/basket')
def basket():  
    return render_template('basket.html')

@app.route('/user')
def user():  
    return render_template('user.html')

@app.route('/order')
def order():  
    return render_template('order.html')


if __name__ == '__main__':
    app.run(debug=True)
