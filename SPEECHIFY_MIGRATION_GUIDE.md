# Speechify Migration Guide

This guide helps you migrate from ElevenLabs TTS to Speechify TTS in the InferAnki addon.

## Overview

The InferAnki addon has been successfully migrated from ElevenLabs TTS to Speechify TTS. This migration maintains backward compatibility while providing access to Speechify's advanced TTS capabilities.

## What's Changed

### ✅ Maintained Features
- All existing TTS functionality
- Norwegian language optimization
- HTML text processing
- Speech rate control
- Anki integration
- Button controls and UI

### 🔄 Updated Features
- **TTS Provider**: ElevenLabs → Speechify
- **API Integration**: New Speechify API client
- **Voice Options**: Updated voice mapping
- **Configuration**: New Speechify-specific settings

### 🆕 New Features
- **Multilingual Support**: Better language detection
- **Advanced Audio Options**: Loudness and text normalization
- **Multiple Audio Formats**: AAC, MP3, OGG, WAV support
- **Enhanced Voice Quality**: Speechify's latest models

## Installation

### 1. Install Speechify API
```bash
pip install speechify-api
```

### 2. Get Speechify API Key
1. Visit: https://console.sws.speechify.com/signup
2. Create an account and get your API key
3. Add the key to your `config.json`

### 3. Update Configuration

Edit your `InferAnki/config.json` file:

```json
{
  "tts_engine": "speechify",
  "speechify_api_key": "YOUR_SPEECHIFY_API_KEY_HERE",
  "speechify_voice_id": "scott",
  "speechify_model": "simba-multilingual",
  "speechify_language_code": "nb-NO",
  "speechify_audio_format": "mp3",
  "speechify_loudness_normalization": true,
  "speechify_text_normalization": true
}
```

## Configuration Options

### Required Settings
- `speechify_api_key`: Your Speechify API key
- `speechify_voice_id`: Voice ID (default: "scott")
- `speechify_model`: TTS model ("simba-english" or "simba-multilingual")

### Optional Settings
- `speechify_language_code`: Language code (e.g., "nb-NO" for Norwegian)
- `speechify_audio_format`: Audio format ("aac", "mp3", "ogg", "wav")
- `speechify_loudness_normalization`: Enable loudness normalization
- `speechify_text_normalization`: Enable text normalization

### Backward Compatibility
- `elevenlabs_speech_rate`: Still supported for speech rate control
- `tts_voice`: Voice name mapping (now maps to Speechify voices)

## Language Support

### Fully Supported Languages
| Language              | Code  |
|-----------------------|-------|
| English               | en    |
| French                | fr-FR |
| German                | de-DE |
| Spanish               | es-ES |
| Portuguese (Brazil)   | pt-BR |
| Portuguese (Portugal) | pt-PT |

### Beta Languages (Including Norwegian)
| Language   | Code  |
|------------|-------|
| Norwegian  | nb-NO |
| Arabic     | ar-AE |
| Danish     | da-DK |
| Dutch      | nl-NL |
| Estonian   | et-EE |
| Finnish    | fi-FI |
| Greek      | el-GR |
| Hebrew     | he-IL |
| Hindi      | hi-IN |
| Italian    | it-IT |
| Japanese   | ja-JP |
| Polish     | pl-PL |
| Russian    | ru-RU |
| Swedish    | sv-SE |
| Turkish    | tr-TR |
| Ukrainian  | uk-UA |
| Vietnamese | vi-VN |

## Voice Selection

### Default Voice
- **Voice ID**: "scott"
- **Model**: "simba-multilingual"
- **Language**: Norwegian Bokmål (nb-NO)

### Finding Available Voices
Use the provided `filter_voice_models` function to find voices:

```python
from speechify import Speechify

client = Speechify(token="YOUR_TOKEN")
voices = client.tts.voices.list()

# Filter by gender
male_voices = filter_voice_models(voices, gender="male")

# Filter by locale
norwegian_voices = filter_voice_models(voices, locale="nb-NO")

# Filter by tags
deep_voices = filter_voice_models(voices, tags=["timbre:deep"])
```

