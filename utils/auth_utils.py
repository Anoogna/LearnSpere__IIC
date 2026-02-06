"""
Authentication utility functions
Handles JWT token generation and validation
"""
import jwt
from datetime import datetime, timedelta
import os
from functools import wraps
from flask import request, jsonify, session

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
TOKEN_EXPIRATION_HOURS = 24

def generate_token(username):
    """Generate JWT token for user"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token and return username"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        # Check cookies
        if not token and 'auth_token' in request.cookies:
            token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        username = verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.username = username
        return f(*args, **kwargs)
    
    return decorated

def require_login(f):
    """Decorator to require login (stored in session)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Login required'}), 401
        request.username = session['username']
        return f(*args, **kwargs)
    
    return decorated
