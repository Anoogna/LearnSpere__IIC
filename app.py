#!/usr/bin/env python3
"""
ML Learning Assistant - Main Flask Application
GyanGuru: AI Powered Learning Assistant for AI & ML
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename

# Import utility modules
from utils.genai_utils import get_gemini, init_gemini
from utils.audio_utils import get_audio, init_audio
from utils.image_utils import get_images, init_images
from utils.code_executor import get_code_executor, init_code_executor

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Enable CORS
CORS(app)

# Initialize upload directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/code', exist_ok=True)

# Initialize utility modules
init_gemini(os.getenv('GOOGLE_API_KEY'))
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
# API ROUTES - TEXT EXPLANATION
# ============================================

@app.route('/api/generate-explanation', methods=['POST'])
def generate_explanation():
    """Generate text explanation for ML topic"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        complexity = data.get('complexity', 'Intermediate')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        gemini = get_gemini()
        explanation = gemini.generate_text_explanation(topic, complexity)
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'topic': topic,
            'complexity': complexity,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
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
        
        gemini = get_gemini()
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
        
        gemini = get_gemini()
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
        backend = data.get('backend', 'gemini')
        
        if not concept:
            return jsonify({'error': 'Concept is required'}), 400
        
        gemini = get_gemini()
        prompt = gemini.generate_image_prompt(concept, diagram_type)
        
        images = get_images()
        filepath, webpath = images.generate_image_from_prompt(prompt, use_api=backend)
        
        if filepath:
            return jsonify({
                'success': True,
                'image_url': webpath,
                'concept': concept,
                'diagram_type': diagram_type,
                'prompt': prompt,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to generate image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-images-multiple', methods=['POST'])
def generate_images_multiple():
    """Generate multiple diagrams for a concept"""
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        count = min(int(data.get('count', 1)), 5)  # Max 5 images
        
        if not concept:
            return jsonify({'error': 'Concept is required'}), 400
        
        gemini = get_gemini()
        images_obj = get_images()
        
        generated_images = []
        for i in range(count):
            diagram_types = ['Conceptual', 'Technical', 'Flowchart']
            diagram_type = diagram_types[i % len(diagram_types)]
            
            prompt = gemini.generate_image_prompt(concept, diagram_type)
            filepath, webpath = images_obj.generate_image_from_prompt(prompt)
            
            if filepath:
                generated_images.append({
                    'image_url': webpath,
                    'diagram_type': diagram_type,
                    'prompt': prompt
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
        
        gemini = get_gemini()
        
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
