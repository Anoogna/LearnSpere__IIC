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
from utils.genai_utils import get_groq, init_groq
from utils.audio_utils import get_audio, init_audio
from utils.image_utils import get_images, init_images
from utils.code_executor import get_code_executor, init_code_executor
import logging
# Configure logging to file
logging.basicConfig(
    filename='flask_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'iichackathon')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Force template reloading
app.jinja_env.auto_reload = True  # Force Jinja2 auto-reload
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable file caching

# Enable CORS
CORS(app)

# Initialize upload directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/code', exist_ok=True)

# Initialize utility modules
init_groq() # Automatically loads from GROQ_API_KEY env var
init_audio()
init_images()
init_code_executor()

# ============================================
# STATIC FILES SERVING
# ============================================

# Serve uploaded files
@app.route('/uploads/<path:filepath>')
def serve_upload(filepath):
    """Serve uploaded files (audio, images, code)"""
    print(f"📁 Upload request for: {filepath}")
    try:
        full_path = os.path.join('uploads', filepath)
        print(f"📂 Full path: {full_path}")
        print(f"📂 File exists: {os.path.exists(full_path)}")
        if os.path.exists(full_path):
            # Determine MIME type based on file extension
            mimetype = 'application/octet-stream'
            if filepath.lower().endswith('.mp3'):
                mimetype = 'audio/mpeg'
            elif filepath.lower().endswith('.wav'):
                mimetype = 'audio/wav'
            elif filepath.lower().endswith('.png'):
                mimetype = 'image/png'
            elif filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
                mimetype = 'image/jpeg'
            elif filepath.lower().endswith('.py'):
                mimetype = 'text/plain'
            
            # Serve file inline (for playing in browser) not as attachment
            response = send_file(full_path, mimetype=mimetype, as_attachment=False)
            # Add headers for better caching and browser support
            response.headers['Cache-Control'] = 'public, max-age=86400'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        gemini = get_groq()
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
        
        print(f"🔧 Code generation request: algorithm='{algorithm}', complexity='{complexity}'")
        
        if not algorithm:
            return jsonify({'error': 'Algorithm is required'}), 400
        
        gemini = get_groq()
        code = gemini.generate_code_example(algorithm, complexity)
        
        print(f"📝 Generated code length: {len(code)} characters")
        print(f"📝 Code preview: {code[:200]}...")
        
        # Detect dependencies
        dependencies = get_code_executor().detect_dependencies(code)
        
        print(f"📦 Dependencies detected: {dependencies}")
        
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
        print(f"💥 Error in code generation: {str(e)}")
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
        result = None
        
        if audio_type == 'script':
            result = audio.generate_educational_audio(text, topic)
        else:
            result = audio.generate_audio(text)
        
        if result:
            filepath, webpath, filename = result
            audio_play_url = f'/uploads/audio/{filename}'
            audio_download_url = f'/api/download/audio/{filename}'
            return jsonify({
                'success': True,
                'audio_url': audio_play_url,
                'audio_path': filepath,
                'filename': filename,
                'download_url': audio_download_url,
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
        
        print(f"🎙️ Generating audio script for: {topic} (Length: {length})")
        
        gemini = get_groq()
        script = gemini.generate_audio_script(topic, length)
        
        print(f"📝 Script generated, length: {len(script)} characters")
        
        # Generate audio from script
        audio = get_audio()
        audio_result = audio.generate_educational_audio(script, topic)
        
        if audio_result:
            filepath, webpath, filename = audio_result
            print(f"✅ Audio file created: {filename}")
            
            audio_play_url = f'/api/download/audio/{filename}?mode=play'
            audio_download_url = f'/api/download/audio/{filename}'
            
            return jsonify({
                'success': True,
                'script': script,
                'topic': topic,
                'length': length,
                'audio_url': audio_play_url,
                'filename': filename,
                'download_url': audio_download_url,
                'generated_at': datetime.now().isoformat()
            })
        else:
            print("❌ Audio generation failed")
            return jsonify({
                'success': True,
                'script': script,
                'topic': topic,
                'length': length,
                'audio_url': None,
                'filename': None,
                'message': 'Script generated but audio generation failed',
                'generated_at': datetime.now().isoformat()
            })
    except Exception as e:
        print(f"💥 Error: {str(e)}")
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
        
        print(f"🎨 Generating {diagram_type} diagram for: {concept}")
        
        gemini = get_groq()
        prompt = gemini.generate_image_prompt(concept, diagram_type)
        
        print(f"📝 Prompt generated for image creation")
        
        images = get_images()
        logging.debug(f"Calling generate_image_from_prompt for {concept}")
        result = images.generate_image_from_prompt(prompt, filename=None, diagram_type=diagram_type, use_api=backend, topic=concept)
        logging.debug(f"Generation result: {result}")
        
        if result:
            filepath, webpath = result
            print(f"✅ Image generated successfully: {diagram_type}")
            return jsonify({
                'success': True,
                'image_url': webpath,
                'concept': concept,
                'diagram_type': diagram_type,
                'prompt': prompt[:200] if len(prompt) > 200 else prompt,
                'generated_at': datetime.now().isoformat()
            })
        else:
            print(f"❌ Image generation failed completely - both API and fallback")
            return jsonify({
                'success': False,
                'error': 'Image generation service unavailable. Please try again later.',
                'concept': concept,
                'diagram_type': diagram_type
            }), 503  # Service Unavailable
    except Exception as e:
        print(f"💥 Error generating image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

@app.route('/api/generate-images-multiple', methods=['POST'])
def generate_images_multiple():
    """Generate multiple diverse diagrams for a concept from different perspectives"""
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        count = min(int(data.get('count', 4)), 5)  # Max 5 images
        
        if not concept:
            return jsonify({'error': 'Concept is required'}), 400
        
        print(f"🖼️ Generating {count} diverse diagrams for: {concept}")
        
        gemini = get_groq()
        images_obj = get_images()
        
        # Get diverse perspectives for this topic
        all_perspectives = gemini.get_diverse_perspectives(concept)
        perspectives = all_perspectives[:count]
        
        generated_images = []
        
        for i, (diagram_type, perspective) in enumerate(perspectives):
            print(f"📐 Creating {diagram_type} diagram - {perspective or 'general'} ({i+1}/{count})...")
            
            # Generate unique prompt for this perspective
            prompt = gemini.generate_image_prompt(concept, diagram_type, perspective)
            result = images_obj.generate_image_from_prompt(prompt, filename=None, diagram_type=diagram_type, topic=concept)
            
            if result:
                filepath, webpath = result
                perspective_label = f"{perspective.title()}" if perspective else "General"
                generated_images.append({
                    'image_url': webpath,
                    'diagram_type': diagram_type,
                    'perspective': perspective_label,
                    'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt
                })
                print(f"✅ {diagram_type} ({perspective_label}) diagram generated")
            else:
                print(f"⚠️ {diagram_type} ({perspective_label}) diagram generation failed")
        
        print(f"✅ Generated {len(generated_images)} unique diagrams")
        
        return jsonify({
            'success': True,
            'images': generated_images,
            'concept': concept,
            'count': len(generated_images),
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"💥 Error generating multiple images: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print(f"📊 Listed {len(files)} audio files")
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        print(f"❌ Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete/audio/<filename>', methods=['DELETE'])
def delete_audio_file(filename):
    """Delete an audio file"""
    print(f"🗑️ Delete request received for: {filename}")
    try:
        filename = secure_filename(filename)
        print(f"🔒 Secure filename: {filename}")
        filepath = os.path.join('uploads/audio', filename)
        print(f"📁 Full path: {filepath}")
        print(f"📂 File exists: {os.path.exists(filepath)}")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ File deleted successfully")
            return jsonify({
                'success': True,
                'message': f'Audio file "{filename}" deleted successfully'
            })
        else:
            print(f"❌ File not found")
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        print(f"💥 Error: {str(e)}")
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

# Audio playback endpoint (serves inline for browser playback)
@app.route('/api/play/audio/<filename>', methods=['GET'])
def play_audio(filename):
    """Play audio file inline in browser"""
    print(f"🎵 Play request for: {filename}")
    try:
        filename = secure_filename(filename)
        print(f"🔒 Secure filename: {filename}")
        filepath = os.path.join('uploads/audio', filename)
        print(f"📁 Full path: {filepath}")
        print(f"📂 File exists: {os.path.exists(filepath)}")
        
        if os.path.exists(filepath):
            print(f"✅ Serving audio file")
            # Serve inline for playback, not as attachment
            response = send_file(
                filepath,
                mimetype='audio/mpeg',
                as_attachment=False
            )
            # Add headers for streaming and caching
            response.headers['Cache-Control'] = 'public, max-age=3600'
            response.headers['Accept-Ranges'] = 'bytes'
            return response
        else:
            print(f"❌ Audio file not found")
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    return "Server is working!"

@app.route('/api/test-delete', methods=['DELETE'])
def test_delete():
    return jsonify({'success': True, 'message': 'Delete route works'})

@app.route('/api/download/<file_type>/<filename>', methods=['GET'])
def download_file(file_type, filename):
    """Download generated files with proper headers"""
    try:
        filename = secure_filename(filename)
        
        if file_type == 'audio':
            filepath = os.path.join('uploads/audio', filename)
            mimetype = 'audio/mpeg'
        elif file_type == 'image':
            filepath = os.path.join('uploads/images', filename)
            mimetype = 'image/png'
        elif file_type == 'code':
            filepath = os.path.join('uploads/code', filename)
            mimetype = 'text/plain'
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        if os.path.exists(filepath):
            # Check if this is for playback or download
            mode = request.args.get('mode', 'download')
            as_attachment = (mode != 'play')
            
            response = send_file(
                filepath,
                mimetype=mimetype,
                as_attachment=as_attachment,
                download_name=filename if as_attachment else None
            )
            
            if as_attachment:
                # Download headers
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                # Playback headers -remove attachment header for inline playback
                response.headers['Cache-Control'] = 'public, max-age=3600'
                response.headers['Accept-Ranges'] = 'bytes'
                # Remove Content-Disposition to allow inline playback
                if 'Content-Disposition' in response.headers:
                    del response.headers['Content-Disposition']
            
            return response
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
                'download_url': audio_file[1] if audio_file else None,
                'filename': audio_file[2] if audio_file else None,
                'api_download_url': f'/api/download/audio/{audio_file[2]}' if audio_file else None
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
    port = int(os.getenv('FLASK_PORT', 5000))
    host = '0.0.0.0'
    print(f"\n{'='*60}")
    print(f"🚀 Starting ML Learning Assistant...")
    print(f"🌐 Running on: http://localhost:{port}")
    print(f"🔧 Host: {host}")
    print(f"{'='*60}\n")
    
    app.run(
        debug=os.getenv('FLASK_ENV') == 'development',
        host=host,
        port=port
    )
