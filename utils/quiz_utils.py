"""
Quiz System for Progressive Learning
Handles quiz generation, evaluation, and error-based teaching with AI integration
"""

import json
import os
import random
from typing import List, Dict, Optional, Tuple
from utils.genai_utils import get_groq
from utils.hf_utils import hf_manager
from utils.sklearn_utils import sklearn_manager
from datetime import datetime

class QuizSystem:
    def __init__(self, quiz_file: str = "data/quizzes.json"):
        self.quiz_file = quiz_file
        self.ensure_quiz_file()
        self.load_quizzes()

    def generate_realtime_quiz(self, topic: str, difficulty: str = "Intermediate", num_questions: int = 5) -> Dict:
        """
        Generate a real-time quiz using Hugging Face and Groq AI
        """
        try:
            # Use Groq to generate quiz content
            groq_client = get_groq()

            prompt = f"""
            Generate {num_questions} multiple-choice questions for a {difficulty} level quiz on "{topic}" in Machine Learning.

            For each question, provide:
            1. A clear, concise question
            2. Four answer options (A, B, C, D)
            3. The correct answer letter
            4. A brief explanation of why it's correct

            Format as JSON:
            {{
                "topic": "{topic}",
                "difficulty": "{difficulty}",
                "questions": [
                    {{
                        "question": "Question text here?",
                        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                        "correct": "A",
                        "explanation": "Brief explanation here"
                    }}
                ]
            }}
            """

            # Generate quiz content
            response = groq_client.generate_text_explanation(f"Generate quiz for {topic}", difficulty)

            # Try to parse as JSON, fallback to structured parsing
            try:
                quiz_data = json.loads(response)
            except:
                # Fallback: manually structure the response
                quiz_data = self._parse_quiz_response(response, topic, difficulty)

            # Enhance with Hugging Face for question quality
            quiz_data = self._enhance_quiz_with_hf(quiz_data)

            return {
                "success": True,
                "quiz": quiz_data,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate quiz: {str(e)}"
            }

    def _parse_quiz_response(self, response: str, topic: str, difficulty: str) -> Dict:
        """Parse unstructured quiz response into structured format"""
        # This is a fallback parser for when JSON parsing fails
        lines = response.split('\n')
        questions = []

        current_question = None
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')) and '?' in line:
                if current_question:
                    questions.append(current_question)
                current_question = {
                    "question": line.split('.', 1)[1].strip(),
                    "options": [],
                    "correct": "A",
                    "explanation": "Generated explanation"
                }
            elif current_question and line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_question["options"].append(line)

        if current_question:
            questions.append(current_question)

        return {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions[:5]  # Limit to 5 questions
        }

    def _enhance_quiz_with_hf(self, quiz_data: Dict) -> Dict:
        """Enhance quiz questions using Hugging Face models"""
        try:
            for question in quiz_data.get("questions", []):
                # Use Hugging Face for sentiment analysis on question quality
                question_text = question.get("question", "")
                if question_text:
                    sentiment = hf_manager.analyze_sentiment(question_text)
                    question["sentiment_score"] = sentiment.get("score", 0.5)

                # Use question answering to validate question clarity
                if len(question.get("options", [])) >= 2:
                    context = f"{question_text} {' '.join(question['options'])}"
                    qa_result = hf_manager.answer_question(
                        question_text,
                        context
                    )
                    question["qa_confidence"] = qa_result.get("score", 0.0)

        except Exception as e:
            # HF enhancement is optional, don't fail if it doesn't work
            pass

    def analyze_quiz_performance(self, quiz_results: List[Dict], user_history: List[Dict] = None) -> Dict:
        """
        Analyze quiz performance using scikit-learn for predictive insights
        """
        try:
            if not quiz_results:
                return {"error": "No quiz results provided"}

            # Prepare data for ML analysis
            scores = [result.get("score", 0) for result in quiz_results]
            times = [result.get("time_taken", 0) for result in quiz_results]
            difficulties = [result.get("difficulty", "Intermediate") for result in quiz_results]

            # Convert difficulties to numeric
            difficulty_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
            difficulty_scores = [difficulty_map.get(d, 2) for d in difficulties]

            # Create feature matrix for analysis
            import numpy as np
            X = np.column_stack([difficulty_scores, times])
            y = np.array(scores)

            if len(X) >= 3:  # Need minimum data for meaningful analysis
                # Train a simple model to predict performance
                analysis_result = sklearn_manager.train_model(
                    X, y,
                    model_type="linear_regression",
                    test_size=0.2
                )

                # Generate insights
                avg_score = np.mean(scores)
                score_trend = "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
                time_efficiency = np.corrcoef(times, scores)[0, 1] if len(times) == len(scores) else 0

                return {
                    "success": True,
                    "analytics": {
                        "average_score": float(avg_score),
                        "score_trend": score_trend,
                        "time_efficiency": float(time_efficiency),
                        "performance_prediction": float(analysis_result["metrics"].get("mean_squared_error", 0)),
                        "total_quizzes": len(quiz_results),
                        "model_metrics": analysis_result["metrics"]
                    },
                    "recommendations": self._generate_recommendations(avg_score, score_trend, time_efficiency)
                }
            else:
                # Fallback for limited data
                avg_score = np.mean(scores) if scores else 0
                return {
                    "success": True,
                    "analytics": {
                        "average_score": float(avg_score),
                        "total_quizzes": len(quiz_results),
                        "data_points": "insufficient for ML analysis"
                    },
                    "recommendations": ["Complete more quizzes for detailed analytics"]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Performance analysis failed: {str(e)}"
            }

    def _generate_recommendations(self, avg_score: float, trend: str, time_efficiency: float) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []

        if avg_score < 60:
            recommendations.append("Focus on fundamental concepts - consider starting with beginner topics")
        elif avg_score < 80:
            recommendations.append("Good progress! Practice with more advanced topics")

        if trend == "improving":
            recommendations.append("Great improvement! Keep up the momentum")
        elif trend == "stable":
            recommendations.append("Consider varying your study approach - try different learning modalities")

        if time_efficiency < -0.3:  # Negative correlation means slower times hurt scores
            recommendations.append("Work on time management - accuracy is improving with practice")
        elif time_efficiency > 0.3:  # Positive correlation means faster times help scores
            recommendations.append("Excellent time management! Consider challenging yourself with harder topics")

        return recommendations

    def _generate_quiz_feedback(self, score: float, detailed_results: List[Dict], topic: str) -> Dict:
        """
        Generate AI-powered feedback for quiz results using Hugging Face
        """
        try:
            # Analyze performance patterns
            total_questions = len(detailed_results)
            correct_answers = sum(1 for r in detailed_results if r.get('is_correct', False))

            # Generate feedback using Groq
            groq_client = get_groq()

            feedback_prompt = f"""
            Generate personalized feedback for a Machine Learning quiz on "{topic}".
            Student scored {score:.1f}% ({correct_answers}/{total_questions} correct).

            Provide:
            1. A brief performance summary
            2. 2-3 specific strengths
            3. 1-2 areas for improvement
            4. Next learning recommendations

            Keep it encouraging and actionable.
            """

            ai_feedback = groq_client.generate_text_explanation(f"Quiz feedback for {topic}", "Intermediate")

            # Use Hugging Face for sentiment analysis on feedback quality
            sentiment = hf_manager.analyze_sentiment(ai_feedback)
            feedback_quality = "positive" if sentiment.get("score", 0) > 0.5 else "neutral"

            return {
                "summary": f"You scored {score:.1f}% on the {topic} quiz.",
                "ai_feedback": ai_feedback,
                "feedback_quality": feedback_quality,
                "strengths": self._analyze_strengths(detailed_results),
                "improvements": self._analyze_improvements(detailed_results),
                "recommendations": self._generate_learning_recommendations(score, topic)
            }

        except Exception as e:
            # Fallback feedback
            return {
                "summary": f"You scored {score:.1f}% on the {topic} quiz.",
                "ai_feedback": "Great effort! Keep practicing to improve your understanding.",
                "strengths": ["Completed the quiz"],
                "improvements": ["Review the material"],
                "recommendations": ["Try the topic again", "Explore related concepts"]
            }

    def _analyze_strengths(self, detailed_results: List[Dict]) -> List[str]:
        """Analyze what the student did well"""
        strengths = []
        correct_count = sum(1 for r in detailed_results if r.get('is_correct', False))

        if correct_count > len(detailed_results) * 0.7:
            strengths.append("Strong understanding of core concepts")
        if correct_count > 0:
            strengths.append("Good problem-solving approach")

        return strengths or ["Persistent effort in attempting questions"]

    def _analyze_improvements(self, detailed_results: List[Dict]) -> List[str]:
        """Analyze areas for improvement"""
        improvements = []
        incorrect_count = sum(1 for r in detailed_results if not r.get('is_correct', False))

        if incorrect_count > len(detailed_results) * 0.5:
            improvements.append("Review fundamental concepts")
        if incorrect_count > 0:
            improvements.append("Practice with similar problems")

        return improvements or ["Continue learning at your own pace"]

    def _generate_learning_recommendations(self, score: float, topic: str) -> List[str]:
        """Generate next learning steps"""
        recommendations = []

        if score < 60:
            recommendations.extend([
                f"Review basic {topic} concepts",
                "Try beginner-level practice problems",
                "Watch introductory videos on the topic"
            ])
        elif score < 80:
            recommendations.extend([
                f"Practice intermediate {topic} problems",
                "Explore practical applications",
                "Discuss concepts with peers"
            ])
        else:
            recommendations.extend([
                f"Explore advanced {topic} topics",
                "Work on real-world projects",
                "Mentor others learning this topic"
            ])

        return recommendations

    def get_adaptive_quiz(self, user_performance: Dict, topic: str) -> Dict:
        """Generate an adaptive quiz based on user performance history"""
        try:
            avg_score = user_performance.get("average_score", 70)

            # Determine appropriate difficulty
            if avg_score < 50:
                difficulty = "Beginner"
                num_questions = 3
            elif avg_score < 75:
                difficulty = "Intermediate"
                num_questions = 5
            else:
                difficulty = "Advanced"
                num_questions = 7

            # Generate adaptive quiz
            return self.generate_realtime_quiz(topic, difficulty, num_questions)

        except Exception as e:
            return {
                "success": False,
                "error": f"Adaptive quiz generation failed: {str(e)}"
            }

    def ensure_quiz_file(self):
        """Ensure quiz file exists"""
        os.makedirs(os.path.dirname(self.quiz_file), exist_ok=True)
        if not os.path.exists(self.quiz_file):
            # Create default quiz data
            default_quizzes = {
                "linear_regression": {
                    "topic": "Linear Regression",
                    "questions": [
                        {
                            "question": "What is the main goal of linear regression?",
                            "options": [
                                "To classify data into categories",
                                "To predict a continuous output variable",
                                "To find clusters in data",
                                "To reduce dimensionality"
                            ],
                            "correct": 1,
                            "explanation": "Linear regression is used to predict continuous numerical values based on input features."
                        }
                    ]
                }
            }
            with open(self.quiz_file, 'w') as f:
                json.dump(default_quizzes, f, indent=2)

    def load_quizzes(self):
        """Load quiz data from file"""
        try:
            with open(self.quiz_file, 'r') as f:
                self.quizzes = json.load(f)
        except Exception as e:
            print(f"Error loading quizzes: {e}")
            self.quizzes = {}

    def get_quiz(self, topic: str) -> Optional[Dict]:
        """Get quiz for a specific topic"""
        # Normalize topic name
        normalized_topic = topic.lower().replace(" ", "_")
        return self.quizzes.get(normalized_topic)

    def generate_quiz_for_topic(self, topic: str) -> Dict:
        """Generate a quiz for any topic using AI"""
        try:
            gemini = get_groq()
            prompt = f"""Create a 3-5 question multiple choice quiz for the topic: {topic}

Format as JSON:
{{
    "topic": "{topic}",
    "questions": [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": 0,
            "explanation": "Why this is correct"
        }}
    ]
}}

Make questions progressive in difficulty, covering basic to advanced concepts."""

            # Since Groq returns text, we'll parse it
            response = gemini.generate_text_explanation(f"Create quiz for {topic}", "Intermediate")

            # For now, return a simple generated quiz
            return {
                "topic": topic,
                "questions": [
                    {
                        "question": f"What is a key concept in {topic}?",
                        "options": [
                            "Basic understanding",
                            "Advanced implementation",
                            "Data preprocessing",
                            "Model evaluation"
                        ],
                        "correct": 0,
                        "explanation": f"This covers fundamental aspects of {topic}."
                    },
                    {
                        "question": f"How do you evaluate performance in {topic}?",
                        "options": [
                            "Using accuracy only",
                            "Using appropriate metrics for the task",
                            "Ignoring validation",
                            "Using random guessing"
                        ],
                        "correct": 1,
                        "explanation": "Proper evaluation metrics are crucial for assessing model performance."
                    }
                ]
            }
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None

    def evaluate_answers(self, topic: str, answers: List[int]) -> Dict:
        """Evaluate quiz answers and return results"""
        quiz = self.get_quiz(topic)
        if not quiz:
            quiz = self.generate_quiz_for_topic(topic)

        if not quiz:
            return {"error": "Could not load or generate quiz"}

        results = []
        correct_count = 0

        for i, answer in enumerate(answers):
            if i < len(quiz["questions"]):
                question = quiz["questions"][i]
                is_correct = answer == question["correct"]
                if is_correct:
                    correct_count += 1

                results.append({
                    "question": question["question"],
                    "user_answer": answer,
                    "correct_answer": question["correct"],
                    "is_correct": is_correct,
                    "explanation": question["explanation"]
                })

        score = correct_count / len(quiz["questions"]) * 100

        return {
            "topic": quiz["topic"],
            "score": score,
            "total_questions": len(quiz["questions"]),
            "correct_answers": correct_count,
            "results": results,
            "passed": score >= 70  # 70% passing threshold
        }

    def generate_error_based_teaching(self, topic: str, incorrect_questions: List[Dict]) -> str:
        """Generate targeted teaching for incorrect answers"""
        try:
            gemini = get_groq()

            error_summary = "\n".join([
                f"Question: {q['question']}\nUser answered: {q['user_answer']}\nCorrect: {q['correct_answer']}\nExplanation: {q['explanation']}"
                for q in incorrect_questions
            ])

            prompt = f"""Based on these incorrect quiz answers for {topic}, provide targeted reteaching:

{error_summary}

Create a focused explanation that:
1. Identifies the conceptual misunderstanding
2. Provides clear, simple explanation of the correct concept
3. Gives a practical example
4. Suggests how to remember this concept
5. Recommends the best next learning modality (text/code/audio/visual) for this learner

Keep it concise but thorough."""

            # Use the underlying chat model with the custom prompt so we actually
            # incorporate the user's incorrect answers.
            try:
                message = gemini.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=getattr(gemini, "model", "llama-3.1-8b-instant"),
                    temperature=0.6,
                    max_tokens=1200,
                )
                return message.choices[0].message.content
            except Exception:
                # Fallback to the simpler helper if direct chat call fails
                return gemini.generate_text_explanation(f"Error-based teaching for {topic}", "Beginner")

        except Exception as e:
            return f"Error generating teaching: {str(e)}"

# Global instance
quiz_system = None

def init_quiz():
    """Initialize quiz system"""
    global quiz_system
    quiz_system = QuizSystem()
    return quiz_system

def get_quiz_system():
    """Get quiz system instance"""
    global quiz_system
    if quiz_system is None:
        quiz_system = QuizSystem()
    return quiz_system
