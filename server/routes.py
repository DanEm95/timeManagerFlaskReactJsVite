from app import app, db, login_manager
from flask import request, jsonify
from models import Users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from functools import wraps


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return error message with 403 error
        if current_user.id != 1:
            return jsonify({'error': 'You are not an Administrator'}), 403
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    return jsonify([user.to_json() for user in users]), 200


# Create a user
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
      # Validate request
      required_fields = ['email', 'password']
      for field in required_fields:
        if not request.json or field not in request.json:
          return jsonify({'error': 'Please provide all required fields'}), 400

      user = Users.query.filter_by(email=request.json['email']).first()
      if user:
        return jsonify({'error': 'Email already exists'}), 400

      data = request.get_json()

      email = data['email']
      password = data['password']

      hash_and_salted_password = generate_password_hash(
          password,
          method='pbkdf2:sha256',
          salt_length=8
      )

      new_user = Users(email=email, password=hash_and_salted_password)

      db.session.add(new_user)
      db.session.commit()
      return jsonify(new_user.to_json()), 201
    
    except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500


# Delete a user, admin only
@app.route('/api/users/<int:id>', methods=['DELETE'])
@admin_only
def delete_user(id):
    user = Users.query.get(id)
    try:
      if user is None:
          return jsonify({'error': 'User not found'}), 404

      db.session.delete(user)
      db.session.commit()
      return jsonify({'msg': 'User deleted'}), 200
  
    except Exception as e:
       db.session.rollback()
       return jsonify({'error': str(e)}), 500


# Update a user
@app.route('/api/users/<int:id>', methods=['PATCH'])
def update_user(id):
    user = Users.query.get(id)
    try:
      if user is None:
          return jsonify({'error': 'User not found'}), 404

      data = request.get_json()

      if 'email' in data:
          user.email = data['email']
      if 'password' in data:
          user.password = generate_password_hash(
          data['password'],
          method='pbkdf2:sha256',
          salt_length=8
      )

      db.session.commit()
      return jsonify(user.to_json()), 200

    except Exception as e:
      db.session.rollback()
      return jsonify({'error': str(e)}), 500



# Login a user
@app.route('/api/login', methods=['POST'])
def login():
    try:
      # Validate request
      required_fields = ['email', 'password']
      for field in required_fields:
        if not request.json or field not in request.json:
          return jsonify({'error': 'Please provide all required fields'}), 400

      user = Users.query.filter_by(email=request.json['email']).first()
      if user is None:
        return jsonify({'error': 'User not found'}), 404

      if check_password_hash(user.password, request.json['password']):
        login_user(user)
        return jsonify({'msg': 'Login successful'}), 200
      else:
        return jsonify({'error': 'Invalid password'}), 400

    except Exception as e:
      return jsonify({'error': str(e)}), 500


# Logout a user
@app.route('/api/logout', methods=['POST'])
def logout():
  logout_user()
  return jsonify({'msg': 'Logout successful'}), 200
