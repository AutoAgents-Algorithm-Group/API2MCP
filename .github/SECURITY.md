# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Zeus seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do NOT:

- Open a public GitHub issue
- Disclose the vulnerability publicly until it has been addressed
- Exploit the vulnerability beyond what is necessary to demonstrate it

### Please DO:

1. **Email us privately** at the project maintainer's contact (check GitHub profile or open a private security advisory)
2. **Use GitHub's Security Advisory** feature:
   - Go to the repository's Security tab
   - Click "Report a vulnerability"
   - Fill in the details

### What to Include:

Please provide as much information as possible to help us understand and resolve the issue:

- **Type of vulnerability** (e.g., XSS, SQL injection, authentication bypass)
- **Full paths of source file(s)** related to the manifestation of the issue
- **Location of the affected source code** (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit it
- **Any special configuration** required to reproduce the issue

### What to Expect:

- **Initial Response**: Within 48 hours
- **Progress Updates**: At least every 7 days
- **Fix Timeline**:
  - Critical: Immediate response, fix ASAP
  - High: Fix within 30 days
  - Medium: Fix within 90 days
  - Low: Fix in next regular release

## Security Update Process

1. **Vulnerability Reported**: Security issue is submitted privately
2. **Acknowledgment**: We confirm receipt within 48 hours
3. **Assessment**: We evaluate severity and impact
4. **Fix Development**: Patch is developed and tested
5. **Coordinated Disclosure**: Fix is released and vulnerability is disclosed
6. **Credit**: Reporter is credited (unless anonymity is requested)

## Security Best Practices

When using Zeus, we recommend:

### Authentication

- Use strong passwords or authentication tokens
- Enable HTTPS in production
- Store API keys securely (environment variables, not in code)
- Regularly rotate credentials

### API Security

- Validate all inputs
- Use rate limiting to prevent abuse
- Implement proper CORS policies
- Keep dependencies up to date

### Deployment

- Use Docker with non-root users
- Keep all services behind a firewall
- Enable logging and monitoring
- Regular security audits

### Configuration

- Never commit `.env` files or secrets
- Use secret management tools (e.g., Docker secrets, Kubernetes secrets)
- Regularly review access permissions
- Enable security headers

## Known Security Considerations

### Current Security Features

- API authentication using session tokens
- CORS protection
- Input validation and sanitization
- SQL injection prevention (using ORM)
- XSS protection

### Areas Requiring Attention

Users should be aware of:

- **MCP Integration**: Ensure trusted MCP servers only
- **File Uploads**: Validate file types and sizes
- **Sandbox Execution**: Code execution happens in isolated environment
- **LLM API Keys**: Protect your API keys for OpenAI, Anthropic, etc.

## Disclosure Policy

- We aim to disclose vulnerabilities responsibly
- Coordination with reporters on disclosure timing
- Public disclosure after fix is available
- CVE assignment for significant vulnerabilities

## Security Hall of Fame

We appreciate the security researchers who help keep Zeus secure:

<!-- Security researchers will be listed here after verified reports -->

*Be the first to contribute to our security!*

## Contact

For security concerns, please use:

- GitHub Security Advisories (preferred)
- Project maintainer contacts (see GitHub profiles)

For general questions, use GitHub Issues instead.

## Acknowledgments

We follow security best practices inspired by:

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

Thank you for helping keep Zeus and our users safe! 🔒

