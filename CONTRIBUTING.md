# Contributing to EchoForge

Thank you for your interest in contributing to EchoForge! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional. We're building something great together.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/echoforge/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python/Node versions)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing [Discussions](https://github.com/yourusername/echoforge/discussions)
2. Open a new discussion describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - Why this benefits the community

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend && pytest tests/

   # Frontend (when tests exist)
   cd frontend && npm test
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add awesome new feature"
   ```

   Use conventional commit prefixes:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation
   - `style:` formatting
   - `refactor:` code restructure
   - `test:` adding tests
   - `chore:` maintenance

6. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```

## Development Setup

### Prerequisites
- macOS 11.0+ (for now)
- Python 3.9+
- Node.js 18+
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/echoforge.git
cd echoforge

# Run installation
./install-mac.sh

# Create feature branch
git checkout -b feature/my-feature
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions focused and small

### JavaScript/React
- Use modern ES6+ syntax
- Prefer functional components
- Use meaningful variable names
- Add comments for complex logic

### General
- Keep code DRY (Don't Repeat Yourself)
- Write self-documenting code
- Add comments for "why", not "what"

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Writing Tests

- Test new features
- Test edge cases
- Test error handling
- Aim for 80%+ coverage

## Documentation

- Update README.md for user-facing changes
- Update relevant documentation in `/docs`
- Add docstrings to new functions
- Update API documentation if needed

## Areas We Need Help

- 🧪 Writing more tests
- 📱 Mobile responsive improvements
- 🌍 Internationalization (i18n)
- 🎨 UI/UX enhancements
- 📝 Documentation improvements
- 🐛 Bug fixes
- ⚡ Performance optimizations

## Questions?

- Open a [Discussion](https://github.com/yourusername/echoforge/discussions)
- Check existing documentation
- Ask in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to EchoForge! 🎤
