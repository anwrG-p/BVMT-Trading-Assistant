# Contributing Guidelines

Thank you for your interest in contributing to the BVMT Trading Assistant!

## Code of Conduct

We are committed to providing a welcoming community. Please see our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

- **Check Issues**: Ensure the bug hasn't already been reported.
- **Open an Issue**: Use the "Bug Report" template. Include:
  - Docker logs (`docker logs bvmt-app`).
  - Input data sample (if reproducible).
  - Expected vs. Actual behavior.

### Suggesting Features

- **Open an Issue**: Use the "Feature Request" template.
- **Discuss**: Engage in discussion to refine the idea.

### Pull Request Process

1.  **Fork the Repo**: Create your own copy of the repository.
2.  **Create a Branch**: `git checkout -b feature/your-feature-name`.
3.  **Implement Changes**: Write code and tests.
4.  **Run Tests**: Ensure `pytest` passes.
5.  **Commit**: Use descriptive messages (e.g., `feat: add bollinger bands`).
6.  **Push**: `git push origin feature/your-feature-name`.
7.  **Open PR**: Submit a Pull Request against the `main` branch.

## Development Setup

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for detailed instructions.

### Code Style

- **Python**: Follow PEP 8. Use `black` and `isort`.
- **Docstrings**: Google Style.

Example:

```python
def my_function(arg1: int) -> int:
    """
    Description of function.

    Args:
        arg1: Description of arg1.

    Returns:
        Description of return value.
    """
    return arg1 * 2
```

## Review Process

- Maintainers will review your PR within 1 week.
- Address feedback promptly.
- Once approved, your PR will be merged.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
