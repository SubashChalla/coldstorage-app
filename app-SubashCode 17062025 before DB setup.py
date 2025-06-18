from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import re
import requests
import os
import datetime

from functools import wraps
from flask import abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user['username']:
            abort(401, description="Authentication required")
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user['role'] or current_user['role'] not in roles:
                abort(403, description=f"Access denied. Required role: {', '.join(roles)}")
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Usage shortcuts
admin_required = role_required('admin')
manager_required = role_required('admin', 'manager')
can_operate_stock = role_required('admin', 'manager','staff')
## can_deliver_stock = role_required('admin', 'manager', 'staff')

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------- Stock Records --------------------
stocks = []
stock_id_counter = 1

# -------------------- Stock Acceptance Routine --------------------
@app.route('/stocks/accept', methods=['POST'])
@can_operate_stock
def accept_stock():
    global stock_id_counter
    data = request.get_json()

    required_fields = ['commodity', 'variety', 'quantity', 'client_id']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400

    stock_entry = {
        'id': stock_id_counter,
        'action': 'accept',
        'commodity': data['commodity'],
        'variety': data['variety'],
        'quantity': data['quantity'],
        'client_id': data['client_id'],
        'handled_by': current_user['username']
    }
    stocks.append(stock_entry)
    stock_id_counter += 1
    return jsonify({'message': 'Stock accepted', 'stock': stock_entry}), 201

# -------------------- Delivery Records --------------------
deliveries = []
delivery_id_counter = 1


# -------------------- Stock Delivery Routine --------------------
@app.route('/stocks/deliver', methods=['POST'])
@can_operate_stock 
def deliver_stock():
    global delivery_id_counter
    data = request.get_json()

    required_fields = ['client_id', 'commodity_code', 'variety', 'quantity', 'delivered_by']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    delivery = {
        'id': delivery_id_counter,
        'client_id': data['client_id'],
        'commodity_code': data['commodity_code'],
        'variety': data['variety'],
        'quantity': data['quantity'],
        'delivered_by': data['delivered_by'],
        'timestamp': datetime.datetime.now().isoformat()
    }

    deliveries.append(delivery)
    delivery_id_counter += 1
    return jsonify({'message': 'Stock delivered', 'delivery': delivery}), 201

# -------------------- View Stock Delivery Routine (for Admins/Managers)--------------------
@app.route('/stocks/deliveries', methods=['GET'])
@manager_required
def list_deliveries():
    return jsonify({'deliveries': deliveries})


# ----------------------- Users & Roles -----------------------

# Simulated session for now
current_user = {'username': None, 'role': None}

# In-memory user storage
users = []
user_id_counter = 1

# Sample admin user (username: admin, password: admin123)
users.append({
    'id': 0,
    'username': 'admin',
    'password_hash': generate_password_hash('admin123'),
    'role': 'admin'
})

# ----------------------- Admin Creates Users -----------------------

@app.route('/users', methods=['POST'])
@admin_required
def create_user():
    global user_id_counter
    data = request.get_json()

    # Assume this route is protected by an @admin_required decorator later
    required_fields = ['username', 'password', 'role']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if any(user['username'] == data['username'] for user in users):
        return jsonify({'error': 'Username already exists'}), 400

    new_user = {
        'id': user_id_counter,
        'username': data['username'],
        'password_hash': generate_password_hash(data['password']),
        'role': data['role'].lower()
    }
    users.append(new_user)
    user_id_counter += 1
    return jsonify({'message': 'User created', 'user': {'id': new_user['id'], 'username': new_user['username'], 'role': new_user['role']}}), 201

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------- Register User -----------------------

@app.route('/register', methods=['POST'])
@admin_required
def register_user():
    data = request.get_json()

    if not data.get('username') or not data.get('password') or not data.get('role'):
        return jsonify({'error': 'Missing username, password, or role'}), 400

    # Simulate admin check (basic logic for now)
    requesting_user = users[0]  # <-- simulate current user is always admin (for testing)
    if requesting_user['role'] != 'admin':
        return jsonify({'error': 'Only admins can create users.'}), 403

    for u in users:
        if u['username'] == data['username']:
            return jsonify({'error': 'Username already exists.'}), 400

    new_user = {
        'username': data['username'],
        'password_hash': generate_password_hash(data['password']),
        'role': data['role']
    }
    users.append(new_user)
    return jsonify({'message': 'User created.', 'user': {'username': new_user['username'], 'role': new_user['role']}})

# ----------------------- Login -----------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = next((u for u in users if u['username'] == username), None)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    current_user['username'] = user['username']
    current_user['role'] = user['role']

    # For simplicity, just returning the role here — use tokens in production
    return jsonify({'message': 'Login successful', 'username': user['username'], 'role': user['role']}), 200

# ----------------------- Add Clients -----------------------

clients = []
client_id_counter = 1

