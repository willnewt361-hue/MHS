# 🤖 LOCAL AI & FREE AI SETUP GUIDE FOR MENGO-HUB
**Complete guide to use FREE AI with your system - Local + Cloud options**

---
## 🎯 THREE AI OPTIONS
### Option 1: Local AI (GPTAll) - EASIEST ⭐
- ✅ Free (offline, no API keys needed)
- ✅ Privacy (runs on your computer)
- ✅ Fast (CPU/GPU accelerated)
- Status: **READY TO USE** (in requirements.txt)

### Option 2: Local AI (Ollama) - BEST
- ✅ Free (offline)
- ✅ More models available
- ✅ Better performance
- Status: **SETUP REQUIRED** (5 minutes)

### Option 3: Free Cloud AI - POWERFUL
- ✅ Free API tier (limited requests)
- ✅ No setup needed
- ✅ Better quality responses
- Status: **SELECT ONE BELOW**

---
## 🚀 QUICK START: USE LOCAL AI NOW
### Step 1: Install (Already in requirements.txt)
```bash
pip install gpt4all
```

### Step 2: Download a model (First time only)
```python
python -c "from gpt4all import GPT4All; model = GPT4All('mistral-7b-instruct-v0.1.Q4_0.gguf'); print('✅ Model downloaded!')"
```

Takes 2-5 minutes (downloads ~4 GB model)
### Step 3: Update .env
```env
AI_PROVIDER=gpt4all
# That's it! Uses local model by default
```

### Step 4: Start system
```bash
python flask_app.py
```

### Step 5: Use AI
```bash
curl -X POST https://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer MengoStudentToken123" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "query": "Explain photosynthesis"
  }'
```

**Result**: ✅ AI response from local model!
---
## 🎵 DETAILED SETUP: OLLAMA (Recommended Local)
### What is Ollama?
- Free tool to run LLMs locally
- Better than GPTAll
- Faster responses
- More models available

### Installation
#### Windows
1. Download: https://ollama.ai/download (Windows)
2. Install
3. Run it
4. Done!

#### Mac
```bash
brew install ollama
ollama serve
```

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
ollama serve
```

### Step 1: Download a Model
```bash
ollama pull mistral
# or
ollama pull neural-chat
# or
ollama pull orca-mini
```

First download takes 5-10 minutes

### Step 2: Test it works
```bash
ollama run mistral "Explain photosynthesis"
```
You should see AI response!

### Step 3: Update .env for Mengo-Hub
```env
AI_PROVIDER=local
LOCAL_AI_URL=http://localhost:11434/api/generate
# Ollama runs on port 11434 by default
```

### Step 4: Restart system
```bash
python flask_app.py
```

### Step 5: Use in Mengo-Hub
```bash
curl -X POST https://localhost:5000/api/ai/chat \
  -d '{"student_id":"S001","query":"What is AI?"}'
```
**Result**: ✅ Ollama model responds!

---
## 📊 RECOMMENDED LOCAL MODELS
|       Model     | Size |     Speed    |  Quality  |         Commands        |
|-----------------|------|--------------|-----------|-------------------------|
| **mistral**     | 4 GB | ⚡⚡⚡ Fast |    Good   |  `ollama pull mistral`  |
| **neural-chat** | 5 GB | ⚡⚡ Medium | Very Good | `ollama pull neural-chat`|
| **orca-mini**   | 2 GB | ⚡⚡⚡ Fast |    Good   | `ollama pull orca-mini` |
| **llama2**      | 4 GB | ⚡⚡ Medium | Very Good |   `ollama pull llama2`   |
| **openhermes**  | 4 GB | ⚡⚡ Medium | Excellent | `ollama pull openhermes` |
**Recommended for Mengo-Hub**: `mistral` (best balance)

---
## 🆓 FREE CLOUD AI SERVICES (No Installation)
### Option 1: Hugging Face (BEST FREE) ⭐
- Free API access
- No credit card needed
- Limited rate limit
- High quality

**Setup**:
```bash
# 1. Register: https://huggingface.co/
# 2. Get API key: https://huggingface.co/settings/tokens
# 3. Create new token (read-only ok)
# 4. Add to .env:

HF_API_KEY=hf_xxxxxxxxxxxxx
AI_PROVIDER=huggingface
```

**In Mengo-Hub .env**:
```env
AI_PROVIDER=huggingface
HF_API_KEY=hf_your_api_key_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
```

**Usage**:
```bash
pip install requests
# System will auto-use Hugging Face
```

---
### Option 2: OpenAI (ChatGPT) - LIMITED FREE
- **Free tier**: $5 credit (good for testing)
- No credit card if using credit
- Best quality responses
- Most expensive long-term

**Setup**:
1. Go to: https://platform.openai.com/account/api-keys
2. Register (no credit card for free trial)
3. Get API key
4. Add to .env:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
```

**Then use**:
```bash
pip install openai
python flask_app.py
# Mengo-Hub auto-uses OpenAI
```
**Free**: $5 credit = ~100 requests

