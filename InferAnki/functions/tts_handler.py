import os
import re
import tempfile
import json
import base64
from datetime import datetime
from pathlib import Path

# Anki imports - make optional for testing
try:
    from aqt.utils import showInfo, showCritical # type: ignore
    from aqt import mw # type: ignore
    from anki.utils import stripHTML # type: ignore
    ANKI_AVAILABLE = True
except ImportError:
    # Mock functions for testing outside Anki
    def showInfo(msg): print(f"INFO: {msg}")
    def showCritical(msg): print(f"CRITICAL: {msg}")
    def stripHTML(text): return re.sub(r'<[^>]+>', '', text)
    mw = None
    ANKI_AVAILABLE = False

# Speechify API imports
try:
    from speechify import Speechify
    from speechify.tts import GetSpeechOptionsRequest
    SPEECHIFY_AVAILABLE = True
except ImportError:
    SPEECHIFY_AVAILABLE = False

class SpeechifyTTSProcessor:
    """Handle Speechify TTS processing for Anki cards with Norwegian optimization"""
    
    def __init__(self, config):
        self.config = config
        self.language = config.get("tts_language", "no")  # Norwegian ISO 639-3 code
        self.enabled = config.get("tts_enabled", True)
        self.max_chars = config.get("tts_max_chars", 40000)  # Speechify supports large text
        self.field_index = 1  # Always use field index 1 (second field) for TTS
        
        # Speechify TTS configuration
        self.api_key = config.get("speechify_api_key", "")
        self.voice_id = config.get("speechify_voice_id", "scott")  # Default to scott
        self.voice_name = config.get("tts_voice", "Emma")  # Default to Emma (Norwegian native)
        self.model = config.get("speechify_model", "simba-multilingual")  # Multilingual model for Norwegian support
        self.language_code = config.get("speechify_language_code", "nb-NO")  # Norwegian Bokmål
        self.audio_format = config.get("speechify_audio_format", "mp3")
        
        # Speechify advanced options
        self.loudness_normalization = config.get("speechify_loudness_normalization", True)
        self.text_normalization = config.get("speechify_text_normalization", True)
        
        # Backward compatibility with ElevenLabs settings
        self.speech_rate = config.get("elevenlabs_speech_rate", 0.8)  # Speech rate: 0.5-2.0 (0.8 = 20% slower)
        
        # Norwegian voice recommendations for Speechify
        self.norwegian_voices = {
            "Emma": "scott",       # Default Norwegian voice
            "Rachel": "scott",     # Fallback to scott
            "Domi": "scott",       # Fallback to scott
            "Bella": "scott",      # Fallback to scott
            "Antoni": "scott",     # Fallback to scott
            "Josh": "scott",       # Fallback to scott
            "Arnold": "scott",     # Fallback to scott
            "Adam": "scott",       # Fallback to scott
            "Sam": "scott"         # Fallback to scott
        }
        
        # Set voice ID based on voice name (only if no custom voice_id is provided)
        if not self.voice_id or self.voice_id == "scott":
            if self.voice_name in self.norwegian_voices:
                self.voice_id = self.norwegian_voices[self.voice_name]
            else:
                self.voice_id = "scott"  # Default to scott
        
        # Check API availability
        if not SPEECHIFY_AVAILABLE:
            showCritical("Speechify TTS requires 'speechify-api' library")
            self.enabled = False
        elif not self.api_key or self.api_key == "your-api-key-here":
            if config.get("debug_mode", False):
                showInfo("Speechify API key not configured in config.json")
    
    def process_text_for_tts(self, text):
        """Process text with comprehensive HTML cleaning for Norwegian TTS"""
        if not text or not isinstance(text, str):
            return ""
        input_text = text.strip()
        
        # DEBUG: Add version marker to logs to confirm new code is running
        debug_marker = " [v0.6.0-SPEECHIFY]"
        
        # FIRST: Remove 🔸 bullet content (improved logic)
        # Pattern 1: 🔸 content with <br><br> ending
        input_text = re.sub(r'(?:<[^>]*>)?🔸.*?<br\s*/?>\s*<br\s*/?>', '', input_text, flags=re.IGNORECASE | re.DOTALL)
        # Pattern 2: 🔸 content at end of text
        input_text = re.sub(r'(?:<[^>]*>)?🔸.*$', '', input_text, flags=re.IGNORECASE | re.DOTALL)
        
        # SECOND: Convert HTML entities BEFORE tag removal (but keep &lt; and &gt; for now)
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&quot;': '"',
            '&apos;': "'",
            '&#39;': "'",
            '&mdash;': '—',
            '&ndash;': '–',
            '&hellip;': '...',
            '&rsquo;': "'",
            '&lsquo;': "'",
            '&rdquo;': '"',
            '&ldquo;': '"'
        }
        
        for entity, replacement in html_entities.items():
            input_text = input_text.replace(entity, replacement)
        
        # THIRD: Handle HTML tags with content preservation
        # Replace <br><br> (double) with longer pause for clear separation
        input_text = re.sub(r'<br\s*/?>\s*<br\s*/?>', ' ... ', input_text, flags=re.IGNORECASE)
        # Replace single <br> with medium pause for word separation
        input_text = re.sub(r'<br\s*/?>', ' .. ', input_text, flags=re.IGNORECASE)
        
        # Handle list items - add pause between list items
        input_text = re.sub(r'</li>\s*<li[^>]*>', ' .. ', input_text, flags=re.IGNORECASE)
        input_text = re.sub(r'</?li[^>]*>', ' ', input_text, flags=re.IGNORECASE)
        input_text = re.sub(r'</?ul[^>]*>', ' ', input_text, flags=re.IGNORECASE)
        input_text = re.sub(r'</?ol[^>]*>', ' ', input_text, flags=re.IGNORECASE)
        
        # Handle div tags - add spacing between divs
        input_text = re.sub(r'</div>\s*<div[^>]*>', ' .. ', input_text, flags=re.IGNORECASE)
        input_text = re.sub(r'</?div[^>]*>', ' ', input_text, flags=re.IGNORECASE)
        
        # FOURTH: Strip remaining HTML tags (comprehensive approach)
        # Remove all HTML tags but preserve content
        input_text = re.sub(r'<[^>]+>', '', input_text)
        
        # FIFTH: Now convert remaining HTML entities that could interfere with text
        input_text = input_text.replace('&lt;', '<')
        input_text = input_text.replace('&gt;', '>')
        
        # SIXTH: Norwegian text processing
        # Handle pipe-separated words (Norwegian learning) - convert all | to commas
        input_text = re.sub(r'\s*\|\s*', ', ', input_text)
        
        # Handle dashes - convert to commas ONLY when surrounded by spaces (preserve within words like "PC-en")
        input_text = re.sub(r'\s+-\s+', ', ', input_text)
        
        # Handle angle brackets (< >) - convert to commas as well  
        input_text = re.sub(r'\s*<\s*', ', ', input_text)
        input_text = re.sub(r'\s*>\s*', ', ', input_text)
        
        # Force pause after every real linebreak
        input_text = re.sub(r'\r?\n+', ' ... ', input_text)
        
        # Convert multiple dots to pauses (use placeholders to prevent interference)
        input_text = re.sub(r'\.{4,}', '⟨LONG_PAUSE⟩', input_text)
        input_text = re.sub(r'\.{3}', '⟨LONG_PAUSE⟩', input_text)
        input_text = re.sub(r'\.{2}', '⟨MED_PAUSE⟩', input_text)
        
        # Convert placeholders to final pause format
        input_text = re.sub(r'⟨LONG_PAUSE⟩', ' ... ', input_text)
        input_text = re.sub(r'⟨MED_PAUSE⟩', ' .. ', input_text)
        
        # SEVENTH: Clean up spacing and whitespace
        input_text = re.sub(r'\s+', ' ', input_text)  # Multiple spaces to single
        input_text = input_text.strip()
        
        # LOG: Record processed text with version marker
        if self.config.get("debug_mode", False):
            try:
                logs_dir = r"a:\KODEKRAFT\PROJECTS\InferAnki\logs"
                os.makedirs(logs_dir, exist_ok=True)
                log_file = os.path.join(logs_dir, "convert.log")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] ORIGINAL: {repr(text)}\n")
                    f.write(f"[{timestamp}] PROCESSED{debug_marker}: {input_text}\n")
            except:
                pass

        # Apply speech rate control using SSML (if not default rate)
        if hasattr(self, 'speech_rate') and self.speech_rate != 1.0:
            input_text = f'<prosody rate="{self.speech_rate}">{input_text}</prosody>'
        
        # Final check - if result is empty, return empty
        if not input_text:
            return ""
      
        return input_text
    
    def create_audio_file(self, text):
        """Create MP3 audio file using Speechify TTS"""
        if not self.enabled or not SPEECHIFY_AVAILABLE:
            return None
            
        try:
            # Process text with SSML markup
            processed_text = self.process_text_for_tts(text)
            if not processed_text or not processed_text.strip():
                return None
            
            # Initialize Speechify client
            client = Speechify(token=self.api_key)
            
            # Prepare options
            options = GetSpeechOptionsRequest(
                loudness_normalization=self.loudness_normalization,
                text_normalization=self.text_normalization
            )
            
            # Make TTS request
            audio_response = client.tts.audio.speech(
                audio_format=self.audio_format,
                input=processed_text,
                language=self.language_code,
                model=self.model,
                options=options,
                voice_id=self.voice_id
            )
            
            # Decode audio data
            audio_bytes = base64.b64decode(audio_response.audio_data)
            
            # Create temporary file
            now = datetime.now().strftime('%y%m%d-%H%M%S')
            filename = f"inferanki-speechify-tts-{now}.{self.audio_format}"
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)
            
            # Save audio file
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            return temp_path
            
        except Exception as e:
            showCritical(f"Error creating Speechify TTS audio: {str(e)}")
            return None
    
    def get_field_content(self, editor):
        """Get raw HTML content from field index 1 (second field)"""
        try:
            if hasattr(editor, 'note') and editor.note and len(editor.note.fields) > 1:
                return editor.note.fields[1]  # Field index 1 (second field)
            return ""
        except Exception as e:
            if self.config.get("debug_mode", False):
                showCritical(f"Error getting field content: {str(e)}")
            return ""
    
    def clear_audio_field(self, editor):
        """Clear audio field without questions"""
        try:
            if hasattr(editor, 'note') and editor.note:
                audio_fields = ['Audio', 'audio', 'Sound', 'sound']
                for field in audio_fields:
                    if field in editor.note:
                        editor.note[field] = ""
                        break
        except Exception as e:
            pass
    
    def add_audio_to_note(self, editor, audio_path):
        """Add audio file to note"""
        try:
            if not os.path.exists(audio_path):
                showCritical("Audio file not found")
                return False
                
            filename = os.path.basename(audio_path)
            
            # Add file to Anki media collection (only if in Anki environment)
            if mw and hasattr(mw, 'col') and mw.col:
                media_name = mw.col.media.addFile(audio_path)
            else:
                media_name = filename
                showInfo(f"TEST MODE: Would add audio file {filename}")
            
            # Add audio reference to note
            if hasattr(editor, 'note') and editor.note:
                audio_fields = ['Audio', 'audio', 'Sound', 'sound']
                audio_field = None
                
                for field in audio_fields:
                    if field in editor.note:
                        audio_field = field
                        break
                
                if audio_field:
                    audio_tag = f"[sound:{media_name}]"
                    editor.note[audio_field] = audio_tag
                    return True
                else:
                    showCritical("No audio field found (looking for: Audio, audio, Sound, sound)")
                    return False
            
            return False
            
        except Exception as e:
            showCritical(f"Error adding audio to note: {str(e)}")
            return False
    
    def process_text(self, editor):
        """Main TTS processing function"""
        if not self.enabled:
            showInfo("Speechify TTS is disabled in configuration")
            return False
            
        if not SPEECHIFY_AVAILABLE:
            showCritical("Speechify TTS requires 'speechify-api' library")
            return False
        
        if not self.api_key or self.api_key == "your-api-key-here":
            showCritical("Speechify API key not configured. Please add 'speechify_api_key' to config.json")
            return False
            
        try:
            # Get text from field index 1 (second field)
            text = self.get_field_content(editor)
            
            if not text or not text.strip():
                showInfo(f"Field 2 (index 1) is empty. Please add text to generate TTS audio.")
                return False
                
            # Check character limit
            if len(text) > self.max_chars:
                showCritical(f"Text too long ({len(text)} chars). Max allowed: {self.max_chars}")
                return False
            
            # Clear existing audio (silent processing)
            self.clear_audio_field(editor)
            
            # Create audio file
            audio_path = self.create_audio_file(text)
            if not audio_path:
                showCritical("Failed to create audio file")
                return False
                
            # Add audio to note
            success = self.add_audio_to_note(editor, audio_path)
            if success:
                # Update editor display (only if in Anki environment)
                if ANKI_AVAILABLE and hasattr(editor, 'loadNote'):
                    editor.loadNote()
                
                # Clean up temporary file
                try:
                    os.remove(audio_path)
                except:
                    pass
                    
                return True
            else:
                showCritical("Failed to add audio to note")
                return False
                
        except Exception as e:
            showCritical(f"Speechify TTS processing error: {str(e)}")
            return False

# Maintain backward compatibility with old class names
ElevenLabsTTSProcessor = SpeechifyTTSProcessor
TTSHandler = SpeechifyTTSProcessor
TTSProcessor = SpeechifyTTSProcessor
