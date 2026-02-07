"""
Groq AI Integration Module
Handles text and image generation using Groq's API
"""

from groq import Groq
import os
from typing import Optional, List
import json

class GroqAIUtils:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq AI with API key"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        # Set the environment variable for Groq SDK
        if self.api_key:
            os.environ['GROQ_API_KEY'] = self.api_key
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"  # Fast & stable model (recommended for hackathon)
        
    def generate_text_explanation(self, topic: str, complexity_level: str = "Intermediate") -> str:
        """
        Generate comprehensive text explanation for ML topics
        Args:
            topic: ML topic to explain
            complexity_level: "Beginner", "Intermediate", "Comprehensive"
        Returns:
            Structured explanation text
        """
        prompt = f"""You are an expert ML educator. Provide a comprehensive explanation of the following topic: {topic}.

Your response should be structured in markdown format with clear headings and sections.

Cover the following aspects:

- Basic definition and intuition
- Key concepts and terminology
- Mathematical foundations (if applicable)
- Practical applications
- Common pitfalls and best practices

Keep the explanation educational, clear, and engaging. Use simple language and avoid jargon where possible.

IMPORTANT: Provide ONLY text explanation. Absolutely NO code, NO code snippets, NO code examples, NO programming code at all. Even if the topic involves algorithms or programming concepts, explain them in plain text without writing any code. Focus purely on explanatory prose.

Include these sections (use headings):
1. Brief Overview (2-3 sentences)
2. Key Concepts (bullet points)
3. Intuition (plain-language explanation)
4. Mathematical Foundation (only if applicable; keep concise)
5. Practical Examples (real-world use-cases; not full code)
6. Common Misconceptions
7. Resources for Further Learning
"""
        
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=2000,
            )
            return message.choices[0].message.content
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
        # Determine code type based on algorithm topic
        algorithm_lower = algorithm.lower()
        
        if any(keyword in algorithm_lower for keyword in ['neural network', 'cnn', 'rnn', 'lstm', 'transformer']):
            code_type = "neural network implementation"
        elif any(keyword in algorithm_lower for keyword in ['linear regression', 'logistic regression', 'svm', 'decision tree', 'random forest']):
            code_type = "machine learning model implementation"
        elif any(keyword in algorithm_lower for keyword in ['preprocessing', 'feature engineering', 'data cleaning']):
            code_type = "data preprocessing pipeline"
        elif any(keyword in algorithm_lower for keyword in ['clustering', 'pca', 'dimensionality']):
            code_type = "unsupervised learning algorithm"
        elif any(keyword in algorithm_lower for keyword in ['evaluation', 'metrics', 'validation']):
            code_type = "model evaluation and metrics"
        else:
            code_type = "machine learning algorithm implementation"
        
        prompt = f"""You are an expert Python developer specializing in machine learning. Generate a complete, runnable Python code example for {code_type} of "{algorithm}".

Requirements for {complexity} complexity:
1. Include all necessary imports at the top
2. Create a well-structured class or function with proper docstrings
3. Add comprehensive inline comments explaining the code logic
4. Include example usage with sample data
5. Add error handling where appropriate
6. Follow Python best practices and PEP 8 style

The code should be immediately executable and demonstrate the {algorithm} concept clearly.

Format as complete Python code that can be copied and run."""
        
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=2000,
            )
            return message.choices[0].message.content
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
4. Has natural transitions and pauses marked with [PAUSE]
5. Ends with key takeaways and next steps

Write in a conversational tone as if explaining to a student during office hours."""
        
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=1500,
            )
            return message.choices[0].message.content
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
            message = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.6,
                max_tokens=800,
            )
            return message.choices[0].message.content
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
groq_utils = None

def init_groq(api_key: Optional[str] = None):
    """Initialize the Groq utility module"""
    global groq_utils
    groq_utils = GroqAIUtils(api_key)
    return groq_utils

def get_groq():
    """Get the Groq utility instance"""
    global groq_utils
    if groq_utils is None:
        groq_utils = GroqAIUtils()
    return groq_utils

# Keep backward compatibility
GeminiAIUtils = GroqAIUtils
gemini_utils = groq_utils
init_gemini = init_groq
get_gemini = get_groq