---
### Option 3: Anthropic Claude - BEST FREE TIER
- **Free tier**: Great for testing
- NO credit card needed (sometimes)
- High quality like ChatGPT
- Generous free credits

**Setup**:
1. Go to: https://console.anthropic.com/
2. Register
3. Get API key
4. Add to .env:

```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

**Usage**:
```bash
pip install anthropic
python flask_app.py
```

---
### Option 4: Google Gemini - FREE
- **Free tier**: Generous limits
- No credit card sometimes needed
- Good quality
- Fast responses

**Setup**:
1. Go to: https://makersuite.google.com/app/apikey
2. Create API key
3. Add to .env:

```env
AI_PROVIDER=google
GOOGLE_API_KEY=your_key_here
```

**Usage**:
```bash
pip install google-generativeai
python flask_app.py
```

---
### Option 5: Replicate (MOST FREE MODELS)
- Cheapest for heavy use
- Free tier with $5 credit
- Huge model selection
- Pay-as-you-go

**Setup**:
1. Register: https://replicate.com
2. Get API key
3. Add to .env:

```env
REPLICATE_API_KEY=your_key_here
```
**Usage**: ~$0.001-0.01 per request

---
## 📊 COMPARISON TABLE
|      Service     | Free Tier |   Best For  |Setup Time|  Quality  |
|------------------|-----------|-------------|----------|-----------|
| **Ollama Local** | ✅  Full |  Production  |  15 min | Very Good |
| **GPTAll Local** | ✅  Full |  Quick test  |  5 min  |    Good   |
| **Hugging Face** | ✅ Limit |   Testing    |  5 min  |    Good   |
| **OpenAI**       | ⚠️ $5    | Best quality |  5 min  | Excellent |
| **Anthropic**    | ✅ Limited| Good quality|  5 min  | Excellent |
| **Google Gemini**| ✅ Limit |     Fast     |  5 min  |    Good   |
| **Replicate**    | ⚠️ $5    |  Any model   |  5 min  |   Varies  |

---
## 🎯 RECOMMENDED FOR MENGO-HUB
### FOR DEVELOPMENT (FREE)
```env
AI_PROVIDER=gpt4all
# Uses local GPTAll - instant setup, no keys needed
```

### FOR PRODUCTION (FREE + CLOUD)
```env
AI_PROVIDER=huggingface
HF_API_KEY=hf_xxxxx
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
# Free API from Hugging Face
```

### FOR BEST QUALITY (PAID, BUT $5 FREE)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
# Use free $5 credit for testing
```

---
## 🔄 HOW TO SWITCH PROVIDERS
### In .env file:
```env
# Option 1: Local (No setup needed)
AI_PROVIDER=gpt4all

# Option 2: Ollama (Need to run ollama serve)
AI_PROVIDER=local
LOCAL_AI_URL=http://localhost:11434/api/generate

# Option 3: OpenAI (Need API key)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx

# Option 4: Anthropic (Need API key)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Option 5: Google Gemini (Need API key)
AI_PROVIDER=google
GOOGLE_API_KEY=xxxxx

# Option 6: Hugging Face (Need API key)
AI_PROVIDER=huggingface
HF_API_KEY=hf_xxxxx
```

### Then restart:
```bash
python flask_app.py
```

**That's it!** System auto-uses new provider.
---
## 📝 STEP-BY-STEP SETUP GUIDES
### Setup #1: Local GPTAll (5 Minutes)

```bash
# 1. Already in requirements.txt
pip install gpt4all

# 2. Download model (first time only)
python << 'EOF'
from gpt4all import GPT4All
model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
model.generate("Hello!")
print("✅ Model ready!")
EOF

# 3. Update .env
echo "AI_PROVIDER=gpt4all" >> .env

# 4. Start
python flask_app.py

# 5. Test
curl -X POST https://localhost:5000/api/ai/chat \
  -d '{"student_id":"S001","query":"Hello"}'
```

---
### Setup #2: Ollama Local (15 Minutes)
```bash
# 1. Install Ollama from https://ollama.ai
# (Just download and install)

# 2. Download model
ollama pull mistral

# 3. Run ollama server
ollama serve
# Keep this running in background

# 4. Update .env
cat > .env << 'EOF'
AI_PROVIDER=local
LOCAL_AI_URL=http://localhost:11434/api/generate
EOF

# 5. Start Mengo-Hub (in new terminal)
python flask_app.py

# 6. Test
curl -X POST https://localhost:5000/api/ai/chat \
  -d '{"student_id":"S001","query":"Test"}'
```

---
### Setup #3: Hugging Face FREE (5 Minutes)
```bash
# 1. Register: https://huggingface.co/
# 2. Get API key: https://huggingface.co/settings/tokens

# 3. Update .env
cat > .env << 'EOF'
AI_PROVIDER=huggingface
HF_API_KEY=hf_your_key_here
EOF

# 4. Start
python flask_app.py

# 5. Test
curl -X POST https://localhost:5000/api/ai/chat \
  -d '{"student_id":"S001","query":"Explain AI"}'
```

