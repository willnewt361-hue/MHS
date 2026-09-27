# Audio Study Aids (Binaural Beats) Integration Guide
---
## Quick Reference
**Endpoint**: `/api/premium/audio/generate`
**Method**: POST
**Auth**: Bearer token required
---

## What Are Binaural Beats?
Binaural beats are two slightly different frequencies played in each ear, creating a perceived "third frequency" in the brain. This can help with:
- **Focus/Concentration**: 40 Hz (Beta waves)
- **Relaxation**: 10 Hz (Alpha waves)
- **Sleep/Meditation**: 4 Hz (Theta waves)
- **Alertness**: 20-30 Hz (Beta-high)
---

## Generate Binaural Beats
### Basic Request
```bash
curl -X POST https://mengo-hub.local/api/premium/audio/generate \
  -H "Authorization: Bearer MengoStudentToken" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "beat_frequency": 10,
    "duration_minutes": 30,
    "base_frequency": 200
  }'
```

### Response
```json
{
  "success": true,
  "message": "Audio generated successfully",
  "audio_url": "/audio/beats/binaural_10hz_30min.wav",
  "duration": "30:00",
  "beat_frequency": 10,
  "file_size": "5.2 MB"
}
```
---
## Frequency Guide
|Frequency|           Use Case        | Brain State | Duration |
|---------|---------------------------|-------------|----------|
| 4 Hz    |  Deep sleep,  meditation  | Theta       |  60 min  |
| 7-8 Hz  |  Relaxation,  creativity  | Alpha-Theta |  45 min  |
| 10 Hz   | Relaxation, focus         | Alpha       | 30-45min |
| 20-30Hz |  Alertness, concentration | Beta        | 20-30min |
| 40 Hz   | Deep focus,problem solving| Gamma       | 15-20min |
---
## Frontend Integration
### HTML Audio Player
```html
<div class="audio-study-section">
  <h2>🎵 Audio Study Aids</h2>
  
  <div class="preset-buttons">
    <button onclick="generateBeat(10, 30)">Relax (30 min)</button>
    <button onclick="generateBeat(20, 25)">Focus (25 min)</button>
    <button onclick="generateBeat(40, 20)">Deep Focus (20 min)</button>
    <button onclick="generateBeat(4, 60)">Sleep (60 min)</button>
  </div>

  <div class="custom-generator">
    <label>Frequency (Hz):</label>
    <input type="number" id="frequency" min="1" max="100" value="10">
    
    <label>Duration (min):</label>
    <input type="number" id="duration" min="5" max="120" value="30">
    
    <button onclick="customBeat()">Generate Custom Beat</button>
  </div>

  <div id="player-container" style="display:none;">
    <audio id="audio-player" controls style="width: 100%; margin-top: 10px;">
      Your browser does not support the audio element.
    </audio>
    <button onclick="downloadAudio()">Download Audio</button>
  </div>

  <div id="loading-spinner" style="display:none;">
    <p>⏳ Generating binaural beats...</p>
  </div>
</div>

<style>
.audio-study-section {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  margin: 20px 0;
}

.preset-buttons {
  display: flex;
  gap: 10px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.preset-buttons button {
  padding: 10px 15px;
  background: rgba(255,255,255,0.2);
  border: 2px solid white;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
}

.preset-buttons button:hover {
  background: rgba(255,255,255,0.4);
}

.custom-generator {
  display: flex;
  gap: 10px;
  margin: 15px 0;
  flex-wrap: wrap;
  align-items: center;
}

.custom-generator label {
  font-weight: 500;
}

.custom-generator input {
  padding: 8px;
  border: none;
  border-radius: 4px;
  width: 80px;
}

.custom-generator button {
  padding: 8px 15px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
}

#loading-spinner {
  text-align: center;
  padding: 20px;
}
</style>

<script>
const studentToken = localStorage.getItem('mengo_token');

async function generateBeat(frequency, duration) {
  document.getElementById('loading-spinner').style.display = 'block';
  
  try {
    const response = await fetch('/api/premium/audio/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${studentToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_id: localStorage.getItem('student_id'),
        beat_frequency: frequency,
        duration_minutes: duration,
        base_frequency: 200
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      const player = document.getElementById('audio-player');
      player.src = data.audio_url;
      document.getElementById('player-container').style.display = 'block';
      document.getElementById('loading-spinner').style.display = 'none';
      
      showNotification(`✅ ${frequency}Hz beat generated for ${duration} minutes`);
    } else {
      showNotification('❌ Failed to generate audio');
    }
  } catch (e) {
    console.error(e);
    showNotification('Error generating audio');
  } finally {
    document.getElementById('loading-spinner').style.display = 'none';
  }
}

function customBeat() {
  const freq = parseInt(document.getElementById('frequency').value);
  const dur = parseInt(document.getElementById('duration').value);
  
  if (freq < 1 || freq > 100) {
    showNotification('Frequency must be between 1-100 Hz');
    return;
  }
  if (dur < 5 || dur > 120) {
    showNotification('Duration must be between 5-120 minutes');
    return;
  }
  
  generateBeat(freq, dur);
}

function downloadAudio() {
  const audioSrc = document.getElementById('audio-player').src;
  const link = document.createElement('a');
  link.href = audioSrc;
  link.download = 'binaural-beats.wav';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function showNotification(msg) {
  // Implement your notification system
  alert(msg);
}
</script>
```

