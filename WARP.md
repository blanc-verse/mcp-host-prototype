# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Jalin Web Host is a Chainlit-based web application that provides an intelligent data consultant interface called "Blanc". The system serves as a multilingual (Bahasa Indonesia) AI assistant that helps users analyze financial data through a conversational interface.

## Architecture Overview

### Core Components

1. **Main Application (`main.py`)**
   - Chainlit web application entry point
   - Handles authentication, data layer setup, and message routing
   - Integrates with SQLAlchemy for data persistence

2. **Service Layer Architecture**
   - **Agent Runner Services** (`services/agent_runner/`): Orchestrates AI agent execution
   - **Content Parsers** (`services/content_parser/`): Handles message format conversion between Chainlit and AI models
   - **File Storage Services** (`services/file_storage/`): Manages file uploads and storage
   - **Application Services** (`services/application/`): Core application utilities

3. **AI Agent Integration**
   - Supports multiple AI providers: OpenAI, Gemini, Claude (Anthropic)
   - Uses OpenAI Agents framework with MCP (Model Context Protocol) servers
   - Integrates code interpreter tools for data analysis

4. **Data Processing**
   - Handles Excel (.xlsx, .xls, .xlsm) and CSV file uploads
   - PostgreSQL database integration via SQLAlchemy
   - Memory management through SQLAlchemy sessions

## Development Commands

### Environment Setup
```bash
# Copy environment template and configure
cp .env.example .env

# Install dependencies using uv
uv sync
```

### Development
```bash
# Start development server with hot reload
make dev
# or manually:
uv run chainlit run main.py -w
```

### Testing
```bash
# Run tests using ADK
make test
# or manually:
adk web ./clients
```

### Database Setup
Ensure PostgreSQL is running and update the `DATABASE_URL` in your `.env` file:
```
DATABASE_URL=postgresql://postgres:@localhost:5432/postgres
```

## Configuration Requirements

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI GPT models
- `GEMINI_API_KEY`: Required for Google Gemini models
- `ANTHROPIC_API_KEY`: Required for Claude models
- `DATABASE_URL`: PostgreSQL connection string
- `CHAINLIT_AUTH_SECRET`: Authentication secret (generate with `chainlit create-secret`)

### MCP Server Integration
The system expects a Finance Database MCP server running on `http://127.0.0.1:8010/mcp`. This external service provides database access capabilities to the AI agents.

## Key Development Patterns

### Adding New AI Providers
1. Create a new runner service in `services/agent_runner/`
2. Implement corresponding content parser in `services/content_parser/`
3. Follow the existing pattern from OpenAI or Gemini implementations

### Content Parser Extension
- Parsers handle bidirectional conversion between Chainlit messages and AI model formats
- Support for file attachments (Excel, CSV) with automatic DataFrame conversion
- Image and file artifact handling with local storage

### Agent Configuration
The main agent "Blanc" is configured as:
- Indonesian data consultant persona
- Formal Bahasa Indonesia communication
- Mentoring approach for non-technical users
- Code interpreter capabilities for data analysis

## File Upload Handling

### Supported Formats
- **Excel files**: .xlsx, .xls, .xlsm (converted to CSV for processing)
- **CSV files**: Direct pandas DataFrame conversion
- **Images**: PNG, JPG, JPEG (stored in artifacts directory)

### Artifact Management
Generated files (charts, reports) are stored locally in the artifacts directory and served through Chainlit's element system.

## Authentication
Simple credential-based authentication is implemented with default admin/admin credentials. This should be updated for production use.

## Development Notes

- The system uses SQLAlchemy async sessions for database operations
- Agent sessions are managed per user/session ID
- File storage is currently local disk-based
- The application supports streaming responses from AI models
- Memory is persisted across conversations through database storage