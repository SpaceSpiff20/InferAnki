#!/usr/bin/env python3
"""
Simple test suite for Speechify TTS migration
Tests core TTS functionality without Anki dependencies
"""

import unittest
import tempfile
import os
import json
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock Anki environment before importing
sys.modules['aqt'] = Mock()
sys.modules['aqt.utils'] = Mock()
sys.modules['aqt'] = Mock()
sys.modules['anki.utils'] = Mock()

# Mock Speechify
sys.modules['speechify'] = Mock()
sys.modules['speechify.tts'] = Mock()

# Add the InferAnki directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'InferAnki'))

class TestSpeechifySimple(unittest.TestCase):
    """Simple test cases for Speechify TTS migration"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            "debug_mode": False,
            "tts_enabled": True,
            "tts_voice": "Emma",
            "tts_max_chars": 40000,
            "speechify_api_key": "test_api_key",
            "speechify_voice_id": "scott",
            "speechify_model": "simba-multilingual",
            "speechify_language_code": "nb-NO",
            "speechify_audio_format": "mp3",
            "speechify_loudness_normalization": True,
            "speechify_text_normalization": True,
            "elevenlabs_speech_rate": 0.8
        }
    
    def test_import_speechify_processor(self):
        """Test that SpeechifyTTSProcessor can be imported"""
        try:
            # Import directly from the file to avoid Anki dependencies
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tts_handler", 
                os.path.join(os.path.dirname(__file__), 'InferAnki', 'functions', 'tts_handler.py')
            )
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            
            # Test that the class exists
            self.assertTrue(hasattr(tts_module, 'SpeechifyTTSProcessor'))
            self.assertTrue(hasattr(tts_module, 'ElevenLabsTTSProcessor'))
            self.assertTrue(hasattr(tts_module, 'TTSHandler'))
            self.assertTrue(hasattr(tts_module, 'TTSProcessor'))
            
        except Exception as e:
            self.fail(f"Failed to import TTS handler: {e}")
    
    def test_text_processing_logic(self):
        """Test text processing logic without full initialization"""
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tts_handler", 
                os.path.join(os.path.dirname(__file__), 'InferAnki', 'functions', 'tts_handler.py')
            )
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            
            # Create processor instance
            processor = tts_module.SpeechifyTTSProcessor(self.test_config)
            
            # Test HTML cleaning
            test_text = "<b>Hello</b> <br> World <br><br> Test"
            processed = processor.process_text_for_tts(test_text)
            self.assertIn("Hello", processed)
            self.assertIn("World", processed)
            self.assertNotIn("<b>", processed)
            self.assertNotIn("<br>", processed)
            
            # Test Norwegian text processing
            norwegian_text = "hei | verden - test < >"
            processed = processor.process_text_for_tts(norwegian_text)
            self.assertIn("hei, verden, test", processed)
            
        except Exception as e:
            self.fail(f"Text processing test failed: {e}")
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tts_handler", 
                os.path.join(os.path.dirname(__file__), 'InferAnki', 'functions', 'tts_handler.py')
            )
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            
            # Create processor instance
            processor = tts_module.SpeechifyTTSProcessor(self.test_config)
            
            # Test configuration loading
            self.assertEqual(processor.api_key, "test_api_key")
            self.assertEqual(processor.voice_id, "scott")
            self.assertEqual(processor.model, "simba-multilingual")
            self.assertEqual(processor.language_code, "nb-NO")
            self.assertEqual(processor.audio_format, "mp3")
            self.assertTrue(processor.enabled)
            
        except Exception as e:
            self.fail(f"Configuration loading test failed: {e}")
    
    def test_voice_mapping(self):
        """Test Norwegian voice mapping"""
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tts_handler", 
                os.path.join(os.path.dirname(__file__), 'InferAnki', 'functions', 'tts_handler.py')
            )
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            
            # Test Emma voice mapping
            config_emma = self.test_config.copy()
            config_emma["tts_voice"] = "Emma"
            processor = tts_module.SpeechifyTTSProcessor(config_emma)
            self.assertEqual(processor.voice_id, "scott")
            
            # Test custom voice ID
            config_custom = self.test_config.copy()
            config_custom["speechify_voice_id"] = "custom_voice"
            processor = tts_module.SpeechifyTTSProcessor(config_custom)
            self.assertEqual(processor.voice_id, "custom_voice")
            
        except Exception as e:
            self.fail(f"Voice mapping test failed: {e}")
    
    def test_audio_formats(self):
        """Test different audio format support"""
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "tts_handler", 
                os.path.join(os.path.dirname(__file__), 'InferAnki', 'functions', 'tts_handler.py')
            )
            tts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tts_module)
            
            supported_formats = ["aac", "mp3", "ogg", "wav"]
            
            for audio_format in supported_formats:
                config = self.test_config.copy()
                config["speechify_audio_format"] = audio_format
                
                processor = tts_module.SpeechifyTTSProcessor(config)
                self.assertEqual(processor.audio_format, audio_format)
                
        except Exception as e:
            self.fail(f"Audio formats test failed: {e}")

class TestConfigurationFiles(unittest.TestCase):
    """Test configuration file structure"""
    
    def test_config_file_structure(self):
        """Test that config.json has correct structure"""
        config_path = os.path.join(os.path.dirname(__file__), 'InferAnki', 'config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check for Speechify settings
            self.assertIn('speechify_api_key', config)
            self.assertIn('speechify_voice_id', config)
            self.assertIn('speechify_model', config)
            self.assertIn('speechify_language_code', config)
            self.assertIn('speechify_audio_format', config)
            
            # Check that tts_engine is set to speechify
            self.assertEqual(config.get('tts_engine'), 'speechify')
        else:
            self.fail("config.json file not found")
    
    def test_requirements_file(self):
        """Test that requirements.txt includes speechify-api"""
        requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                requirements = f.read()
            
            self.assertIn('speechify-api', requirements)
        else:
            self.fail("requirements.txt file not found")

def run_simple_tests():
    """Run simplified migration tests"""
    print("Running Simple Speechify Migration Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestSpeechifySimple))
    suite.addTest(unittest.makeSuite(TestConfigurationFiles))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_simple_tests()
    sys.exit(0 if success else 1) 