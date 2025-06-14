# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- `uv sync` - Install all dependencies (including dev dependencies)
- `uv sync --no-dev` - Install only production dependencies

### Running the Application
- `uv run streamlit run app/main.py` - Run Streamlit app locally on port 8080
- `docker build . -f Dockerfile --target prod --tag app && docker run -it --read-only -p 8080:8080 app` - Run in production-like container

### Code Quality
- `uv run ruff check .` - Run linter
- `uv run ruff format .` - Format code
- `uv run mypy .` - Type checking (configured in pyproject.toml)

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest tests/test_specific.py` - Run specific test file

### Package Management
- `uv add <package>` - Add production dependency
- `uv add --dev <package>` - Add development dependency

## Architecture

This is a Streamlit-based web application for a 1-day R&D internship program. The project uses:

- **Package Manager**: uv for fast Python dependency management
- **Web Framework**: Streamlit for rapid UI development
- **Data Visualization**: Plotly for charts, streamlit-agraph for network graphs
- **Code Quality**: Ruff for linting/formatting, MyPy for type checking
- **Testing**: pytest with Streamlit testing framework

### Project Structure
- `app/main.py` - Main Streamlit application entry point
- `app/dummy_data.csv` - Sample data for the application
- `app/crud/` - CRUD operations for business cards and contact history API
  - `models.py` - Pydantic models for API responses
  - `business_cards.py` - Business card CRUD operations
  - `contact_history.py` - Contact history CRUD operations
- `tests/` - Test files using pytest and Streamlit testing
- `.streamlit/config.toml` - Streamlit configuration (port 8080, minimal UI)

### Key Configuration
- Python version: >=3.10,<3.14
- Streamlit runs on port 8080
- Ruff configured with strict linting (line length 120, complexity max 5)
- Docker multi-stage build with dev/prod targets

## External API Integration

**Base URL**: https://circuit-trial.stg.rd.ds.sansan.com/api

### Business Cards API
- `GET /cards/` - List business cards (with pagination)
- `GET /cards/count` - Get total count of business cards
- `GET /cards/{user_id}` - Get specific business card by user ID
- `GET /cards/{user_id}/similar_top10_users` - Get top 10 similar users

### Contact History API  
- `GET /contacts/` - List contact histories (with pagination and date filtering)
- `GET /contacts/count` - Count contact histories
- `GET /contacts/owner_user/{user_id}` - Get contacts by owner user
- `GET /contacts/owner_company/{company_id}` - Get contacts by owner company

### CRUD Usage
```python
from app.crud import BusinessCardCRUD, ContactHistoryCRUD

# Initialize CRUD clients
business_cards = BusinessCardCRUD()
contacts = ContactHistoryCRUD()

# Example usage
cards = business_cards.get_all_cards(limit=50)
user_card = business_cards.get_card_by_user_id(12345)
similar_users = business_cards.get_similar_users(12345)
contact_history = contacts.get_all_contacts(limit=100)
```