---
### Setup #4: OpenAI (5 Minutes, Need $5)
```bash
# 1. Register: https://platform.openai.com/account/api-keys
# 2. Get API key
# 3. Add $5 credit (or use free trial)

# 4. Update .env
cat > .env << 'EOF'
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
EOF

# 5. Install
pip install openai>=1.3.9

# 6. Start
python flask_app.py

# 7. Test
curl -X POST https://localhost:5000/api/ai/chat \
  -d '{"student_id":"S001","query":"What is machine learning?"}'
```

---
## 💡 WHICH ONE SHOULD I USE?
### For Testing (Right Now)
→ **GPTAll** (no setup, instant)
```env
AI_PROVIDER=gpt4all
```

### For Production (Best Price/Quality)
→ **Ollama** (free, runs locally, good quality)
```
1. Install Ollama
2. ollama pull mistral
3. Set AI_PROVIDER=local
```

### For Best Quality (Can Pay)
→ **OpenAI** (use $5 free credit to test)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
```

### For Free Cloud (No Setup)
→ **Hugging Face** (free API, no credit card)
```env
AI_PROVIDER=huggingface
HF_API_KEY=hf_xxxxx
```

---
## 🔧 ADVANCED: USE MULTIPLE AIS
In `ai_service.py`, you can set fallback:

```python
# Primary: Local
# Fallback: Hugging Face
# Fallback: OpenAI

AI_PROVIDER=gpt4all  # Try local first
HF_API_KEY=hf_xxxxx  # Fallback
OPENAI_API_KEY=sk-xxxxx  # Ultimate fallback
```

System tries each in order!

---
## ⚠️ TROUBLESHOOTING
### "ModuleNotFoundError: gpt4all"
```bash
pip install gpt4all
```

### "Cannot connect to Ollama"
```bash
# Make sure ollama is running
ollama serve  # Run this in another terminal
```

### "Invalid API key"
- Check key is copied correctly
- Check provider name matches key (openai, anthropic, etc.)
- Verify key is still active

### "Rate limit exceeded"
- Using free tier? Try local AI instead
- Or wait (depends on provider)
- Consider paid plan

### "Slow responses"
- Local AI slower than cloud
- Use Ollama instead of GPTAll
- Or use OpenAI (fastest)

---
## 📊 COST COMPARISON (Per 1000 Requests)
|     Provider     | Cost | Per Request |
|------------------|------|------------|
| **Ollama**       | Free |    $0.000  |
| **GPTAll**       | Free |    $0.000  |
| *Hugging Face*   | Free |    $0.000  |
| *Google Gemini*  |Freetier|$0.000(ltd)|
| *OpenAI GPT-3.5* | ~$2  |    $0.002  |
| **OpenAI GPT-4** | ~$30 |    $0.030  |
| *Anthropic*      | ~$5  |    $0.005  |

**BEST VALUE**: Ollama (free, unlimited)
---
## 🚀 QUICK COMMAND: TEST ALL PROVIDERS

```bash
# GPTAll (Local)
echo "Testing GPTAll..."
python << 'EOF'
from gpt4all import GPT4All
model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
response = model.generate("What is 2+2?")
print(f"✅ GPTAll: {response}")
EOF

# Ollama (Local)
echo "Testing Ollama..."
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "What is 2+2?",
  "stream": false
}'

# OpenAI
echo "Testing OpenAI..."
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer sk-YOUR_KEY" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"What is 2+2?"}]}'
```

---
## 🎯 RECOMMENDED SETUP FOR MENGO-HUB
### Development
```env
AI_PROVIDER=gpt4all
# Free, instant setup, no internet needed
```

### Production
```env
AI_PROVIDER=local
LOCAL_AI_URL=http://localhost:11434/api/generate
# Run ollama serve in background
```

### Production (Cloud)
```env
AI_PROVIDER=huggingface
HF_API_KEY=hf_your_key
# Free, no setup needed, cloud-based
```

---
## 📞 SUPPORT
**Can't get AI working?**
- Check .env file has correct AI_PROVIDER
- Check API key (if using cloud)
- Check port if using local (Ollama on 11434)
- See logs: `logs/mengo_hub.log`

**Want different AI?**
- Just change `AI_PROVIDER` in .env
- Restart: `python flask_app.py`
- Done!

**Need more models?**
- Ollama: `ollama pull model_name`
- Hugging Face: https://huggingface.co/models
- OpenAI: https://platform.openai.com/models

---
## ✅ YOU'RE READY!
Choose your AI:
1. **Now**: Use GPTAll (no setup)
2. **Next**: Install Ollama (5 min)
3. **Later**: Add OpenAI (5 min)

**Start Mengo-Hub with AI!**
```bash
# Set your provider in .env
# Then run:
python flask_app.py

# Visit:
https://localhost:5000

# AI will respond to student queries! 🤖
```

---

**Version**: Complete with AI Guide
**Status**: ✅ Ready to use any AI provider
**Cost**: From FREE (Ollama) to pay-as-you-go