---
## API Endpoints
### Generate Audio
**POST** `/api/premium/audio/generate`
```json
{
  "student_id": "S001",
  "beat_frequency": 10,
  "duration_minutes": 30,
  "base_frequency": 200
}
```

Response includes:
- `audio_url`: Path to generated WAV file
- `duration`: Human-readable duration
- `beat_frequency`: Generated frequency
- `file_size`: File size in MB

### Get Available Presets
**GET** `/api/premium/audio/presets`
```json
{
  "presets": [
    {
      "name": "Focus",
      "frequency": 20,
      "duration": 25,
      "description": "For concentration and alertness"
    },
    {
      "name": "Relax",
      "frequency": 10,
      "duration": 30,
      "description": "For calm and relaxation"
    }
  ]
}
```
### List Generated Audios
**GET** `/api/premium/audio/list/:student_id`
```json
{
  "audios": [
    {
      "id": 1,
      "frequency": 10,
      "duration": 30,
      "created_at": "2024-01-15",
      "url": "/audio/beats/..."
    }
  ]
}
```
---
## Technical Implementation
### Audio Generation (NumPy/Wave)
```python
import numpy as np
import wave

def generate_binaural_beats(
    frequency_left: int,
    frequency_right: int,
    duration: int,
    sample_rate: int = 44100
) -> bytes:
    """
    Generate binaural beats as stereo WAV audio
    
    frequency_left: Left ear frequency (Hz)
    frequency_right: Right ear frequency (Hz)
    duration: Duration in seconds
    sample_rate: Sample rate (Hz)
    """
    
    # Generate time array
    t = np.linspace(0, duration, sample_rate * duration, False)
    
    # Generate sine waves for each ear
    left_channel = np.sin(2 * np.pi * frequency_left * t) * 0.3
    right_channel = np.sin(2 * np.pi * frequency_right * t) * 0.3
    
    # Combine into stereo (interleaved)
    stereo = np.zeros((len(t), 2))
    stereo[:, 0] = left_channel
    stereo[:, 1] = right_channel
    
    # Convert to 16-bit PCM
    stereo_int16 = np.int16(stereo * 32767)
    
    return stereo_int16.tobytes()
```
---
## Student Study Plan Integration
```json
{
  "study_session": {
    "subject": "Mathematics",
    "duration": 120,
    "audio_aid": {
      "type": "binaural_beats",
      "frequency": 40,
      "duration_minutes": 30,
      "recommendations": "Deep focus for solving complex problems"
    }
  }
}
```

---
## Safety Guidelines
⚠️ **Important Notes**:
- Binaural beats are safe for most people
- Recommended maximum duration: 2 hours per session
- Not recommended for people with epilepsy
- Use comfortable volume (never above 85dB)
- Don't use while driving or operating machinery
- Frequency recommendations:
  - 1-4 Hz: For sleep/deep relaxation (use in evening)
  - 4-7 Hz: For light meditation
  - 7-12 Hz: For relaxation and focus
  - 12-30 Hz: For alertness and concentration
  - 30+ Hz: For intense focus (limit to 20-30 min)

---
## Student Features
✅ **Included**:
- Generate custom beats
- Download audios for offline use
- Save favorite presets
- Track listening history
- Compare performance before/after sessions

📊 **Analytics**:
- Track which frequencies work best for student
- Correlate listening sessions with quiz scores
- Provide recommendations

---
## Admin Controls
**Manage Audio Presets** (Admin endpoint):
```bash
curl -X POST https://mengo-hub.local/api/admin/audio-presets \
  -H "Authorization: Bearer AdminToken" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_preset",
    "preset": {
      "name": "Evening Study",
      "frequency": 8,
      "duration": 45,
      "description": "Relaxed focus for evening sessions"
    }
  }'
```
---
## Performance Tracking
Link audio use to student performance:
```json
{
  "student_id": "S001",
  "weekly_stats": {
    "audio_sessions": 12,
    "total_listening_minutes": 360,
    "avg_frequency_used": 15,
    "quiz_performance_improvement": "+8%",
    "most_effective_frequency": 20
  }
}
```
---
## Troubleshooting
**Audio won't play?**
- Check browser supports HTML5 audio
- Verify file path is correct
- Check file size (should be < 100MB)

**Generation fails?**
- Check duration isn't too long (max 120 min)
- Verify frequency is 1-100 Hz
- Check server disk space

**Quality issues?**
- Increase sample rate in generation
- Use higher base frequency
- Check audio volume level

---
## Future Enhancements
- [ ] Add music overlays (nature sounds, rain, etc.)
- [ ] Implement AI-recommended frequencies based on performance
- [ ] Create playlists of multiple beats
- [ ] Add visualization (waveforms)
- [ ] Mobile app audio playback
- [ ] Offline sync capability

