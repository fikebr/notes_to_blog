# Project Requirements Document (PRD)
## Notes to Blog Post Application

### 1. Project Overview

**Project Name:** Notes to Blog Post Application  
**Version:** 1.0  
**Date:** 2025-01-27  

#### 1.1 Purpose
An automated application that transforms unorganized notes into well-structured blog posts using AI agents, research capabilities, and image generation.

#### 1.2 Core Functionality
- Convert raw notes into comprehensive blog posts
- Automate research and content expansion
- Generate relevant images
- Structure content with proper formatting and metadata

### 2. Technical Architecture

#### 2.1 Design Patterns
- **DRY (Don't Repeat Yourself):** Abstract common functionality to reduce repetition
- **Adapter Pattern:** Create middleware layers between code and external libraries
- **Microservices Architecture:** Build as suite of small, focused services

#### 2.2 Technology Stack
- **Core Framework:** Python with CrewAI for agent orchestration
- **LLM Interface:** OpenRouter API
- **Image Generation:** Replicate.com text-to-image service
- **Web Search:** Brave Browser API
- **Data Models:** Pydantic for type safety and validation
- **Configuration:** python-dotenv for secrets, config.py for settings
- **Storage:** PickleDB as Redis alternative
- **Package Management:** UV for virtual environments and dependencies
- **Testing:** Pytest framework

### 3. Functional Requirements

#### 3.1 Core Process Flow
1. **Input Processing**
   - Monitor inbox folder for new notes files
   - Validate and parse input notes

2. **Content Analysis & Planning**
   - Summarize raw notes
   - Generate blog post title and description
   - Create content outline with 2-5 subheadings

3. **Content Development**
   - Write introduction and conclusion
   - Research content for each subheading
   - Expand and write subheading content

4. **Media Generation**
   - Create prompts for header and supplemental images
   - Generate images using Replicate.com
   - Link images in blog post content

5. **Metadata & Organization**
   - Select category from predefined list
   - Choose 2-5 relevant tags
   - Generate frontmatter header
   - Create appropriate filename

6. **Output Generation**
   - Write complete markdown file with frontmatter
   - Save images to target location
   - Validate final output

#### 3.2 Content Categories
Predefined categories for blog post classification:
- development
- computer
- home
- ai
- business
- crafting
- health
- diy
- recipes

#### 3.3 Output Format
**Markdown Structure:**
```markdown
+++
title = "Blog Post Title"
description = "Post description"
date = YYYY-MM-DD
draft = true

[taxonomies]
categories=["selected_category"]
tags=["tag1", "tag2", "tag3"]
+++

[Content body with images]
```

### 4. Technical Requirements

#### 4.1 Code Standards
- **Naming Convention:** snake_case for all identifiers
- **Function Names:** Descriptive with auxiliary verbs (e.g., `open_image_list_file`)
- **Variable Names:** Descriptive with auxiliary verbs (e.g., `is_active`, `has_permission`)

#### 4.2 Type Safety & Validation
- All Python functions must use proper type hints
- Pydantic models for all data structures
- Comprehensive input validation

#### 4.3 Documentation
- Every function requires a docstring (max 3 lines)
- Prioritize descriptive function names over lengthy documentation
- Maintain clear code structure and readability

#### 4.4 Error Handling
- Implement graceful error catching throughout
- Handle errors at function beginning with early returns
- Report error message, function name, and line number
- Avoid deeply nested conditional statements

#### 4.5 Logging
- Implement comprehensive logging system
- Log to both file and console output
- Include file rotation (10MB max, 3 backup files)
- Use structured logging format with timestamps

### 5. External Dependencies

#### 5.1 API Integrations
- **CrewAI:** Agent orchestration and workflow management
- **OpenRouter:** LLM interface for content generation
- **Replicate.com:** Text-to-image generation
- **Brave Browser API:** Web search capabilities

#### 5.2 Configuration Management
- **Environment Variables:** .env file for API keys and secrets
- **Application Config:** config.py for application settings
- **Templates:** Stored templates for frontmatter, agent prompts, and crew prompts as editable .txt files

### 6. File Structure

```
notes_to_blog/
├── docs/
│   ├── notes.md
│   └── PRD.md
├── src/
│   ├── logger.py
│   ├── config.py
│   ├── models/
│   ├── services/
│   └── agents/
├── templates/
│   ├── frontmatter_template.md
│   ├── agent_prompts/
│   │   ├── content_analyzer.txt
│   │   ├── researcher.txt
│   │   ├── content_writer.txt
│   │   ├── image_generator.txt
│   │   └── metadata_generator.txt
│   └── crew_prompts/
│       └── blog_post_crew.txt
├── inbox/
├── output/
├── images/
├── main.py
├── pyproject.toml
├── requirements.txt
└── .env
```

### 7. Quality Assurance

#### 7.1 Testing Strategy
- Unit tests for all functions using pytest
- Integration tests for API interactions
- End-to-end tests for complete workflow

#### 7.2 Performance Requirements
- Process notes files within reasonable time limits
- Handle concurrent processing if needed
- Efficient image generation and storage

#### 7.3 Security Considerations
- Secure API key management
- Input validation and sanitization
- Safe file operations

### 8. Deployment & Operations

#### 8.1 Environment Setup
- Use UV for virtual environment management
- Automated dependency installation
- Environment-specific configurations

#### 8.2 Monitoring
- Comprehensive logging for debugging
- Performance metrics tracking
- Error monitoring and alerting

### 9. Success Criteria

#### 9.1 Functional Success
- Successfully convert notes to well-structured blog posts
- Generate relevant and high-quality images
- Maintain consistent output format and quality

#### 9.2 Technical Success
- Zero critical errors in production
- All tests passing
- Performance within acceptable limits
- Maintainable and extensible codebase

### 10. Future Enhancements

#### 10.1 Potential Features
- Support for multiple input formats
- Advanced image editing capabilities
- SEO optimization features
- Social media integration
- Multi-language support

#### 10.2 Scalability Considerations
- Support for batch processing
- Distributed processing capabilities
- Enhanced caching mechanisms
- API rate limiting and optimization 