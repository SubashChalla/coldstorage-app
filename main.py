from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Commodity, Variety, Grade
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coldstorage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# ----------------------------- HELPERS -----------------------------

def is_valid_phone(number):
    return number and number.isdigit() and len(number) == 10

def capitalize_words(s):
    return ' '.join(word.capitalize() for word in s.split())

def get_current_user():
    username = request.headers.get('X-Username')
    return User.query.filter_by(username=username).first()

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user or user.role not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ----------------------------- MODELS -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    client_type = db.Column(db.String(20), nullable=False)
    org_name = db.Column(db.String(120), nullable=False)
    s_o = db.Column(db.String(100))
    address = db.Column(db.String(200))
    village = db.Column(db.String(100))
    mandal = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    phone = db.Column(db.String(10), unique=True, nullable=False)
    alt_phone = db.Column(db.String(10))
    email = db.Column(db.String(100), unique=True)

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hsn_code = db.Column(db.String(20), nullable=True)
    varieties = db.relationship('Variety', backref='commodity', cascade="all, delete-orphan")

class Variety(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'), nullable=False)
    grades = db.relationship('Grade', backref='variety', cascade="all, delete-orphan")

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    variety_id = db.Column(db.Integer, db.ForeignKey('variety.id'), nullable=False)



class StockAcceptance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    commodity_code = db.Column(db.String(20), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    accepted_by = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False, default=lambda: datetime.now().isoformat())

class StockDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    commodity_code = db.Column(db.String(20), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    delivered_by = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False, default=lambda: datetime.now().isoformat())


# ----------------------------- AUTH ROUTES -----------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'message': 'Login successful', 'username': user.username, 'role': user.role})

@app.route('/users', methods=['POST'])
@role_required('admin')
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'})

#---------------------- Route to bulk upload Commodities - START ------------
@app.route('/bulk_upload_commodities', methods=['POST'])
@role_required('admin')
def bulk_upload_commodities():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of commodities'}), 400

    try:
        for item in data:
            commodity_name = item.get('commodity')
            variety_name = item.get('variety')
            grade_name = item.get('grade')
            hsn_code = item.get('hsn_code')

            if not commodity_name:
                continue  # skip incomplete rows

            # Check or create Commodity
            commodity = Commodity.query.filter_by(name=commodity_name).first()
            if not commodity:
                commodity = Commodity(name=commodity_name, hsn_code=hsn_code)
                db.session.add(commodity)
                db.session.flush()  # get commodity.id

            # Check or create Variety
            variety = None
            if variety_name:
                variety = Variety.query.filter_by(name=variety_name, commodity_id=commodity.id).first()
                if not variety:
                    variety = Variety(name=variety_name, commodity_id=commodity.id)
                    db.session.add(variety)
                    db.session.flush()  # get variety.id

            # Check or create Grade
            if grade_name and variety:
                grade = Grade.query.filter_by(name=grade_name, variety_id=variety.id).first()
                if not grade:
                    grade = Grade(name=grade_name, variety_id=variety.id)
                    db.session.add(grade)

        db.session.commit()
        return jsonify({'message': 'Bulk upload successful'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
#---------------------- Route to bulk upload Commodities - END ------------ 

# ----------------------------- CLIENT ROUTES -----------------------------

@app.route('/clients', methods=['POST'])
@role_required('admin', 'manager')
def add_client():
    data = request.get_json()
    required = ['first_name', 'last_name', 'client_type', 'village', 'mandal', 'phone']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing: {', '.join(missing)}"}), 400

    if data['client_type'] == 'Farmer':
        if not data.get('s_o'):
            return jsonify({'error': 'S/o is required for Farmers'}), 400
        data['org_name'] = f"{data['first_name']} {data['last_name']}"
    elif not data.get('org_name'):
        return jsonify({'error': 'Org Name is required for Traders'}), 400

    new_client = Client(
        first_name=capitalize_words(data['first_name']),
        last_name=capitalize_words(data['last_name']),
        s_o=capitalize_words(data.get('s_o', '')),
        address=capitalize_words(data.get('address', '')),
        village=capitalize_words(data['village']),
        mandal=capitalize_words(data['mandal']),
        district=capitalize_words(data.get('district', '')),
        state=capitalize_words(data.get('state', '')),
        city=capitalize_words(data.get('city', '')),
        pincode=data.get('pincode'),
        phone=data['phone'],
        alt_phone=data.get('alt_phone'),
        email=data.get('email'),
        client_type=data['client_type'],
        org_name=capitalize_words(data['org_name'])
    )

    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client added'})

# ----------------------------- COMMODITY ROUTES -----------------------------

@app.route('/commodities', methods=['POST'])
@role_required('admin')
def create_commodity():
    data = request.get_json()

    name = data.get('name')
    variety_name = data.get('variety')
    grade_name = data.get('grade')
    hsn_code = data.get('hsn_code')

    if not name or not variety_name:
        return jsonify({'error': 'Commodity Name and Variety are required'}), 400

    # Check if commodity exists
    commodity = Commodity.query.filter_by(name=name).first()
    if not commodity:
        commodity = Commodity(name=name, hsn_code=hsn_code)
        db.session.add(commodity)
        db.session.flush()  # Get ID for FK

    # Check if variety exists under this commodity
    variety = Variety.query.filter_by(name=variety_name, commodity_id=commodity.id).first()
    if not variety:
        variety = Variety(name=variety_name, commodity_id=commodity.id)
        db.session.add(variety)
        db.session.flush()

    # If grade is provided, add it under variety
    if grade_name:
        grade = Grade.query.filter_by(name=grade_name, variety_id=variety.id).first()
        if not grade:
            grade = Grade(name=grade_name, variety_id=variety.id)
            db.session.add(grade)

    db.session.commit()
    return jsonify({'message': 'Commodity entry created successfully'}), 201


#---------------GET COMMODITIES--------
@app.route('/commodities/fields', methods=['GET'])
def get_commodities():
    commodities = Commodity.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'hsn_code': c.hsn_code
    } for c in commodities])

