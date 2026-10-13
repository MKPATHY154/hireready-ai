# HireReady AI - Project Documentation

## Overview

**HireReady AI** is an intelligent resume matching and mock interview platform built with Streamlit. It helps candidates prepare for technical interviews by:

1. **Uploading a resume** (PDF) - extracts text and detects technical skills
2. **Entering a job description** - provides context for interview questions
3. **Generating AI-powered interview questions** - tailored to the candidate's resume and the job requirements

---

## Current Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **PDF Processing**: PyMuPDF (fitz)
- **Environment Management**: python-dotenv
- **AI Provider**: OpenRouter (OpenAI-compatible API)
- **Current Model**: `nvidia/nemotron-3-ultra-550b-a55b` (free tier via OpenRouter)

### Project Structure
```
hireready-ai/
├── app.py                 # Main Streamlit application
├── .env                   # Environment variables (API keys, model config)
├── venv/                  # Python virtual environment
├── PROJECT_DOCUMENTATION.md  # This file
└── requirements.txt       # (Optional) Python dependencies
```

---

## Configuration

### Environment Variables (`.env`)
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b
```

### Model Configuration
- **Provider**: OpenRouter (https://openrouter.ai)
- **Base URL**: `https://openrouter.ai/api/v1`
- **Current Model**: `nvidia/nemotron-3-ultra-550b-a55b`
- **Model Type**: Free tier (no cost per token)
- **Headers Required**:
  - `HTTP-Referer`: Identifies your app
  - `X-OpenRouter-Title`: App name for rankings

---

## Evolution History

### Version 1.0 - Original (Gemini)
- **Provider**: Google Gemini
- **Model**: `gemini-2.5-flash`
- **Client**: `google.genai`
- **Status**: ❌ **DEPRECATED** - Model no longer available to new users

### Version 2.0 - DeepSeek Migration
- **Provider**: DeepSeek
- **Model**: `deepseek-chat` / `deepseek-flash`
- **Client**: OpenAI-compatible (`openai` package)
- **Base URL**: `https://api.deepseek.com`
- **Status**: ⚠️ **BLOCKED** - Insufficient balance on account

### Version 3.0 - OpenRouter (First Attempt)
- **Provider**: OpenRouter
- **Model**: `openai/gpt-oss-20b:free`
- **Status**: ❌ **FAILED** - Model unavailable for free tier

### Version 4.0 - Current (OpenRouter + NVIDIA Nemotron)
- **Provider**: OpenRouter
- **Model**: `nvidia/nemotron-3-ultra-550b-a55b`
- **Status**: ✅ **WORKING** - Verified with live API call

---

## Key Changes Summary

| Change | From | To | Reason |
|--------|------|-----|--------|
| AI Provider | Google Gemini | DeepSeek | Gemini model deprecated |
| AI Provider | DeepSeek | OpenRouter | DeepSeek account balance issue |
| Model | `gemini-2.5-flash` | `deepseek-chat` | Provider migration |
| Model | `deepseek-chat` | `openai/gpt-oss-20b:free` | Free tier via OpenRouter |
| Model | `openai/gpt-oss-20b:free` | `nvidia/nemotron-3-ultra-550b-a55b` | Free model unavailable, switched to working free model |
| Client Library | `google.genai` | `openai` | OpenAI-compatible API standard |
| Base URL | `generativelanguage.googleapis.com` | `https://api.deepseek.com` | DeepSeek endpoint |
| Base URL | `https://api.deepseek.com` | `https://openrouter.ai/api/v1` | OpenRouter endpoint |
| Auth Headers | None | `HTTP-Referer`, `X-OpenRouter-Title` | OpenRouter requirements |

---

## Code Changes in `app.py`

### Imports
```python
# Before (Gemini)
from google import genai

# After (OpenRouter via OpenAI client)
from openai import OpenAI
```

### Configuration
```python
# Before
api_key = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# After
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
```

