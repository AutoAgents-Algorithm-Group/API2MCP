# Contributing to Zeus

Thank you for your interest in contributing to Zeus! 🎉

We welcome contributions from everyone. This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Push to your fork and submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ and pnpm
- Docker and Docker Compose (optional)

### Backend Setup

```bash
cd ai-backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd web
pnpm install
```

### Running the Development Environment

```bash
# Start all services
make dev

# Or manually:
# Backend
cd ai-backend
python -m uvicorn src.api.main:app --reload --port 8000

# Frontend
cd web
pnpm dev
```

### Using Docker

```bash
# Start with Docker Compose
docker-compose -f docker/docker-compose.yml up

# Or use Makefile
make docker-up
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details**: OS, Python/Node version, browser, etc.

### Suggesting Features

Feature requests are welcome! Please provide:

- **Clear use case**: What problem does it solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **Additional context**: Any relevant examples or mockups

### Pull Requests

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Backend tests
   cd ai-backend
   pytest
   
   # Frontend tests
   cd web
   pnpm test
   ```

4. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/demos (if UI changes)

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Use `black` for formatting
- Use `ruff` for linting

```bash
# Format code
black .

# Lint code
ruff check .
```

### TypeScript/JavaScript (Frontend)

- Follow the existing code style
- Use TypeScript strict mode
- Use ESLint and Prettier
- Write meaningful variable/function names

```bash
# Lint and format
pnpm lint
pnpm format
```

### General Guidelines

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Write tests for new features
- Update documentation as needed

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(chat): add message streaming support
fix(api): resolve CORS issue with MCP endpoints
docs(readme): update installation instructions
refactor(workspace): simplify file upload logic
```

## Pull Request Process

1. **Update Documentation**: Ensure README and docs reflect your changes
2. **Update Tests**: Add/update tests for your changes
3. **Check CI**: Ensure all tests pass
4. **Request Review**: Tag maintainers for review
5. **Address Feedback**: Make requested changes
6. **Squash Commits**: Clean up commit history if needed

### PR Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings generated
- [ ] Related issues linked

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test updates

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Need Help?

- Check our [documentation](docs/)
- Read the [Architecture guide](docs/ARCHITECTURE.md)
- Open an issue with the `question` label
- Join our community discussions

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to Zeus! 🚀