@app.route('/api/states', methods=['GET'])
def get_indian_states():
    url = "https://api.countrystatecity.in/v1/countries/IN/states"
    headers = {
        "X-CSCAPI-KEY": os.getenv("CSC_API_KEY")
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        state_names = [state['name'] for state in response.json()]
        return jsonify(states=state_names)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities', methods=['GET'])
def get_cities_by_state():
    state_code = request.args.get('state_code')
    if not state_code:
        return jsonify({'error': 'Missing state_code parameter'}), 400
    url = f"https://api.countrystatecity.in/v1/countries/IN/states/{state_code}/cities"
    headers = {"X-CSCAPI-KEY": os.getenv("CSC_API_KEY")}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        city_names = [city['name'] for city in response.json()]
        return jsonify(cities=city_names)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

def is_valid_phone(number):
    return number and number.isdigit() and len(number) == 10

def capitalize_words(s):
    return ' '.join(word.capitalize() for word in s.split())

def format_fields(data):
    for field in ['first_name', 'last_name', 's_o', 'address', 'village', 'mandal', 'district', 'state', 'org_name']:
        if field in data and data[field]:
            data[field] = capitalize_words(data[field])
    return data

def is_duplicate(data):
    for client in clients:
        if client['phone'] == data.get('phone'):
            return 'Phone number already exists.'
        if client.get('email') and client['email'] == data.get('email'):
            return 'Email address already exists.'
        if (client['first_name'].lower() == data.get('first_name', '').lower() and
            client['last_name'].lower() == data.get('last_name', '').lower()):
            return 'Client with this first and last name already exists.'
        if client.get('org_name') and data.get('org_name') and \
           client['org_name'].lower() == data['org_name'].lower():
            return 'Client with this organization name already exists.'
    return None

@app.route('/clients', methods=['POST'])
@manager_required
def add_client():
    global client_id_counter
    data = request.get_json()

    required = ['first_name', 'last_name', 'client_type', 'village', 'mandal', 'phone']
    missing = [field for field in required if not data.get(field)]
    if missing:
        return {'error': f"Missing fields: {', '.join(missing)}"}, 400

    if data.get('client_type') == 'Farmer' and not data.get('s_o'):
        return {'error': 'S/o is required for Farmer type clients.'}, 400

    if data.get('client_type') == 'Farmer':
        data['org_name'] = f"{data.get('first_name', '')} {data.get('last_name', '')}"
    elif not data.get('org_name'):
        return {'error': 'Organization name is required for Trader clients.'}, 400

    error = is_duplicate(data)
    if error:
        return {'error': error}, 400

    if not is_valid_phone(data['phone']):
        return {'error': 'Phone must be a 10-digit number.'}, 400
    if data.get('alt_phone') and not is_valid_phone(data['alt_phone']):
        return {'error': 'Alt Phone must be a 10-digit number.'}, 400
    if data.get('pincode') and (not data['pincode'].isdigit() or len(data['pincode']) != 6):
        return {'error': 'Pincode must be a 6-digit number.'}, 400
    if data.get('email'):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return {'error': 'Email is not valid.'}, 400

    format_fields(data)

    new_client = {
        'id': client_id_counter,
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'client_type': data['client_type'],
        'org_name': data['org_name'],
        's_o': data.get('s_o'),
        'address': data.get('address'),
        'village': data.get('village'),
        'mandal': data.get('mandal'),
        'district': data.get('district'),
        'state': data.get('state'),
        'pincode': data.get('pincode'),
        'phone': data['phone'],
        'alt_phone': data.get('alt_phone'),
        'email': data.get('email')
    }

    clients.append(new_client)
    client_id_counter += 1
    return {'client': new_client}, 201

# ----------------------- Edit Clients -----------------------

@app.route('/clients/<int:client_id>', methods=['PUT'])
@manager_required
def update_client(client_id):
    data = request.get_json()
    format_fields(data)

    if data.get('phone') and not is_valid_phone(data['phone']):
        return {'error': 'Phone must be a 10-digit number.'}, 400
    if data.get('alt_phone') and not is_valid_phone(data['alt_phone']):
        return {'error': 'Alt Phone must be a 10-digit number.'}, 400
    if data.get('pincode') and (not data['pincode'].isdigit() or len(data['pincode']) != 6):
        return {'error': 'Pincode must be a 6-digit number.'}, 400
    if data.get('email'):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return {'error': 'Email is not valid.'}, 400

    if data.get('client_type') == 'Farmer':
        data['org_name'] = f"{data.get('first_name', '')} {data.get('last_name', '')}"

    for client in clients:
        if client['id'] == client_id:
            for field in client:
                if field in data:
                    client[field] = data[field]
            return {'client': client}
    return {'error': 'Client not found'}, 404

@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(clients=clients)

@app.route('/clients/search', methods=['GET'])
def search_clients():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return {'clients': []}
    fields = ['first_name', 'last_name', 's_o', 'org_name', 'village', 'mandal', 'phone']
    matched = [c for c in clients if any(query in str(c.get(f, '')).lower() for f in fields)]
    return {'clients': matched}

# ----------------------- Delete Clients -----------------------

@app.route('/clients/<int:client_id>', methods=['DELETE'])
@manager_required
def delete_client(client_id):
    global clients
    clients = [c for c in clients if c['id'] != client_id]
    return {'message': 'Client deleted'}

if __name__ == '__main__':
    app.run(debug=True)
