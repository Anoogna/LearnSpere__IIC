"""
Image Generation and Processing Module
Handles creation of educational diagrams and visual content
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
import base64
from io import BytesIO
import requests

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ImageUtils:
    def __init__(self, output_dir: str = "uploads/images"):
        """
        Initialize image utilities
        Args:
            output_dir: Directory to store generated images
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    def generate_image_from_prompt(self, prompt: str, filename: Optional[str] = None,
                                  use_api: str = "gemini") -> Optional[Tuple[str, str]]:
        """
        Generate image using AI model
        Args:
            prompt: Detailed prompt for image generation
            filename: Optional custom filename
            use_api: "gemini" or "stable_diffusion"
        Returns:
            Tuple of (file_path, file_url) or None if error
        """
        try:
            if use_api == "gemini":
                return self._generate_with_gemini(prompt, filename)
            elif use_api == "stable_diffusion":
                return self._generate_with_stable_diffusion(prompt, filename)
            else:
                return self._generate_placeholder_diagram(prompt, filename)
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None
    
    def _generate_with_gemini(self, prompt: str, filename: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Generate image using Google Gemini
        Note: Requires implementation with actual Gemini API image generation
        """
        try:
            import google.generativeai as genai
            from google.generativeai import types
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"diagram_gemini_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Note: Image generation in Gemini 2.0 has specific requirements
            # This is a placeholder - actual implementation depends on Gemini API version
            model = genai.GenerativeModel('gemini-2.0-flash-preview-image-generation')
            response = model.generate_content([
                types.Part.from_text(prompt)
            ])
            
            if response.parts and response.parts[0].inline_data:
                image_data = response.parts[0].inline_data.data
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                web_path = filepath.replace('\\', '/')
                return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Gemini image generation not available or failed: {str(e)}")
            # Fall back to placeholder
        
        return None
    
    def _generate_with_stable_diffusion(self, prompt: str, filename: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Generate image using Stable Diffusion via HuggingFace
        Requires HF_TOKEN environment variable
        """
        try:
            hf_token = os.getenv('HF_TOKEN')
            if not hf_token:
                print("HF_TOKEN not set for Stable Diffusion")
                return None
            
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            response = requests.post(api_url, headers=headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                image_data = response.content
                
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"diagram_diffusion_{timestamp}.png"
                
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                web_path = filepath.replace('\\', '/')
                return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Stable Diffusion generation failed: {str(e)}")
        
        return None
    
    def _generate_placeholder_diagram(self, prompt: str, filename: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Generate a simple educational diagram as placeholder
        Uses PIL to create text-based diagrams
        """
        if not PIL_AVAILABLE:
            print("PIL not available for placeholder generation")
            return None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"diagram_placeholder_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Create a simple educational diagram
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color=(240, 248, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw title
            title = "Educational Diagram"
            draw.text((50, 30), title, fill=(0, 0, 0))
            
            # Draw prompt text wrapped
            y_position = 100
            max_width = 70
            for line in prompt[:200].split('\n'):
                for i in range(0, len(line), max_width):
                    draw.text((50, y_position), line[i:i+max_width], fill=(50, 50, 50))
                    y_position += 25
            
            # Draw some decorative elements
            draw.rectangle([50, 450, 750, 550], outline=(100, 150, 200), width=2)
            draw.text((300, 490), "Generated Content Placeholder", fill=(100, 150, 200))
            
            image.save(filepath)
            
            web_path = filepath.replace('\\', '/')
            return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Error generating placeholder: {str(e)}")
            return None
    
    def create_technical_diagram(self, diagram_type: str, data: dict) -> Optional[Tuple[str, str]]:
        """
        Create specific technical diagrams (flowcharts, architecture, etc.)
        Args:
            diagram_type: Type of diagram ("flowchart", "architecture", "decision_tree", etc.)
            data: Dictionary containing diagram-specific data
        Returns:
            Tuple of (file_path, file_url) or None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{diagram_type}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            if diagram_type == "flowchart":
                return self._create_flowchart(data, filepath)
            elif diagram_type == "architecture":
                return self._create_architecture_diagram(data, filepath)
            elif diagram_type == "decision_tree":
                return self._create_decision_tree_diagram(data, filepath)
        except Exception as e:
            print(f"Error creating technical diagram: {str(e)}")
        
        return None
    
    def _create_flowchart(self, data: dict, filepath: str) -> Tuple[str, str]:
        """Create a flowchart diagram"""
        image = Image.new('RGB', (800, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        draw.rectangle([300, 50, 500, 100], outline=(0, 0, 0), width=2)
        draw.text((330, 65), "START", fill=(0, 0, 0))
        
        draw.rectangle([300, 150, 500, 200], outline=(0, 0, 0), width=2)
        draw.text((310, 165), "Process", fill=(0, 0, 0))
        
        draw.line([400, 100, 400, 150], fill=(0, 0, 0), width=2)
        draw.line([400, 200, 400, 250], fill=(0, 0, 0), width=2)
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_architecture_diagram(self, data: dict, filepath: str) -> Tuple[str, str]:
        """Create an architecture diagram"""
        image = Image.new('RGB', (800, 600), color=(245, 245, 245))
        draw = ImageDraw.Draw(image)
        
        # Draw simple layers
        colors = [(200, 220, 255), (200, 255, 220), (255, 240, 200)]
        labels = ["Frontend", "Backend", "Database"]
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            y = 100 + (i * 150)
            draw.rectangle([100, y, 700, y+100], fill=color, outline=(0, 0, 0), width=2)
            draw.text((300, y+40), label, fill=(0, 0, 0))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_decision_tree_diagram(self, data: dict, filepath: str) -> Tuple[str, str]:
        """Create a decision tree diagram"""
        image = Image.new('RGB', (800, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Root node
        draw.ellipse([350, 50, 450, 100], outline=(0, 0, 0), width=2)
        draw.text((360, 65), "Root", fill=(0, 0, 0))
        
        # Left branch
        draw.ellipse([150, 200, 250, 250], outline=(0, 0, 0), width=2)
        draw.line([400, 100, 200, 200], fill=(0, 0, 0), width=2)
        draw.text((160, 215), "Left", fill=(0, 0, 0))
        
        # Right branch
        draw.ellipse([550, 200, 650, 250], outline=(0, 0, 0), width=2)
        draw.line([400, 100, 600, 200], fill=(0, 0, 0), width=2)
        draw.text((560, 215), "Right", fill=(0, 0, 0))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def encode_image_to_base64(self, filepath: str) -> Optional[str]:
        """
        Encode image to base64 for web display
        Args:
            filepath: Path to image file
        Returns:
            Base64 encoded image string
        """
        try:
            with open(filepath, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            return None
    
    def list_generated_images(self) -> List[dict]:
        """
        List all generated images
        Returns:
            List of image information dictionaries
        """
        images = []
        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    images.append({
                        'filename': filename,
                        'path': f"/{filepath.replace(chr(92), '/')}",
                        'created': datetime.fromtimestamp(
                            os.path.getmtime(filepath)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            print(f"Error listing images: {str(e)}")
        
        return sorted(images, key=lambda x: x['created'], reverse=True)

# Create global instance
image_utils = None

def init_images(output_dir: str = "uploads/images"):
    """Initialize the image utility module"""
    global image_utils
    image_utils = ImageUtils(output_dir)
    return image_utils

def get_images():
    """Get the image utility instance"""
    global image_utils
    if image_utils is None:
        image_utils = ImageUtils()
    return image_utils
