from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

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

@app.route('/clients/<int:client_id>', methods=['PUT'])
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

@app.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    global clients
    clients = [c for c in clients if c['id'] != client_id]
    return {'message': 'Client deleted'}

if __name__ == '__main__':
    app.run(debug=True)
