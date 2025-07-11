# Notes to Blog Application

An automated application that transforms unorganized notes into well-structured blog posts using AI agents, research capabilities, and image generation.

## 🚀 Features

- **AI-Powered Content Generation**: Uses CrewAI agents to analyze, research, and write blog content
- **Multi-Format Input**: Supports Markdown and plain text note files
- **Automatic Research**: Integrates with Brave Browser API for content research and validation
- **Image Generation**: Creates relevant images using Replicate.com's text-to-image service
- **Structured Output**: Generates properly formatted blog posts with frontmatter and metadata
- **Batch Processing**: Process multiple notes at once with progress tracking
- **Modern CLI**: Clean command-line interface with rich output and progress bars

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

```
notes_to_blog/
├── src/
│   ├── models/          # Pydantic data models
│   ├── services/        # External service integrations
│   ├── agents/          # CrewAI agents for content processing
│   ├── crews/           # Workflow orchestration
│   └── logger.py        # Logging configuration
├── templates/           # Jinja2 templates for prompts and output
├── inbox/              # Input notes directory
├── output/             # Generated blog posts
├── images/             # Generated images
└── main.py             # CLI entry point
```

### Core Components

- **Input Processor**: Monitors inbox, validates and parses note files
- **Content Analyzer Agent**: Summarizes notes, generates titles and outlines
- **Research Agent**: Performs web research for content expansion
- **Content Writer Agent**: Writes introduction, conclusion, and subheading content
- **Image Generator Agent**: Creates relevant images for blog posts
- **Metadata Generator Agent**: Selects categories, tags, and generates frontmatter
- **Output Generator**: Creates final markdown files with proper formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- UV package manager
- API keys for external services

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd notes_to_blog
   ```

2. **Set up virtual environment**
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy example environment file
   cp example.env.txt .env
   
   # Edit .env with your API keys
   # Required: OPENROUTER_API_KEY, REPLICATE_API_TOKEN, BRAVE_API_KEY
   ```

4. **Create directories**
   ```bash
   mkdir -p inbox output images logs
   ```

5. **Test installation**
   ```bash
   uv run python main.py --help
   ```

## 📖 Usage

### CLI Commands

#### Process a Single Note
```bash
# Process a single markdown file
uv run python main.py process-file path/to/note.md

# Specify custom output directory
uv run python main.py process-file note.md --output ./custom-output
```

#### Batch Processing
```bash
# Process all notes in the inbox directory
uv run python main.py process-batch

# Use custom inbox and output directories
uv run python main.py process-batch --inbox ./my-notes --output ./my-blog
```

#### Configuration Management
```bash
# Show current configuration
uv run python main.py config --show

# Validate configuration
uv run python main.py config --validate

# Reload configuration
uv run python main.py config --reload
```

#### Status and Monitoring
```bash
# Show application status and recent logs
uv run python main.py status
```

### Input Format

Place your note files in the `inbox/` directory. Supported formats:

- **Markdown (.md)**: Full markdown support with headers, lists, code blocks
- **Plain Text (.txt)**: Simple text files

Example note structure:
```markdown
# My Blog Post Idea

## Key Points
- Point 1: Important information
- Point 2: More details
- Point 3: Additional context

## Ideas
Some ideas for the blog post:
- Idea 1
- Idea 2
- Idea 3

## Notes
Additional notes and thoughts.
```

### Output Format

Generated blog posts include:

- **Frontmatter**: Title, description, date, category, tags
- **Structured Content**: Introduction, subheadings, conclusion
- **Images**: Generated images with alt text and captions
- **Metadata**: SEO-friendly descriptions and tags

Example output:
```markdown
+++
title = "My Blog Post Title"
description = "A comprehensive guide to..."
date = 2025-01-27
draft = true

[taxonomies]
categories=["development"]
tags=["python", "tutorial", "programming"]
+++

# My Blog Post Title

Introduction content...

## First Subheading

Content with research and examples...

![Generated Image](images/image1.jpg)

## Second Subheading

More content...

## Conclusion

Summary and next steps...
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenRouter API (for LLM access)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://api.openrouter.ai/api/v1

# Replicate.com API (for image generation)
REPLICATE_API_TOKEN=your_replicate_token

# Brave Browser API (for web search)
BRAVE_API_KEY=your_brave_api_key
BRAVE_SEARCH_URL=https://api.search.brave.com/res/v1/web/search
```

### Application Configuration

The application uses Pydantic models for configuration. Key settings:

- **Paths**: Input/output directories, templates, logs
- **Content**: Categories, tags, subheading limits
- **Image**: Model, dimensions, quality settings
- **Logging**: Levels, formats, rotation
- **CrewAI**: Agent settings, memory, iterations

## 🧪 Testing

### Run All Tests
```bash
uv run pytest tests/ -v --cov=src --cov-report=html
```

