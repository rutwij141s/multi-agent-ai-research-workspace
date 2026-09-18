# aRe_Agent

A professional, modular, multi-agent AI research workspace that provides specialized AI agents for different tasks.

## Features

- **PDF Research Agent**: Upload and interact with PDF documents using RAG architecture
- **Horoscope Research Agent**: Personalized astrology insights with real-time web research
- **General Chat Agent**: General-purpose AI assistant for various tasks
- **History & Geopolitics Agent**: Specialized research agent for historical and geopolitical queries

### Core Capabilities

- Multi-agent architecture with specialized workflows
- RAG (Retrieval-Augmented Generation) for document interaction
- Real-time web research with source citations
- Streaming AI responses
- Conversation history management
- Export to Markdown and Audio (TTS)
- User authentication and session management
- ChromaDB for vector storage and retrieval

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Multi-Agent-AI-Research-Workspace
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key and other configuration:
```
OPENAI_API_KEY=your_actual_api_key_here
```

5. Create necessary directories:
```bash
mkdir -p logs data/chromadb
```

## Usage

Run the application:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### First Time Setup

1. Create an account using the signup page
2. Log in with your credentials
3. Select an agent from the dashboard
4. Start interacting with your chosen agent

## Agent Overview

### PDF Research Agent

Upload one or multiple PDF documents and:
- Ask questions about document content
- Get cited responses with page references
- Summarize documents
- Compare multiple PDFs
- Extract key findings

### Horoscope Research Agent

Get personalized horoscope insights by providing:
- Date of birth
- Time of birth (optional)
- Birth location
- Choose daily, weekly, or monthly horoscope
- Based on 20-30 real-time web sources

### General Chat Agent

A versatile AI assistant for:
- Code generation and debugging
- Writing assistance
- Research and analysis
- Brainstorming
- Technical explanations

### History & Geopolitics Agent

Research-oriented agent for:
- Historical events and timelines
- Geopolitical analysis
- International relations
- Wars and conflicts
- Political and economic history

## Architecture

```
aRe_Agent/
├── agents/          # Agent implementations
├── services/        # Core services (OpenAI, TTS, Research)
├── database/        # ChromaDB integration
├── auth/            # Authentication system
├── components/      # UI components
├── utils/           # Utilities and configuration
├── static/          # CSS and fonts
├── data/            # ChromaDB storage
└── tests/           # Test suite
```

## Security

- Never commit `.env` files with actual credentials
- API keys are loaded exclusively from environment variables
- Passwords are hashed using bcrypt
- User documents are isolated per user
- Input validation on all file uploads
- Session-based authentication

## Export Features

Each AI response can be:
- **Copied** to clipboard
- **Downloaded** as Markdown file
- **Generated as audio** using OpenAI TTS
- **Regenerated** for alternative responses

## Configuration

Key configuration options in `.env`:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)
- `CHROMA_DB_PATH`: Path for ChromaDB storage
- `MAX_FILE_SIZE_MB`: Maximum upload file size
- `MAX_RESEARCH_SOURCES`: Number of sources for research agents

## Troubleshooting

### ChromaDB Issues
If you encounter ChromaDB errors, delete the `data/chromadb` directory and restart.

### OpenAI API Errors
- Verify your API key is correct in `.env`
- Check you have sufficient API credits
- Ensure you're using a supported model

### PDF Upload Issues
- Ensure PDF is not password-protected
- Check file size is under the limit
- Verify PDF is not corrupted

## Development

### Adding New Agents

1. Create agent directory in `agents/`
2. Implement agent class inheriting from `BaseAgent`
3. Register agent in `agent_router.py`
4. Add agent card in UI components

### Running Tests

```bash
pytest tests/
```

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the repository.