### Client Initialization
```python
# Before (Gemini)
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model=MODEL_NAME,
    contents=prompt
)

# After (OpenRouter)
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://localhost",
        "X-OpenRouter-Title": "HireReady AI",
    },
)
response = client.chat.completions.create(
    model=OPENROUTER_MODEL,
    messages=[
        {"role": "system", "content": "You are an experienced technical interviewer."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
)
answer = response.choices[0].message.content
```

---

## How to Run

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)
- OpenRouter API key (free at https://openrouter.ai/settings/keys)

### Setup
```bash
# Clone/navigate to project
cd hireready-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install streamlit pymupdf python-dotenv openai

# Configure .env with your OpenRouter API key
# Edit .env and set OPENROUTER_API_KEY

# Run the app
python -m streamlit run app.py
```

### Access
Open browser to: `http://localhost:8501`

---

## Verified Working Configuration

### Live Test Result
```bash
# Test command
python -c "
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    default_headers={'HTTP-Referer':'https://localhost','X-OpenRouter-Title':'HireReady AI'}
)
response = client.chat.completions.create(
    model=os.getenv('OPENROUTER_MODEL','nvidia/nemotron-3-ultra-550b-a55b'),
    messages=[{'role':'user','content':'Reply with one word: hello'}],
    temperature=0.7
)
print(response.choices[0].message.content)
"

# Output: hello
```

### Syntax Validation
```bash
python -m py_compile app.py
# Exit code: 0 (success)
```

---

## Alternative Free Models on OpenRouter

If you want to experiment with other free models, change `OPENROUTER_MODEL` in `.env`:

| Model | Description |
|-------|-------------|
| `nvidia/nemotron-3-ultra-550b-a55b` | **Current** - NVIDIA Nemotron 3 Ultra (550B params) |
| `meta-llama/llama-3.1-8b-instruct:free` | Meta Llama 3.1 8B Instruct |
| `deepseek/deepseek-r1:free` | DeepSeek R1 reasoning model |
| `deepseek/deepseek-chat-v3-0324:free` | DeepSeek Chat V3 |
| `google/gemma-2-9b-it:free` | Google Gemma 2 9B Instruct |
| `microsoft/phi-3-mini-128k-instruct:free` | Microsoft Phi-3 Mini |

> **Note**: Free model availability changes. Check https://openrouter.ai/models for current list.

---

## Troubleshooting

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `404 - Model unavailable for free` | Model doesn't have free tier | Use a model with `:free` suffix or verified free model |
| `402 - Insufficient Balance` | Account has no credits | Add credits or use free models |
| `401 - Invalid API Key` | Wrong/missing API key | Check `.env` has correct `OPENROUTER_API_KEY` |
| `ModuleNotFoundError: openai` | Missing dependency | Run `pip install openai` |
| `ModuleNotFoundError: fitz` | Missing PyMuPDF | Run `pip install pymupdf` |

### Debug Steps
1. Verify `.env` has correct API key
2. Test API key directly with curl:
   ```bash
   curl -X POST https://openrouter.ai/api/v1/chat/completions \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b","messages":[{"role":"user","content":"test"}]}'
   ```
3. Check OpenRouter dashboard for usage/limits

---

## Future Enhancements

- [ ] Add model selector dropdown in UI
- [ ] Add streaming response support
- [ ] Add cost tracking per generation
- [ ] Support multiple resume uploads
- [ ] Add interview question categories (behavioral, technical, system design)
- [ ] Export questions to PDF/Markdown
- [ ] Add mock interview session with timer

---

## References

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **OpenRouter Models**: https://openrouter.ai/models
- **OpenRouter API Reference**: https://openrouter.ai/docs/api-reference/overview
- **NVIDIA Nemotron 3 Ultra Model Page**: https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b
- **Streamlit Documentation**: https://docs.streamlit.io
- **PyMuPDF Documentation**: https://pymupdf.readthedocs.io

---

*Last Updated: 2026-10-12*
*Current Status: ✅ Working with OpenRouter + NVIDIA Nemotron 3 Ultra (free)*