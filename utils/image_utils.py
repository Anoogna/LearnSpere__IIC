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
import random

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

    def _unique_stamp(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{ts}_{random.randint(1000, 9999)}"
        
    def generate_image_from_prompt(self, prompt: str, filename: Optional[str] = None,
                                  use_api: str = "placeholder", diagram_type: str = None,
                                  variation: int = 0) -> Optional[Tuple[str, str]]:
        """
        Generate image using AI model or placeholder diagram
        Args:
            prompt: Detailed prompt for image generation
            filename: Optional custom filename
            use_api: "stable_diffusion", "placeholder", or any other (defaults to placeholder)
            diagram_type: Force a specific diagram type ("neural_network", "decision_tree", "flowchart", "architecture", "generic")
            variation: Visual variation (0-4) for different styles of the same diagram type
        Returns:
            Tuple of (file_path, file_url) or None if error
        """
        try:
            if use_api == "stable_diffusion":
                return self._generate_with_stable_diffusion(prompt, filename)
            else:
                # Default to smart placeholder diagram generation
                return self._generate_placeholder_diagram(prompt, filename, diagram_type, variation)
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None

    def _generate_svg_placeholder(self, prompt: str, filename: Optional[str] = None) -> Optional[Tuple[str, str]]:
        try:
            if filename is None:
                filename = f"diagram_generated_{self._unique_stamp()}.svg"
            if not filename.lower().endswith('.svg'):
                filename = os.path.splitext(filename)[0] + '.svg'

            filepath = os.path.join(self.output_dir, filename)
            title = (prompt or "Concept Visualization").strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if len(title) > 80:
                title = title[:77] + '...'

            svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"500\" viewBox=\"0 0 900 500\">
  <rect x=\"0\" y=\"0\" width=\"900\" height=\"500\" fill=\"#ffffff\"/>
  <rect x=\"40\" y=\"40\" width=\"820\" height=\"420\" rx=\"18\" fill=\"#f8f9fa\" stroke=\"#667eea\" stroke-width=\"3\"/>
  <text x=\"450\" y=\"120\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"26\" fill=\"#333\">ML Concept Diagram</text>
  <text x=\"450\" y=\"190\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"18\" fill=\"#555\">{title}</text>
  <circle cx=\"250\" cy=\"320\" r=\"55\" fill=\"#667eea\" opacity=\"0.85\"/>
  <circle cx=\"450\" cy=\"320\" r=\"55\" fill=\"#764ba2\" opacity=\"0.85\"/>
  <circle cx=\"650\" cy=\"320\" r=\"55\" fill=\"#28a745\" opacity=\"0.85\"/>
  <line x1=\"305\" y1=\"320\" x2=\"395\" y2=\"320\" stroke=\"#999\" stroke-width=\"3\"/>
  <line x1=\"505\" y1=\"320\" x2=\"595\" y2=\"320\" stroke=\"#999\" stroke-width=\"3\"/>
  <text x=\"250\" y=\"326\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\" fill=\"#fff\">Input</text>
  <text x=\"450\" y=\"326\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\" fill=\"#fff\">Model</text>
  <text x=\"650\" y=\"326\" text-anchor=\"middle\" font-family=\"Arial\" font-size=\"14\" fill=\"#fff\">Output</text>
</svg>"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg)

            web_path = filepath.replace('\\', '/')
            return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Error generating SVG diagram: {str(e)}")
            return None
    
    def _generate_with_stable_diffusion(self, prompt: str, filename: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Generate image using Stable Diffusion via HuggingFace
        Requires HF_TOKEN environment variable
        """
        try:
            hf_token = os.getenv('HF_TOKEN', '').strip()
            
            # Check if token is valid (not placeholder or empty)
            if not hf_token or hf_token == 'your-huggingface-token-here':
                print("[ERROR] HF_TOKEN not set or is placeholder for Stable Diffusion")
                print("   Get your token from: https://huggingface.co/settings/tokens")
                return None
            
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
            headers = {"Authorization": f"Bearer {hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "guidance_scale": 7.5,
                    "num_inference_steps": 30,
                    "negative_prompt": "low quality, blurry, distorted text, watermark, logo, photorealistic face, extra limbs",
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            print(f"[INFO] Calling Stable Diffusion API with prompt: {prompt[:50]}...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                print("[SUCCESS] Stable Diffusion API returned 200 OK")
                image_data = response.content
                
                if filename is None:
                    filename = f"diagram_diffusion_{self._unique_stamp()}.png"
                
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                print(f"[SUCCESS] Image saved to: {filepath}")
                web_path = filepath.replace('\\', '/')
                return filepath, f"/{web_path}"
            
            elif response.status_code == 503:
                print(f"[ERROR] Stable Diffusion model is loading (503 error). Try again in a moment.")
                try:
                    error_data = response.json()
                    if 'estimated_time' in error_data:
                        print(f"   Estimated reload time: {error_data['estimated_time']} seconds")
                except:
                    pass
                return None
            
            elif response.status_code == 401:
                print(f"[ERROR] Authentication failed (401). Invalid HF_TOKEN.")
                return None
            
            elif response.status_code == 429:
                print(f"[ERROR] Rate limited (429). Too many requests. Please wait.")
                return None
            
            else:
                print(f"[ERROR] Stable Diffusion API error ({response.status_code}): {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[ERROR] Stable Diffusion request timed out (30 seconds). Model may be slow to respond.")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Connection error to Stable Diffusion API. Check your internet connection.")
            return None
        except Exception as e:
            print(f"[ERROR] Stable Diffusion generation failed: {str(e)}")
            return None
    
    def _generate_placeholder_diagram(self, prompt: str, filename: Optional[str] = None, 
                                    force_type: str = None, variation: int = 0) -> Optional[Tuple[str, str]]:
        """
        Generate a smart educational diagram using PIL
        Creates concept-aware diagrams based on the prompt content
        Args:
            prompt: The prompt/concept to visualize
            filename: Optional custom filename
            force_type: Force a specific diagram type instead of auto-detecting
            variation: Visual variation (0-4) for different styles of the same diagram type
        """
        if not PIL_AVAILABLE:
            return self._generate_svg_placeholder(prompt, filename)
        
        try:
            if filename is None:
                type_tag = (force_type or "auto").lower().replace(' ', '_')
                filename = f"diagram_generated_{type_tag}_v{int(variation)}_{self._unique_stamp()}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Determine diagram type
            if force_type:
                diagram_type = force_type.lower()
            else:
                diagram_type = self._detect_diagram_type(prompt)
            
            # Generate the appropriate diagram
            if diagram_type == "neural_network":
                return self._create_neural_network_diagram(filepath, prompt, variation)
            elif diagram_type == "decision_tree":
                return self._create_decision_tree_diagram_auto(filepath, prompt, variation)
            elif diagram_type == "flowchart":
                return self._create_flowchart_auto(filepath, prompt, variation)
            elif diagram_type == "architecture":
                return self._create_architecture_diagram_auto(filepath, prompt, variation)
            else:
                return self._create_generic_concept_diagram(filepath, prompt, variation)
                
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
    
    def _create_neural_network_diagram(self, filepath: str, prompt: str, variation: int = 0) -> Tuple[str, str]:
        """Create a neural network visualization with style variations"""
        width, height = 1000, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Neural Network Architecture", fill=(0, 0, 0))
        
        # Different layer configs for variations
        variations = [
            {"input": 4, "hidden": 6, "output": 2, "color": (100, 150, 255)},  # Blue
            {"input": 5, "hidden": 8, "output": 3, "color": (100, 200, 100)},  # Green
            {"input": 3, "hidden": 7, "output": 2, "color": (255, 150, 100)},  # Orange
            {"input": 6, "hidden": 10, "output": 4, "color": (200, 100, 255)},  # Purple
            {"input": 4, "hidden": 5, "output": 3, "color": (255, 100, 150)},  # Pink
        ]
        
        config = variations[variation % len(variations)]
        input_nodes = config["input"]
        hidden_nodes = config["hidden"]
        output_nodes = config["output"]
        color = config["color"]
        
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
                draw.ellipse([x-15, y-15, x+15, y+15], fill=color, outline=(0, 0, 100), width=2)
                draw.text((x-5, y-5), str(i+1), fill=(255, 255, 255))
            
            # Draw connections to next layer
            if layer_idx < len(layer_pos) - 1:
                next_x, next_num = layer_pos[layer_idx + 1]
                next_y_start = (height - next_num * 80) // 2
                
                for i, (nx, ny) in enumerate(node_positions):
                    for j in range(next_num):
                        next_y = next_y_start + j * 80
                        draw.line([(nx, ny), (next_x, next_y)], fill=(150, 150, 150), width=1)
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_decision_tree_diagram_auto(self, filepath: str, prompt: str, variation: int = 0) -> Tuple[str, str]:
        """Create an enhanced decision tree diagram with variations"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Decision Tree", fill=(0, 0, 0))
        
        # Color schemes for variations
        color_schemes = [
            {"root": (100, 200, 100), "branch": (150, 150, 200), "leaf": (200, 100, 100)},
            {"root": (100, 150, 255), "branch": (200, 200, 100), "leaf": (255, 150, 100)},
            {"root": (200, 100, 150), "branch": (150, 200, 150), "leaf": (100, 150, 255)},
            {"root": (255, 180, 100), "branch": (150, 150, 255), "leaf": (100, 255, 150)},
            {"root": (150, 255, 100), "branch": (255, 150, 150), "leaf": (100, 150, 255)},
        ]
        
        colors = color_schemes[variation % len(color_schemes)]
        
        # Root node
        root_x, root_y = 450, 80
        draw.rectangle([root_x-70, root_y-30, root_x+70, root_y+30], fill=colors["root"], outline=(0, 0, 0), width=2)
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
            draw.rectangle([x-60, y-30, x+60, y+30], fill=colors["branch"], outline=(0, 0, 0), width=2)
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
            draw.ellipse([x-40, y-30, x+40, y+30], fill=colors["leaf"], outline=(0, 0, 0), width=2)
            draw.text((x-35, y-15), label, fill=(255, 255, 255))
        
        image.save(filepath)
        return filepath, f"/{filepath.replace(chr(92), '/')}"
    
    def _create_flowchart_auto(self, filepath: str, prompt: str, variation: int = 0) -> Tuple[str, str]:
        """Create an enhanced flowchart with variations"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Process Flowchart", fill=(0, 0, 0))
        
        # Color and layout variations
        color_sets = [
            [(100, 200, 100), (100, 150, 200), (100, 200, 100), (255, 200, 100), (100, 200, 100), (200, 100, 100)],
            [(150, 200, 255), (200, 150, 100), (150, 200, 255), (100, 200, 150), (150, 200, 255), (255, 100, 150)],
            [(200, 100, 150), (100, 200, 150), (200, 100, 150), (150, 150, 200), (200, 100, 150), (100, 150, 200)],
            [(100, 150, 200), (255, 150, 100), (100, 150, 200), (150, 255, 100), (100, 150, 200), (100, 255, 150)],
            [(255, 180, 100), (100, 180, 255), (255, 180, 100), (100, 255, 180), (255, 180, 100), (180, 100, 255)],
        ]
        
        colors = color_sets[variation % len(color_sets)]
        
        steps = [
            ("START", 100, colors[0]),
            ("Input Data", 200, colors[1]),
            ("Process", 300, colors[2]),
            ("Decision", 400, colors[3]),
            ("Output", 500, colors[4]),
            ("END", 600, colors[5])
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
    
    def _create_architecture_diagram_auto(self, filepath: str, prompt: str, variation: int = 0) -> Tuple[str, str]:
        """Create an enhanced architecture diagram with variations"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(245, 245, 245))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "System Architecture", fill=(0, 0, 0))
        
        # Color schemes
        color_schemes = [
            [(100, 180, 255), (100, 255, 180), (255, 220, 100)],
            [(255, 150, 100), (100, 200, 255), (150, 255, 100)],
            [(200, 100, 150), (100, 200, 150), (150, 100, 200)],
            [(100, 150, 200), (255, 180, 100), (100, 255, 150)],
            [(180, 100, 200), (100, 180, 150), (200, 150, 100)],
        ]
        
        colors = color_schemes[variation % len(color_schemes)]
        
        layers = [
            ("Frontend\n(React, Vue)", 100, colors[0]),
            ("API Layer\n(REST, GraphQL)", 230, colors[1]),
            ("Database\n(SQL, NoSQL)", 360, colors[2])
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
    
    def _create_generic_concept_diagram(self, filepath: str, prompt: str, variation: int = 0) -> Tuple[str, str]:
        """Create a generic concept diagram with visual elements and variations"""
        width, height = 900, 700
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Title
        draw.text((20, 20), "Concept Visualization", fill=(0, 0, 0))
        
        # Color schemes for variations
        central_colors = [
            {"main": (100, 150, 255), "concepts": [(150, 200, 255), (200, 255, 150), (255, 200, 150), (255, 150, 150), (200, 150, 255), (150, 255, 200)]},
            {"main": (100, 200, 100), "concepts": [(150, 255, 150), (255, 150, 100), (150, 150, 255), (255, 255, 100), (100, 255, 255), (255, 100, 255)]},
            {"main": (200, 100, 150), "concepts": [(255, 150, 200), (150, 255, 200), (200, 150, 255), (255, 200, 150), (150, 200, 255), (200, 255, 150)]},
            {"main": (255, 150, 100), "concepts": [(255, 200, 150), (150, 255, 150), (150, 150, 255), (255, 150, 150), (150, 255, 255), (255, 255, 150)]},
            {"main": (150, 150, 200), "concepts": [(200, 200, 255), (200, 255, 200), (255, 200, 200), (255, 200, 255), (200, 255, 255), (255, 255, 200)]},
        ]
        
        colors = central_colors[variation % len(central_colors)]
        
        # Central concept
        center_x, center_y = 450, 350
        draw.ellipse([center_x-80, center_y-80, center_x+80, center_y+80], fill=colors["main"], outline=(0, 0, 100), width=3)
        draw.text((center_x-70, center_y-20), "Main\nConcept", fill=(255, 255, 255))
        
        # Related concepts around
        num_concepts = 6
        import math
        radius = 250
        
        concepts = ["Theory", "Practice", "Application", "Benefits", "Challenges", "Future"]
        
        for i, (concept, color) in enumerate(zip(concepts, colors["concepts"])):
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
                if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
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