### Test Categories
```bash
# Unit tests only
uv run pytest tests/ -m unit

# Integration tests
uv run pytest tests/ -m integration

# API tests (requires API keys)
uv run pytest tests/ -m api
```

### Test Coverage
```bash
# Generate coverage report
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html
```

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
uv sync

# Run with debug mode
uv run python main.py process-batch
```

### Production Deployment

1. **Set up environment**
   ```bash
   # Install production dependencies
   uv pip install -r requirements.txt
   
   # Configure production settings
   export APP_ENV=production
   export DEBUG=false
   ```

2. **Create deployment script**
   ```bash
   #!/bin/bash
   # deploy.sh
   uv run python main.py process-batch
   ```

3. **Set up monitoring**
   ```bash
   # Check application status
   uv run python main.py status
   
   # Monitor logs
   tail -f logs/app.log
   ```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p inbox output images logs

CMD ["python", "main.py", "process-batch"]
```

## 🔧 Development

### Project Structure
```
notes_to_blog/
├── src/
│   ├── models/              # Data models
│   │   ├── config_models.py # Configuration models
│   │   └── blog_models.py   # Blog post models
│   ├── services/            # External services
│   │   ├── openrouter_service.py
│   │   ├── replicate_service.py
│   │   ├── brave_search_service.py
│   │   └── service_registry.py
│   ├── agents/              # CrewAI agents
│   │   ├── base_agent.py
│   │   ├── content_analyzer.py
│   │   ├── researcher.py
│   │   ├── content_writer.py
│   │   ├── image_generator.py
│   │   └── metadata_generator.py
│   └── crews/               # Workflow orchestration
│       └── blog_post_crew.py
├── templates/               # Jinja2 templates
├── tests/                   # Test suite
├── docs/                    # Documentation
└── main.py                  # CLI entry point
```

### Adding New Features

1. **Create data models** in `src/models/`
2. **Implement services** in `src/services/`
3. **Add agents** in `src/agents/`
4. **Update crews** in `src/crews/`
5. **Write tests** in `tests/`
6. **Update CLI** in `main.py`

### Code Style

- **Naming**: Use snake_case for all identifiers
- **Type Hints**: All functions must have proper type hints
- **Documentation**: Every function needs a docstring (max 3 lines)
- **Error Handling**: Implement graceful error catching
- **Logging**: Use structured logging throughout

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**
   ```bash
   uv run pytest tests/ -v
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd notes_to_blog
uv venv
uv pip install -r requirements.txt

# Install development dependencies
uv pip install pytest pytest-cov pytest-mock

# Run tests
uv run pytest tests/ -v

# Run linting (if configured)
uv run flake8 src/ tests/
```

## 📊 Performance

### Benchmarks

- **Single Note Processing**: ~2-5 minutes (depending on content length)
- **Batch Processing**: ~10-30 minutes for 10 notes
- **Image Generation**: ~30-60 seconds per image
- **Research**: ~10-30 seconds per subheading

### Optimization Tips

1. **Use batch processing** for multiple notes
2. **Configure appropriate timeouts** in config
3. **Monitor API rate limits** for external services
4. **Use caching** for repeated research queries

## 🔒 Security

### API Key Management

- Store API keys in `.env` file (never commit to version control)
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage and costs

### Input Validation

- All user input is validated using Pydantic models
- File paths are sanitized and validated
- Content length and format are checked
- Malicious content is filtered

## 🐛 Troubleshooting

### Common Issues

**Configuration Errors**
```bash
# Validate configuration
uv run python main.py config --validate

# Check environment variables
echo $OPENROUTER_API_KEY
```

**API Errors**
```bash
# Check API key validity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://api.openrouter.ai/api/v1/models

# Monitor logs
tail -f logs/app.log
```

**Processing Errors**
```bash
# Run with debug mode
export DEBUG=true
uv run python main.py process-file note.md

# Check file permissions
ls -la inbox/ output/ images/
```

### Getting Help

1. **Check the logs**: `tail -f logs/app.log`
2. **Run with debug**: Set `DEBUG=true` in environment
3. **Validate config**: `uv run python main.py config --validate`
4. **Check status**: `uv run python main.py status`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for agent orchestration
- [OpenRouter](https://openrouter.ai/) for LLM access
- [Replicate](https://replicate.com/) for image generation
- [Brave Search](https://brave.com/search/) for web research
- [Typer](https://typer.tiangolo.com/) for CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

## 📈 Roadmap

- [ ] Support for more input formats (Word, PDF, etc.)
- [ ] Advanced image editing capabilities
- [ ] SEO optimization features
- [ ] Social media integration
- [ ] Multi-language support
- [ ] Web interface
- [ ] Plugin system for custom agents
- [ ] Real-time collaboration features

---

**Happy blogging! 🚀**
