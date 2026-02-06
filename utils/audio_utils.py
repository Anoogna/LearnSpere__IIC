"""
Audio Processing Module
Handles text-to-speech conversion and audio file management
"""

import os
from gtts import gTTS
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

class AudioUtils:
    def __init__(self, output_dir: str = "uploads/audio"):
        """
        Initialize audio utilities
        Args:
            output_dir: Directory to store generated audio files
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    def generate_audio(self, text: str, language: str = "en", 
                      slow: bool = False) -> Optional[Tuple[str, str]]:
        """
        Convert text to speech using gTTS
        Args:
            text: Text to convert to audio
            language: Language code (default: 'en' for English)
            slow: If True, speaks more slowly
        Returns:
            Tuple of (file_path, file_url) or None if error
        """
        try:
            # Clean text for file naming
            filename_text = text[:30].replace(' ', '_').replace('\n', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{filename_text}_{timestamp}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate audio
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(filepath)
            
            # Return relative path for web access
            web_path = filepath.replace('\\', '/')
            return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None
    
    def generate_educational_audio(self, script: str, topic: str = "ML Lesson",
                                  speed: float = 1.0) -> Optional[Tuple[str, str]]:
        """
        Generate audio from educational script
        Args:
            script: Educational content script (audio format)
            topic: Topic name for file naming
            speed: Playback speed (1.0 = normal, 0.8 = slower, 1.2 = faster)
        Returns:
            Tuple of (file_path, file_url) or None if error
        """
        try:
            # Remove markers like [PAUSE]
            clean_script = script.replace('[PAUSE]', ' ')
            
            # Limit length for practical purposes
            if len(clean_script) > 5000:
                clean_script = clean_script[:5000] + "..."
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lesson_{topic.replace(' ', '_')}_{timestamp}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            tts = gTTS(text=clean_script, lang='en', slow=(speed < 1.0))
            tts.save(filepath)
            
            web_path = filepath.replace('\\', '/')
            return filepath, f"/{web_path}"
        except Exception as e:
            print(f"Error generating educational audio: {str(e)}")
            return None
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """
        Clean up audio files older than specified days
        Args:
            days: Number of days to keep files
        Returns:
            Number of files deleted
        """
        import time
        
        deleted_count = 0
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
        except Exception as e:
            print(f"Error cleaning up old files: {str(e)}")
        
        return deleted_count
    
    def get_file_size(self, filepath: str) -> str:
        """
        Get human-readable file size
        Args:
            filepath: Path to the file
        Returns:
            Formatted file size string
        """
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} GB"
        except:
            return "Unknown"
    
    def list_generated_files(self) -> list:
        """
        List all generated audio files
        Returns:
            List of file information dictionaries
        """
        files = []
        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'filename': filename,
                        'path': f"/{filepath.replace(chr(92), '/')}",
                        'size': self.get_file_size(filepath),
                        'created': datetime.fromtimestamp(
                            os.path.getmtime(filepath)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            print(f"Error listing files: {str(e)}")
        
        return sorted(files, key=lambda x: x['created'], reverse=True)

# Create global instance
audio_utils = None

def init_audio(output_dir: str = "uploads/audio"):
    """Initialize the audio utility module"""
    global audio_utils
    audio_utils = AudioUtils(output_dir)
    return audio_utils

def get_audio():
    """Get the audio utility instance"""
    global audio_utils
    if audio_utils is None:
        audio_utils = AudioUtils()
    return audio_utils
