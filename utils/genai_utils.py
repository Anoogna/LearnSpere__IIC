"""
Google Gemini AI Integration Module
Handles text and image generation using Google's Gemini API
"""

import google.generativeai as genai
import os
from typing import Optional, List
import json

class GeminiAIUtils:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI with API key"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.text_model = genai.GenerativeModel('models/gemini-pro')
        self.image_model = genai.GenerativeModel('models/gemini-pro')
        
    def generate_text_explanation(self, topic: str, complexity_level: str = "Intermediate") -> str:
        """
        Generate comprehensive text explanation for ML topics
        Args:
            topic: ML topic to explain
            complexity_level: "Beginner", "Intermediate", "Comprehensive"
        Returns:
            Structured explanation text
        """
        prompt = f"""You are an expert ML educator. Generate a comprehensive explanation for the following topic.

Topic: {topic}
Complexity Level: {complexity_level}

Please provide:
1. Brief Overview (2-3 sentences)
2. Key Concepts (bullet points)
3. Mathematical Foundation (if applicable)
4. Practical Examples
5. Common Misconceptions
6. Resources for Further Learning

Format the response in clear, educational markdown."""
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def generate_code_example(self, algorithm: str, complexity: str = "Detailed") -> str:
        """
        Generate Python code examples with detailed comments
        Args:
            algorithm: Algorithm or concept to implement
            complexity: "Simple", "Detailed", "Production"
        Returns:
            Python code with comments and documentation
        """
        prompt = f"""You are an expert Python developer. Generate a {complexity} Python implementation for the following:

Algorithm/Concept: {algorithm}

Requirements:
1. Include clear inline comments explaining each part
2. Add docstrings for all functions
3. Use best practices and proper error handling
4. Include example usage at the bottom
5. List all required dependencies as a comment at the top

Format the response as complete, runnable Python code."""
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating code: {str(e)}"
    
    def generate_audio_script(self, topic: str, length: str = "Medium") -> str:
        """
        Generate conversational audio script for educational content
        Args:
            topic: Topic to create script for
            length: "Brief", "Medium", "Comprehensive"
        Returns:
            Conversational audio script
        """
        prompt = f"""You are an engaging ML educator creating an audio lesson script.

Topic: {topic}
Duration: {length} (Brief: 2-3 min, Medium: 5-8 min, Comprehensive: 10-15 min)

Create a conversational, engaging script that:
1. Starts with a hook/interesting question
2. Explains the concept clearly WITHOUT jargon overload
3. Includes one or two practical examples
4. Has natural transitions and pauses markers [PAUSE]
5. Ends with key takeaways and next steps

Write in a conversational tone as if explaining to a student during office hours."""
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating audio script: {str(e)}"
    
    def generate_image_prompt(self, concept: str, diagram_type: str = "Conceptual") -> str:
        """
        Generate detailed prompts for educational diagram creation
        Args:
            concept: ML concept to visualize
            diagram_type: "Conceptual", "Technical", "Flowchart"
        Returns:
            Detailed prompt for image generation
        """
        prompt = f"""Create a detailed visual prompt for generating an educational diagram explaining the following concept:

Topic: {concept}
Diagram Type: {diagram_type}

The prompt should be detailed and specific for an image generation model, including:
1. Visual style (clean, professional, educational)
2. Main elements and their relationships
3. Color scheme suggestions
4. Text labels and annotations
5. Composition and layout
6. Any specific visual metaphors or approaches

Provide a single, comprehensive prompt suitable for image generation AI."""
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating image prompt: {str(e)}"
    
    def detect_dependencies(self, code: str) -> List[str]:
        """
        Detect Python dependencies from generated code using AST
        Args:
            code: Python code to analyze
        Returns:
            List of required dependencies
        """
        import ast
        import re
        
        dependencies = set()
        
        try:
            tree = ast.parse(code)
            
            # Find imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        if module != '__main__':
                            dependencies.add(module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        if module != '__main__':
                            dependencies.add(module)
            
            # Map common module names to package names
            mapping = {
                'cv2': 'opencv-python',
                'sklearn': 'scikit-learn',
                'PIL': 'Pillow',
                'yaml': 'PyYAML'
            }
            
            detected = []
            for dep in dependencies:
                detected.append(mapping.get(dep, dep))
            
            return sorted(list(set(detected)))
        except SyntaxError:
            return []

# Create global instance
gemini_utils = None

def init_gemini(api_key: Optional[str] = None):
    """Initialize the Gemini utility module"""
    global gemini_utils
    gemini_utils = GeminiAIUtils(api_key)
    return gemini_utils

def get_gemini():
    """Get the Gemini utility instance"""
    global gemini_utils
    if gemini_utils is None:
        gemini_utils = GeminiAIUtils()
    return gemini_utils
