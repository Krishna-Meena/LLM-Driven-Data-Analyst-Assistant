# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email: **[your-email@example.com]**

### What to include in your report

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)

### Response timeline

- **Acknowledgment**: Within 48 hours of the initial report
- **Assessment**: Within 7 days
- **Fix & Disclosure**: Coordinated with the reporter

## Security Design Principles

This project follows these security practices:

1. **100% Local Processing**: All data processing and LLM inference happens locally. No data is transmitted to external APIs or cloud services.
2. **No Credential Storage**: The application does not store passwords, API keys, or authentication tokens. All configuration is environment-based.
3. **Environment Variables**: Sensitive configuration is managed through `.env` files which are excluded from version control via `.gitignore`.
4. **Dependency Auditing**: Dependencies are locked via `uv.lock` and can be audited for known vulnerabilities.
5. **Input Sanitization**: User-uploaded files are validated by extension and parsed through established libraries (Pandas, PyArrow, OpenPyXL).

## Dependencies

This project relies on well-maintained, widely-used open source libraries. We recommend regularly updating dependencies:

```bash
uv sync --upgrade
```