@app.route('/commodities/<int:commodity_id>/varieties', methods=['GET'])
def get_varieties_for_commodity(commodity_id):
    varieties = Variety.query.filter_by(commodity_id=commodity_id).all()
    return jsonify([{
        'id': v.id,
        'name': v.name
    } for v in varieties])

@app.route('/varieties/<int:variety_id>/grades', methods=['GET'])
def get_grades_for_variety(variety_id):
    grades = Grade.query.filter_by(variety_id=variety_id).all()
    return jsonify([{
        'id': g.id,
        'name': g.name
    } for g in grades])


# ----------------------------- STOCK ACCEPTANCE -----------------------------

@app.route('/stocks/accept', methods=['POST'])
@role_required('admin', 'manager', 'staff')
def accept_stock():
    data = request.get_json()
    for field in ['client_id', 'commodity_code', 'variety', 'quantity']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    stock = StockAcceptance(
        client_id=data['client_id'],
        commodity_code=data['commodity_code'],
        variety=data['variety'],
        quantity=data['quantity'],
        accepted_by=g.current_user.username
    )
    db.session.add(stock)
    db.session.commit()
    return jsonify({'message': 'Stock accepted'})

# ----------------------------- STOCK DELIVERY -----------------------------

@app.route('/stocks/deliver', methods=['POST'])
@role_required('admin', 'manager')
def deliver_stock():
    data = request.get_json()
    for field in ['client_id', 'commodity_code', 'variety', 'quantity']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    delivery = StockDelivery(
        client_id=data['client_id'],
        commodity_code=data['commodity_code'],
        variety=data['variety'],
        quantity=data['quantity'],
        delivered_by=g.current_user.username
    )
    db.session.add(delivery)
    db.session.commit()
    return jsonify({'message': 'Stock delivered'})

# ----------------------------- MAIN -----------------------------

if __name__ == '__main__':
    app.run(debug=True)
