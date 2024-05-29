from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message='User registered successfully'), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify(token=token)
    return jsonify(message='Invalid credentials'), 401

@app.route('/services', methods=['GET', 'POST'])
@jwt_required(optional=True)
def services():
    if request.method == 'GET':
        services = Service.query.all()
        return render_template('services.html', services=services)
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if user.role != 'provider':
        return jsonify(message='Access denied'), 403

    new_service = Service(
        provider_id=user.id,
        name=data['name'],
        description=data['description'],
        price=data['price']
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify(message='Service added successfully'), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
