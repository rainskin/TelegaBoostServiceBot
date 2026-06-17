# README

## Telegram Boost Service Bot

Telegram бот для предоставления услуг по продвижению каналов/ботов и покупки Telegram Stars.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd TelegramBoostServiceBot
```

2. **Install dependencies**
```bash
poetry install
```

3. **Configure environment**
```bash
cp .env.sample .env
# Edit .env with your configuration
```

4. **Run the bot**
```bash
poetry run python src
```

### Docker Setup

```bash
# Build and run with docker-compose
docker-compose up -d

# Or run manually
docker build -t telegramboostservice .
docker run -d --name tg-bot telegramboostservice
```

## ✨ Features

### User Features
- 📝 User registration and authentication via Telegram
- 💰 Balance management with multiple payment methods
- 🛒 Order promotion services (likes, subscribers, views, etc.)
- ⭐ Buy and send Telegram Stars
- 👥 Referral system with rewards
- 🌍 Multi-language support (Russian, English)
- 📊 Order tracking and history

### Admin Features
- 👑 Admin panel via Telegram
- 📦 Order queue management
- 👥 User management
- 💳 Payment processing
- 📈 Statistics and reporting
- 🎯 Promo campaigns

### Technical Features
- ⚡ Fully asynchronous (async/await)
- 🔒 Secure payment integration
- 🔄 Automatic order processing
- 📝 Transaction logging
- 🌐 External API integration
- 🛡️ Rate limiting and security

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

### Key Components

```
src/
├── handlers/           # Telegram event handlers
├── busines_logic/      # Business logic layer
├── core/              # Core functionality
│   ├── db/           # Database layer
│   └── localisation/  # Localization
├── utils/             # Utilities and helpers
└── enums/             # Enumerations
```

## 💻 Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: aiogram 3.13.1
- **Database**: MongoDB (motor 3.4.0)
- **Async**: asyncio, aiohttp

### Payment Gateways
- **Yookassa** - Bank cards (RUB)
- **AAIO** - Cryptocurrency (USDT)
- **Telegram Stars** - Built-in payments

### Development Tools
- **Poetry** - Dependency management
- **Pytest** - Testing framework
- **Black** - Code formatter
- **Ruff** - Linter
- **MyPy** - Type checker

See [docs/tech-stack.md](docs/tech-stack.md) for complete technology stack.

## 📚 Documentation

### Core Documentation
- [Project Overview](docs/project-overview.md) - What this project is
- [Architecture](docs/architecture.md) - System design and structure
- [Tech Stack](docs/tech-stack.md) - Technologies used
- [Features](docs/features.md) - Implemented functionality
- [Current State](docs/current-state.md) - Project status

### Development Guides
- [Best Practices](docs/best-practices.md) - Coding standards and guidelines
- [Security Audit](docs/security-audit.md) - Security assessment
- [Refactoring Recommendations](docs/refactoring-recommendations.md) - Code improvement guide
- [Agent Guidelines](docs/agent-guidelines.md) - AI agent workflow
- [Prompt Template](docs/prompt-template.md) - Task assignment template

### External Documentation
- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)

## 🛠️ Development

### Setting Up Development Environment

1. **Install Poetry** (if not installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install dependencies**
```bash
poetry install
```

3. **Activate virtual environment**
```bash
poetry shell
```

### Code Quality

**Linting**
```bash
poetry run ruff check src/
poetry run ruff check --fix src/
```

**Type Checking**
```bash
poetry run mypy src/
```

**Formatting**
```bash
poetry run black src/
```

**All quality checks**
```bash
poetry run ruff check --fix src/ && poetry run mypy src/ && poetry run black src/
```

### Adding New Features

1. Read [docs/prompt-template.md](docs/prompt-template.md)
2. Follow [docs/best-practices.md](docs/best-practices.md)
3. Write tests
4. Run quality checks
5. Update documentation

### Project Structure

```
TelegramBoostServiceBot/
├── src/                    # Source code
│   ├── handlers/          # Telegram handlers
│   ├── busines_logic/     # Business logic
│   ├── core/              # Core functionality
│   ├── utils/             # Utilities
│   └── enums/             # Enums
├── docs/                  # Documentation
├── tests/                 # Tests
├── .env                   # Environment variables
├── pyproject.toml        # Project configuration
├── Dockerfile            # Docker image
└── docker-compose.yml    # Docker orchestration
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_file.py

# Run with verbose output
poetry run pytest -v
```

### Test Structure

```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
└── e2e/                 # End-to-end tests
```

### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_example():
    # Arrange
    # Act
    # Assert
    assert True
```

See [docs/best-practices.md](docs/best-practices.md#testing-best-practices) for testing guidelines.

## 🚢 Deployment

### Environment Variables

Required environment variables (see `.env.sample`):

```bash
# Bot Configuration
BOT_TOKEN=your_bot_token
BOT_URL=your_bot_url

# Database
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=tg_bot

# API Configuration
API_TOKEN=your_api_token
BASE_URL=https://api.example.com

# Payment Gateways
YOOKASSA_API_KEY=your_key
AAIO_API_KEY=your_key
TG_STARS_API_KEY=your_key

# Admin
ADMIN_ID=your_telegram_id
```

### Docker Deployment

```bash
# Build image
docker build -t telegramboostservice .

# Run container
docker run -d \
  --name tg-bot \
  --network backend \
  -e BOT_TOKEN=$BOT_TOKEN \
  -e MONGO_URL=$MONGO_URL \
  telegramboostservice
```

### Production Considerations

- [ ] Set up proper logging
- [ ] Configure monitoring
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Set up alerting
- [ ] Review security settings
- [ ] Enable audit logging

## 🔒 Security

See [docs/security-audit.md](docs/security-audit.md) for detailed security assessment.

### Security Best Practices
- ✅ All secrets in environment variables
- ✅ No hardcoded credentials
- ✅ Input validation
- ✅ Rate limiting
- ✅ Proper error handling
- ✅ Secure dependencies

## 📊 Current Status

**Version**: 0.1.0
**Status**: Active Development
**Last Updated**: March 2026

See [docs/current-state.md](docs/current-state.md) for detailed project status.

## 🤝 Contributing

When contributing to this project:

1. Read the documentation in `docs/`
2. Follow the coding standards in [docs/best-practices.md](docs/best-practices.md)
3. Write tests for new features
4. Run quality checks before committing
5. Update documentation as needed

## 📝 License

Add your license information here.

## 📞 Support

For support:
- Email: support@example.com
- Telegram: @support_bot
- Documentation: See `docs/` folder

## 🗺️ Roadmap

### Completed
- ✅ User registration and auth
- ✅ Balance management
- ✅ Order creation and processing
- ✅ Multiple payment methods
- ✅ Referral system
- ✅ Multi-language support

### In Progress
- 🔄 Security improvements
- 🔄 Testing coverage
- 🔄 Code refactoring

### Planned
- 📋 SBP (Yookassa)
- 📋 Additional payment methods
- 📋 Analytics dashboard
- 📋 Web interface
- 📋 API for external integration

## 📄 License

[Add your license here]

---

**Built with ❤️ using Python, aiogram, and MongoDB**

For detailed information, see the [docs/](docs/) folder.
