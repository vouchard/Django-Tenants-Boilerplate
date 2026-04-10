# Contributing Guide

Thank you for your interest in this Django Multi-Tenant boilerplate!

## How to Contribute

### Reporting Issues

If you find bugs or have feature suggestions:
1. Check existing issues first
2. Create a new issue with detailed information
3. Include steps to reproduce (for bugs)
4. Provide context for feature requests

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow Django best practices
   - Maintain code consistency with existing style
   - Add docstrings to new functions/classes
   - Update documentation if needed

4. **Test your changes**
   ```bash
   docker-compose exec web python manage.py test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe what changes you made and why
   - Reference any related issues
   - Ensure all tests pass

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add comments for complex logic

### Commit Messages

Use clear, descriptive commit messages:
- `Add: new feature or file`
- `Fix: bug description`
- `Update: modification to existing feature`
- `Refactor: code improvement without changing functionality`
- `Docs: documentation changes`

### Testing

- Write tests for new features
- Ensure existing tests still pass
- Test multi-tenant isolation for tenant-specific features

### Documentation

- Update README.md if adding features
- Document new API endpoints in docstrings
- Update ARCHITECTURE.md for architectural changes
- Add testing instructions to TESTING.md if needed

## Areas for Contribution

### Potential Enhancements

1. **Testing**
   - Add comprehensive unit tests
   - Integration tests for tenant creation
   - API endpoint tests

2. **Features**
   - Tenant-specific settings/configuration
   - File upload with tenant isolation
   - Email sending functionality
   - Celery for background tasks
   - Redis caching
   - Rate limiting per tenant

3. **Security**
   - Additional security middleware
   - Rate limiting on public endpoints
   - Brute force protection
   - Audit logging

4. **DevOps**
   - Production-ready settings file
   - Gunicorn configuration
   - Nginx configuration
   - CI/CD pipeline examples
   - Kubernetes deployment files

5. **Documentation**
   - Video tutorials
   - More detailed examples
   - Deployment guides for different platforms
   - Troubleshooting guide

## Questions?

Feel free to open an issue for any questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