## Testing the Migration

### 1. Run the Test Suite
```bash
python test_speechify_migration.py
```

### 2. Manual Testing
1. Open Anki and create a new card
2. Add Norwegian text to field 2
3. Click the TTS button (👩🏼)
4. Verify audio is generated and added to the card

### 3. Check Logs
Enable debug mode in config.json to see detailed logs:
```json
{
  "debug_mode": true
}
```

## Troubleshooting

### Common Issues

#### 1. "Speechify TTS requires 'speechify-api' library"
**Solution**: Install the Speechify API library
```bash
pip install speechify-api
```

#### 2. "Speechify API key not configured"
**Solution**: Add your API key to config.json
```json
{
  "speechify_api_key": "YOUR_ACTUAL_API_KEY"
}
```

#### 3. "Error creating Speechify TTS audio"
**Solution**: Check your API key and internet connection

#### 4. Audio quality issues
**Solution**: Try different models or voice settings
```json
{
  "speechify_model": "simba-english",
  "speechify_loudness_normalization": true,
  "speechify_text_normalization": true
}
```

### Performance Optimization

#### 1. Audio Format Selection
- **MP3**: Good balance of quality and file size (default)
- **AAC**: Better quality, smaller files
- **WAV**: Highest quality, larger files
- **OGG**: Open format, good compression

#### 2. Model Selection
- **simba-multilingual**: Better for Norwegian and mixed languages
- **simba-english**: Optimized for English content

#### 3. Text Normalization
Enable text normalization for better pronunciation:
```json
{
  "speechify_text_normalization": true
}
```

## Backward Compatibility

### Old Configuration
Old ElevenLabs settings are automatically migrated:
- `elevenlabs_speech_rate` → Preserved for speech rate control
- `tts_voice` → Mapped to Speechify voices
- `tts_max_chars` → Preserved for character limits

### Old Class Names
For developers, old class names still work:
```python
from functions.tts_handler import ElevenLabsTTSProcessor  # Still works
from functions.tts_handler import TTSHandler              # Still works
from functions.tts_handler import TTSProcessor            # Still works
```

## API Usage Examples

### Basic TTS Call
```python
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64

client = Speechify(token="YOUR_TOKEN")
audio_response = client.tts.audio.speech(
    audio_format="mp3",
    input="Hello, world!",
    language="en",
    model="simba-english",
    options=GetSpeechOptionsRequest(
        loudness_normalization=True,
        text_normalization=True
    ),
    voice_id="scott"
)

audio_bytes = base64.b64decode(audio_response.audio_data)
```

### Voice Filtering
```python
def filter_voice_models(voices, *, gender=None, locale=None, tags=None):
    """Filter Speechify voices by criteria"""
    results = []
    for voice in voices:
        if gender and voice.gender.lower() != gender.lower():
            continue
        if locale and not any(
            any(lang.locale == locale for lang in model.languages)
            for model in voice.models
        ):
            continue
        if tags and not all(tag in voice.tags for tag in tags):
            continue
        for model in voice.models:
            results.append(model.name)
    return results
```

## Migration Checklist

- [ ] Install speechify-api: `pip install speechify-api`
- [ ] Get Speechify API key from https://console.sws.speechify.com/signup
- [ ] Update config.json with Speechify settings
- [ ] Test TTS functionality in Anki
- [ ] Verify audio quality and language support
- [ ] Check logs for any errors
- [ ] Update any custom scripts to use new API

## Support

If you encounter issues during migration:

1. Check the troubleshooting section above
2. Enable debug mode and check logs
3. Run the test suite to verify installation
4. Contact support with error messages and logs

## Changelog

### v0.6.0 - Speechify Migration
- ✅ Migrated from ElevenLabs to Speechify TTS
- ✅ Added multilingual language support
- ✅ Enhanced audio quality options
- ✅ Maintained backward compatibility
- ✅ Added comprehensive testing suite
- ✅ Updated configuration system
- ✅ Improved error handling

---

**Note**: This migration maintains all existing functionality while providing access to Speechify's advanced TTS capabilities. The transition should be seamless for most users. 