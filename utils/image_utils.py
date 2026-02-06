"""
Image Generation and Processing Module
Handles creation of educational diagrams and visual content
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import base64
from io import BytesIO
import requests
import json

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
                                  use_api: str = "placeholder") -> Optional[Tuple[str, str]]:
        """
        Generate image using AI model or placeholder diagram
        Args:
            prompt: Detailed prompt for image generation
            filename: Optional custom filename
            use_api: "stable_diffusion", "placeholder", or any other (defaults to placeholder)
        Returns:
            Tuple of (file_path, file_url) or None if error
        """
        try:
            if use_api == "stable_diffusion":
                return self._generate_with_stable_diffusion(prompt, filename)
            else:
                # Default to smart placeholder diagram generation
                return self._generate_placeholder_diagram(prompt, filename)
        except Exception as e:
            print(f"Error generating image: {str(e)}")
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
        Generate a smart educational diagram using PIL
        Creates concept-aware diagrams based on the prompt content
        """
        if not PIL_AVAILABLE:
            print("PIL not available for diagram generation")
            return None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"diagram_generated_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Detect diagram type from prompt
            diagram_type = self._detect_diagram_type(prompt)
            
            if diagram_type == "neural_network":
                return self._create_neural_network_diagram(filepath, prompt)
            elif diagram_type == "decision_tree":
                return self._create_decision_tree_diagram_auto(filepath, prompt)
            elif diagram_type == "flowchart":
                return self._create_flowchart_auto(filepath, prompt)
            elif diagram_type == "architecture":
                return self._create_architecture_diagram_auto(filepath, prompt)
            else:
                return self._create_generic_concept_diagram(filepath, prompt)
                
        except Exception as e:
            print(f"Error generating diagram: {str(e)}")
            return None
    
    def _detect_diagram_type(self, prompt: str) -> str:
        """Detect the type of diagram from the prompt text"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['neural', 'network', 'neuron', 'layer', 'perceptron']):
            return "neural_network"
        elif any(word in prompt_lower for word in ['decision', 'tree', 'split', 'leaf', 'node']):
            return "decision_tree"
        elif any(word in prompt_lower for word in ['flow', 'process', 'step', 'sequence', 'arrow']):
            return "flowchart"
        elif any(word in prompt_lower for word in ['architecture', 'layer', 'component', 'system']):
            return "architecture"
        else:
            return "generic"
    
    def _create_neural_network_diagram(self, filepath: str, prompt: str) -> Tuple[str, str]:
        """Create a neural network visualization"""
        width, height = 1000, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Neural Network Architecture", fill=(0, 0, 0))
        
        # Draw layers
        input_nodes = 4
        hidden_nodes = 6
        output_nodes = 2
        
        layer_pos = [
            (100, input_nodes),
            (400, hidden_nodes),
            (700, output_nodes)
        ]
        layer_names = ["Input Layer", "Hidden Layer", "Output Layer"]
        
        for layer_idx, (x, num_nodes) in enumerate(layer_pos):
            # Draw label
            draw.text((x - 30, 50), layer_names[layer_idx], fill=(50, 50, 100))
            
            # Draw nodes
            y_start = (height - num_nodes * 80) // 2
            node_positions = []
            
            for i in range(num_nodes):
                y = y_start + i * 80
                node_positions.append((x, y))
                draw.ellipse([x-15, y-15, x+15, y+15], fill=(100, 150, 255), outline=(0, 0, 100), width=2)
                draw.text((x-5, y-5), str(i+1), fill=(255, 255, 255))
            
            # Draw connections to next layer
            if layer_idx < len(layer_pos) - 1:
                next_x, next_num = layer_pos[layer_idx + 1]
                next_y_start = (height - next_num * 80) // 2
                
                for i, (nx, ny) in enumerate(node_positions):
                    for j in range(next_num):
                        next_y = next_y_start + j * 80
                        # Draw thin connection lines
                        draw.line([(nx, ny), (next_x, next_y)], fill=(150, 150, 150), width=1)
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_decision_tree_diagram_auto(self, filepath: str, prompt: str) -> Tuple[str, str]:
        """Create an enhanced decision tree diagram"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Decision Tree", fill=(0, 0, 0))
        
        # Root node
        root_x, root_y = 450, 80
        draw.rectangle([root_x-70, root_y-30, root_x+70, root_y+30], fill=(100, 200, 100), outline=(0, 0, 0), width=2)
        draw.text((root_x-50, root_y-15), "Root Node", fill=(255, 255, 255))
        
        # Level 2 nodes (branches)
        level2_nodes = [
            (200, 250, "True"),
            (700, 250, "False")
        ]
        
        for x, y, label in level2_nodes:
            # Draw connector
            draw.line([(root_x, root_y+30), (x, y-30)], fill=(0, 0, 0), width=2)
            # Draw node
            draw.rectangle([x-60, y-30, x+60, y+30], fill=(150, 150, 200), outline=(0, 0, 0), width=2)
            draw.text((x-40, y-15), label, fill=(255, 255, 255))
        
        # Level 3 leaf nodes
        level3_nodes = [
            (100, 420, "Class A"),
            (300, 420, "Class B"),
            (600, 420, "Class C"),
            (800, 420, "Class D")
        ]
        
        # Connect level 2 to level 3
        for i, (x2, y2, _) in enumerate(level2_nodes):
            start_idx = i * 2
            for j in range(2):
                x3, y3, label = level3_nodes[start_idx + j]
                draw.line([(x2, y2+30), (x3, y3-30)], fill=(0, 0, 0), width=1)
        
        # Draw leaf nodes
        for x, y, label in level3_nodes:
            draw.ellipse([x-40, y-30, x+40, y+30], fill=(200, 100, 100), outline=(0, 0, 0), width=2)
            draw.text((x-35, y-15), label, fill=(255, 255, 255))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_flowchart_auto(self, filepath: str, prompt: str) -> Tuple[str, str]:
        """Create an enhanced flowchart"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Process Flowchart", fill=(0, 0, 0))
        
        steps = [
            ("START", 100, (100, 200, 100)),
            ("Input Data", 200, (100, 150, 200)),
            ("Process", 300, (100, 150, 200)),
            ("Decision", 400, (255, 200, 100)),
            ("Output", 500, (100, 200, 100)),
            ("END", 600, (200, 100, 100))
        ]
        
        x = 450
        previous_y = None
        
        for i, (label, y, color) in enumerate(steps):
            if i % 2 == 1:  # Decision diamond
                draw.polygon([(x-50, y), (x, y-40), (x+50, y), (x, y+40)], fill=color, outline=(0, 0, 0))
                draw.text((x-30, y-15), label, fill=(255, 255, 255))
            else:  # Rectangle
                draw.rectangle([x-50, y-30, x+50, y+30], fill=color, outline=(0, 0, 0), width=2)
                draw.text((x-45, y-15), label, fill=(255, 255, 255))
            
            # Draw arrows
            if previous_y is not None:
                draw.line([(x, previous_y+30), (x, y-40)], fill=(0, 0, 0), width=2)
                # Arrow head
                draw.polygon([(x, y-40), (x-5, y-30), (x+5, y-30)], fill=(0, 0, 0))
            
            previous_y = y
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_architecture_diagram_auto(self, filepath: str, prompt: str) -> Tuple[str, str]:
        """Create an enhanced architecture diagram"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(245, 245, 245))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "System Architecture", fill=(0, 0, 0))
        
        layers = [
            ("Frontend\n(React, Vue)", 100, (100, 180, 255)),
            ("API Layer\n(REST, GraphQL)", 230, (100, 255, 180)),
            ("Business Logic\n(Services)", 360, (255, 220, 100)),
            ("Database Layer\n(SQL, NoSQL)", 490, (255, 150, 150))
        ]
        
        box_height = 100
        
        for i, (label, y, color) in enumerate(layers):
            draw.rectangle([100, y, 800, y+box_height], fill=color, outline=(0, 0, 0), width=2)
            # Split label into multiple lines
            for j, line in enumerate(label.split('\n')):
                draw.text((150, y + 20 + j*30), line, fill=(255, 255, 255))
            
            # Draw arrow to next layer
            if i < len(layers) - 1:
                draw.line([(450, y+box_height), (450, y+box_height+20)], fill=(0, 0, 0), width=2)
                draw.polygon([(450, y+box_height+20), (445, y+box_height+10), (455, y+box_height+10)], fill=(0, 0, 0))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_generic_concept_diagram(self, filepath: str, prompt: str) -> Tuple[str, str]:
        """Create a generic concept diagram with visual elements"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Concept Visualization", fill=(0, 0, 0))
        
        # Central concept
        center_x, center_y = 450, 350
        draw.ellipse([center_x-80, center_y-80, center_x+80, center_y+80], fill=(100, 150, 255), outline=(0, 0, 100), width=3)
        draw.text((center_x-70, center_y-20), "Main\nConcept", fill=(255, 255, 255))
        
        # Related concepts around
        num_concepts = 6
        import math
        radius = 250
        
        concepts = ["Theory", "Practice", "Application", "Benefits", "Challenges", "Future"]
        colors = [(150, 200, 255), (200, 255, 150), (255, 200, 150), (255, 150, 150), (200, 150, 255), (150, 255, 200)]
        
        for i, (concept, color) in enumerate(zip(concepts, colors)):
            angle = 2 * math.pi * i / num_concepts
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            
            # Draw connecting line
            draw.line([(center_x, center_y), (x, y)], fill=(150, 150, 150), width=2)
            
            # Draw concept circle
            draw.ellipse([x-50, y-50, x+50, y+50], fill=color, outline=(0, 0, 0), width=2)
            draw.text((x-40, y-10), concept, fill=(0, 0, 0))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
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
