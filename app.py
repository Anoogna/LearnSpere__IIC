#!/usr/bin/env python3
"""
ML Learning Assistant - Main Flask Application
GyanGuru: AI Powered Learning Assistant for AI & ML
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename

# Import utility modules
from utils.genai_utils import get_groq, init_groq
from utils.audio_utils import get_audio, init_audio
from utils.image_utils import get_images, init_images
from utils.code_executor import get_code_executor, init_code_executor
from utils.auth_utils import generate_token, verify_token, token_required, require_login
from models.user import User, ensure_users_file

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS
CORS(app)

# Initialize upload directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/code', exist_ok=True)

# Initialize user data file
ensure_users_file()

# Initialize utility modules
init_groq(os.getenv('GROQ_API_KEY'))
init_audio()
init_images()
init_code_executor()

# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def index():
    """Home page - Dashboard"""
    return render_template('index.html')

@app.route('/text-explanation')
def text_explanation():
    """Text explanation learning page"""
    return render_template('text_explanation.html')

@app.route('/code-generation')
def code_generation():
    """Code generation learning page"""
    return render_template('code_generation.html')

@app.route('/audio-learning')
def audio_learning():
    """Audio learning page"""
    return render_template('audio_learning.html')

@app.route('/image-visualization')
def image_visualization():
    """Image visualization page"""
    return render_template('image_visualization.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/api/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    try:
        # Validate input
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': 'Username must be 3-20 characters'}), 400
        
        # Create user
        User.create(username, email, password)
        
        return jsonify({'success': True, 'message': 'Account created successfully'}), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"[ERROR] Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    try:
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.authenticate(username, password)
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Generate JWT token
        token = generate_token(username)
        
        # Store in session
        session['username'] = username
        session.permanent = True  # Make session persist
        
        return jsonify({
            'success': True, 
            'token': token,
            'username': username,
            'message': 'Login successful'
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    token = request.headers.get('Authorization')
    username = None
    
    if token:
        try:
            username = verify_token(token.split(" ")[1])
        except:
            pass
    
    if not username and 'username' in session:
        username = session['username']
    
    if username:
        return jsonify({'authenticated': True, 'username': username}), 200
    else:
        return jsonify({'authenticated': False}), 200

@app.route('/api/user-profile', methods=['GET'])
@require_login
def user_profile():
    """Get current user profile"""
    username = request.username
    user = User.get_by_username(username)
    
    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'last_login': user.last_login
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# ============================================
# API ROUTES - TEXT EXPLANATION
# ============================================

@app.route('/api/generate-explanation', methods=['POST'])
def generate_explanation():
    """Generate text explanation for ML topic"""
    print("🔥 API HIT: /api/generate-explanation")
    try:
        data = request.get_json()
        print(f"📨 Received data: {data}")
        topic = data.get('topic', '')
        complexity = data.get('complexity', 'Intermediate')
        
        print(f"📝 Topic: {topic}, Complexity: {complexity}")
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        print("🤖 Initializing Groq...")
        gemini = get_groq()
        print("✅ Groq initialized")
        
        print("⏳ Generating explanation...")
        explanation = gemini.generate_text_explanation(topic, complexity)
        print(f"✨ Explanation generated: {explanation[:100]}...")
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'topic': topic,
            'complexity': complexity,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================
# API ROUTES - CODE GENERATION
# ============================================

@app.route('/api/generate-code', methods=['POST'])
def generate_code():
    """Generate Python code for ML concepts"""
    try:
        data = request.get_json()
        algorithm = data.get('algorithm', '')
        complexity = data.get('complexity', 'Detailed')
        
        if not algorithm:
            return jsonify({'error': 'Algorithm is required'}), 400
        
        gemini = get_groq()
        code = gemini.generate_code_example(algorithm, complexity)
        
        # Detect dependencies
        dependencies = get_code_executor().detect_dependencies(code)
        
        # Validate syntax
        is_valid, error = get_code_executor().validate_syntax(code)
        
        # Save code file
        filepath, webpath = get_code_executor().save_code_file(code) or (None, None)
        
        return jsonify({
            'success': True,
            'code': code,
            'algorithm': algorithm,
            'complexity': complexity,
            'dependencies': dependencies,
            'is_valid': is_valid,
            'error': error,
            'download_url': webpath,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/code-execution-guide', methods=['POST'])
def code_execution_guide():
    """Get execution guide for generated code"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        executor = get_code_executor()
        dependencies = executor.detect_dependencies(code)
        guide = executor.create_execution_guide(code, dependencies)
        
        # Create Colab notebook
        colab_code = executor.create_colab_notebook(code, "ML Learning Code")
        
        return jsonify({
            'success': True,
            'guide': guide,
            'dependencies': dependencies,
            'colab_code': colab_code
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API ROUTES - AUDIO GENERATION
# ============================================

@app.route('/api/generate-audio', methods=['POST'])
def generate_audio():
    """Generate audio from text or script"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        topic = data.get('topic', 'lesson')
        audio_type = data.get('type', 'tts')  # 'tts' or 'script'
        
        if not text:
            return jsonify({'error': 'Text content is required'}), 400
        
        audio = get_audio()
        
        if audio_type == 'script':
            filepath, webpath = audio.generate_educational_audio(text, topic)
        else:
            filepath, webpath = audio.generate_audio(text)
        
        if filepath:
            return jsonify({
                'success': True,
                'audio_url': webpath,
                'audio_path': filepath,
                'topic': topic,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-audio-script', methods=['POST'])
def generate_audio_script():
    """Generate audio script from topic"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        length = data.get('length', 'Medium')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        gemini = get_groq()
        script = gemini.generate_audio_script(topic, length)
        
        # Generate audio from script
        audio = get_audio()
        filepath, webpath = audio.generate_educational_audio(script, topic)
        
        return jsonify({
            'success': True,
            'script': script,
            'topic': topic,
            'length': length,
            'audio_url': webpath if filepath else None,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API ROUTES - IMAGE GENERATION
# ============================================

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate educational diagram/image"""
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        diagram_type = data.get('diagram_type', 'Conceptual')
        backend = data.get('backend', 'placeholder')
        
        if not concept:
            return jsonify({'error': 'Concept is required'}), 400
        
        gemini = get_groq()
        prompt = gemini.generate_image_prompt(concept, diagram_type)
        
        images = get_images()
        result = images.generate_image_from_prompt(prompt, use_api=backend)
        
        # If Stable Diffusion fails, fallback to placeholder
        if result is None and backend == 'stable_diffusion':
            print("[WARNING] Stable Diffusion failed, falling back to Smart Diagrams")
            result = images.generate_image_from_prompt(prompt, use_api='placeholder')
        
        if result and len(result) == 2:
            filepath, webpath = result
            return jsonify({
                'success': True,
                'image_url': webpath,
                'concept': concept,
                'diagram_type': diagram_type,
                'prompt': prompt,
                'backend_used': 'placeholder' if backend == 'stable_diffusion' and result else backend,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to generate image'}), 500
    except Exception as e:
        print(f"[ERROR] Error in /api/generate-image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-images-multiple', methods=['POST'])
def generate_images_multiple():
    """Generate multiple diagrams with different types and styles for a concept"""
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        count = min(int(data.get('count', 1)), 5)  # Max 5 images
        
        if not concept:
            return jsonify({'error': 'Concept is required'}), 400
        
        gemini = get_groq()
        images_obj = get_images()
        
        generated_images = []
        diagram_types = ['Conceptual', 'Technical', 'Flowchart']
        
        for i in range(count):
            # Vary diagram type among available options
            diagram_type = diagram_types[i % len(diagram_types)]
            # Vary visual style with variation parameter (0-4)
            variation = i % 5
            
            prompt = gemini.generate_image_prompt(concept, diagram_type)
            # Pass diagram_type to force specific type and variation for visual diversity
            filepath, webpath = images_obj.generate_image_from_prompt(
                prompt, 
                diagram_type=diagram_type,
                variation=variation,
                use_api='placeholder'
            )
            
            if filepath:
                generated_images.append({
                    'image_url': webpath,
                    'diagram_type': diagram_type,
                    'variation': variation,
                    'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt
                })
        
        return jsonify({
            'success': True,
            'images': generated_images,
            'concept': concept,
            'count': len(generated_images),
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API ROUTES - RESOURCE MANAGEMENT
# ============================================

@app.route('/api/list-audio-files', methods=['GET'])
def list_audio_files():
    """List all generated audio files"""
    try:
        audio = get_audio()
        files = audio.list_generated_files()
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-images', methods=['GET'])
def list_images_api():
    """List all generated images"""
    try:
        images = get_images()
        files = images.list_generated_images()
        return jsonify({'success': True, 'images': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-code-files', methods=['GET'])
def list_code_files():
    """List all generated code files"""
    try:
        executor = get_code_executor()
        files = executor.list_generated_code_files()
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_type>/<filename>', methods=['GET'])
def download_file(file_type, filename):
    """Download generated files"""
    try:
        filename = secure_filename(filename)
        
        if file_type == 'audio':
            filepath = os.path.join('uploads/audio', filename)
        elif file_type == 'image':
            filepath = os.path.join('uploads/images', filename)
        elif file_type == 'code':
            filepath = os.path.join('uploads/code', filename)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API ROUTES - COMBINED LEARNING PATH
# ============================================

@app.route('/api/generate-complete-lesson', methods=['POST'])
def generate_complete_lesson():
    """Generate comprehensive lesson with all modalities"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        complexity = data.get('complexity', 'Intermediate')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        gemini = get_groq()
        
        # Generate all content types
        explanation = gemini.generate_text_explanation(topic, complexity)
        code = gemini.generate_code_example(topic, complexity)
        script = gemini.generate_audio_script(topic, "Medium")
        image_prompt = gemini.generate_image_prompt(topic, "Technical")
        
        # Process code
        executor = get_code_executor()
        dependencies = executor.detect_dependencies(code)
        code_valid, code_error = executor.validate_syntax(code)
        code_file = executor.save_code_file(code)
        
        # Generate audio
        audio = get_audio()
        audio_file = audio.generate_educational_audio(script, topic)
        
        # Generate image
        images = get_images()
        image_file = images.generate_image_from_prompt(image_prompt)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'complexity': complexity,
            'explanation': explanation,
            'code': {
                'content': code,
                'dependencies': dependencies,
                'valid': code_valid,
                'download_url': code_file[1] if code_file else None
            },
            'audio': {
                'script': script,
                'download_url': audio_file[1] if audio_file else None
            },
            'image': {
                'prompt': image_prompt,
                'download_url': image_file[1] if image_file else None
            },
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# FILE SERVING
# ============================================

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve files from the uploads directory"""
    try:
        filepath = os.path.join('uploads', filename)
        # Convert to absolute path for checking
        abs_filepath = os.path.abspath(filepath)
        abs_uploads = os.path.abspath('uploads')
        
        # Security check: ensure the file is within uploads directory
        if not abs_filepath.startswith(abs_uploads):
            return jsonify({'error': 'Access denied'}), 403
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath} (absolute: {abs_filepath})")
            return jsonify({'error': f'File not found: {filepath}'}), 404
        
        # Determine mimetype based on file extension
        if filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.mp3'):
            mimetype = 'audio/mpeg'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(filepath, mimetype=mimetype)
    except Exception as e:
        print(f"❌ Error serving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return jsonify({'error': 'Forbidden'}), 403

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'name': 'ML Learning Assistant',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_ENV') == 'development',
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000))
    )
