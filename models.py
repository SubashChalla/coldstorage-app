# --------- model code for your Flask app using SQLAlchemy. Models imported from here to app.py---------
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    client_type = db.Column(db.String(20), nullable=False)
    org_name = db.Column(db.String(200), nullable=True)
    s_o = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(200))
    village = db.Column(db.String(100), nullable=False)
    mandal = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    phone = db.Column(db.String(15), unique=True, nullable=False)
    alt_phone = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    commodity_code = db.Column(db.String(10), unique=True, nullable=False)
    hsn_code = db.Column(db.String(20))

class Variety(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    commodity_id = db.Column(db.Integer, db.ForeignKey('commodity.id'), nullable=False)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    variety_id = db.Column(db.Integer, db.ForeignKey('variety.id'), nullable=False)


class StockAcceptance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    commodity_code = db.Column(db.String(10), db.ForeignKey('commodity.commodity_code'), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    accepted_by = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class StockDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    commodity_code = db.Column(db.String(10), db.ForeignKey('commodity.commodity_code'), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    delivered_by = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
