## Installation and Setup Guide

Complete guide for installing and running aRe_Agent.

## Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **OpenAI API key** (required)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd Multi-Agent-AI-Research-Workspace
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Model configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy

# Optional: Application settings
SECRET_KEY=your-secret-key-here
MAX_FILE_SIZE_MB=50
MAX_RESEARCH_SOURCES=30
```

**Important**: Replace `sk-your-actual-api-key-here` with your real OpenAI API key.

### 5. Create Required Directories

```bash
mkdir -p logs data/chromadb data/audio
```

### 6. Verify Installation

Run the test suite to verify everything is working:
```bash
pytest tests/ -v
```

## Running the Application

### Start the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### First Time Setup

1. **Create an Account**
   - Click on the "Sign Up" tab
   - Enter username, password, and optional email
   - Password must contain uppercase, lowercase, and digit
   - Click "Sign Up"

2. **Log In**
   - Switch to "Login" tab
   - Enter your credentials
   - Click "Login"

3. **Select an Agent**
   - Choose from the four available agents
   - Each agent has specialized capabilities

4. **Start Using**
   - Upload PDFs (PDF Research Agent)
   - Ask questions
   - Get AI-powered responses
   - Export results as Markdown or Audio

## Configuration Options

### OpenAI Models

**Chat Model** (OPENAI_MODEL):
- `gpt-4-turbo-preview` (recommended, best quality)
- `gpt-4` (high quality, slower)
- `gpt-3.5-turbo` (faster, lower cost)

**Embedding Model** (OPENAI_EMBEDDING_MODEL):
- `text-embedding-3-small` (recommended)
- `text-embedding-3-large` (higher quality, higher cost)
- `text-embedding-ada-002` (legacy)

**TTS Model** (OPENAI_TTS_MODEL):
- `tts-1` (faster, recommended)
- `tts-1-hd` (higher quality)

**TTS Voice** (OPENAI_TTS_VOICE):
- `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

### Application Settings

**MAX_FILE_SIZE_MB**: Maximum PDF file size in megabytes (default: 50)

**MAX_RESEARCH_SOURCES**: Maximum number of web sources for research (default: 30)

**LOG_LEVEL**: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

## Troubleshooting

### Issue: "OPENAI_API_KEY is not set"

**Solution**: Ensure your `.env` file contains a valid OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: "ChromaDB errors"

**Solution**: Delete the ChromaDB directory and restart:
```bash
rm -rf data/chromadb
mkdir -p data/chromadb
```

### Issue: "Module not found" errors

**Solution**: Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: PDF upload fails

**Solutions**:
- Ensure PDF is not password-protected
- Check file size is under limit
- Verify PDF is not corrupted
- Make sure PDF contains extractable text (not just images)

### Issue: Research agent returns no sources

**Solutions**:
- Check internet connection
- Some queries may have limited results
- Try rephrasing your question
- Agent will note actual number of sources found

### Issue: Audio generation fails

**Solutions**:
- Check OpenAI API key has TTS access
- Ensure `data/audio` directory exists
- Check response text is not too long (max ~4000 characters)

## Development Setup

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_authentication.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Code Style

```bash
# Format code (if using black)
black .

# Check code style (if using flake8)
flake8 .
```

### Debugging

Enable debug logging in `.env`:
```bash
LOG_LEVEL=DEBUG
```

Check logs:
```bash
tail -f logs/app.log
```

## Production Deployment

### Security Checklist

- [ ] Use strong SECRET_KEY
- [ ] Deploy with HTTPS
- [ ] Use environment-specific API keys
- [ ] Enable firewall rules
- [ ] Implement rate limiting
- [ ] Regular security audits
- [ ] Keep dependencies updated

### Recommended Deployment Platforms

**Streamlit Cloud** (Easiest):
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy

**Docker** (Recommended):
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

**Cloud Platforms**:
- AWS (EC2, ECS, or App Runner)
- Google Cloud (Cloud Run)
- Azure (App Service)
- Heroku
- DigitalOcean

### Environment Variables for Production

Use platform-specific secret management:
- AWS: AWS Secrets Manager
- Google Cloud: Secret Manager
- Azure: Key Vault
- Heroku: Config Vars

## Updating the Application

### Pull Latest Changes

```bash
git pull origin main
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Migrate Data (if needed)

Check CHANGELOG.md for migration instructions.

### Restart Application

```bash
# Stop current instance (Ctrl+C)
streamlit run app.py
```

## Uninstallation

### Remove Virtual Environment

```bash
deactivate
rm -rf venv
```

### Remove Data

```bash
rm -rf data logs
```

### Remove Application Files

```bash
# Navigate to parent directory
cd ..
rm -rf Multi-Agent-AI-Research-Workspace
```

## Getting Help

### Documentation
- README.md - Project overview
- SECURITY.md - Security features
- This file - Installation guide

### Common Issues
- Check the Troubleshooting section above
- Review logs in `logs/app.log`
- Ensure all dependencies are installed

### Support
- Open an issue on GitHub
- Check existing issues for solutions
- Provide detailed error messages and logs

## Performance Tips

1. **Use GPT-3.5-turbo for faster responses** (change OPENAI_MODEL)
2. **Limit MAX_RESEARCH_SOURCES** for faster research
3. **Clear old audio files** regularly from `data/audio/`
4. **Clean up ChromaDB** periodically if database grows large
5. **Use SSDs** for better ChromaDB performance

## Next Steps

After installation:
1. Explore each agent's capabilities
2. Upload sample PDFs to test PDF Research Agent
3. Try different horoscope periods
4. Use General Chat for coding assistance
5. Ask historical questions to test History Agent
6. Export responses as Markdown or Audio
7. Customize configuration for your needs

---

**Need help?** Check README.md or open an issue on GitHub.
