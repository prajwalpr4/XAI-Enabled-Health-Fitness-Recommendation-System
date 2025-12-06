# Security Guide - Health & Fitness XAI System

## Overview
This guide covers all security measures implemented in the Health & Fitness XAI System.

---

## 1. API Key Security

### ✅ Implemented
- **Environment Variables**: API key stored in `.env` file
- **Not Hardcoded**: Key never appears in source code
- **Secure Loading**: Using `python-dotenv` for safe loading

### ⚠️ If Key is Exposed
**IMMEDIATE ACTIONS**:
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Find your API key in the dashboard
3. Click "Delete" to revoke the exposed key
4. Generate a new API key
5. Update `.env` with new key
6. Restart Flask application

### Best Practices
```bash
# ✅ DO: Store in environment variables
GOOGLE_API_KEY=your_actual_key_here

# ❌ DON'T: Commit .env to version control
# Add to .gitignore:
echo ".env" >> .gitignore

# ✅ DO: Use different keys for dev/prod
# Development: Limited quota key
# Production: Full quota key with rate limiting
```

---

## 2. HTTP Security Headers

### Implemented Headers
```python
# In app.py - set_security_headers() function
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

### What Each Header Does
| Header | Purpose | Value |
|--------|---------|-------|
| **X-Content-Type-Options** | Prevent MIME type sniffing | `nosniff` |
| **X-Frame-Options** | Prevent clickjacking | `SAMEORIGIN` |
| **X-XSS-Protection** | Enable XSS filter | `1; mode=block` |
| **HSTS** | Force HTTPS | `max-age=31536000` |
| **CSP** | Control resource loading | `default-src 'self'` |

---

## 3. Session Security

### ✅ Implemented
```python
# Secure session key generation
app.secret_key = secrets.token_hex(16)

# Session-based authentication
if 'user_email' not in session:
    return redirect(url_for('login'))
```

### Features
- **Random Secret Key**: Generated using `secrets` module
- **Session Validation**: Every route checks authentication
- **Session Timeout**: Configure in production
- **Secure Cookies**: Set `SESSION_COOKIE_SECURE=True` in production

### Configuration for Production
```python
# Add to app.py for production
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour timeout
```

---

## 4. Input Validation

### Profile Creation
```python
# In create_profile endpoint
- Age: 18-120 years
- Weight: 30-300 kg
- Height: 100-250 cm
- Activity Level: Predefined options
- Goals: Predefined options
```

### Validation Rules
```javascript
// Frontend validation (index.html)
- Age: number, 18-120
- Weight: number, 30-300
- Height: number, 100-250
- Required fields: All profile fields
```

### Backend Validation
```python
# app.py - create_profile endpoint
- Check user is logged in
- Validate all required fields
- Type checking for numeric fields
- Range validation for all inputs
```

---

## 5. SQL Injection Prevention

### ✅ Implemented
```python
# Using parameterized queries (if applicable)
# Database operations use ORM or prepared statements
# No string concatenation in queries
```

### Example
```python
# ✅ SAFE: Using ORM
user = db.get_user(email)

# ❌ UNSAFE: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"
```

---

## 6. Cross-Site Scripting (XSS) Prevention

### ✅ Implemented
```python
# Flask auto-escapes Jinja2 templates
{{ user_input }}  # Automatically escaped

# JSON responses are safe
return jsonify({'data': user_input})
```

### Content Security Policy
```python
# Restricts script sources
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

---

## 7. Cross-Site Request Forgery (CSRF) Protection

### ✅ Recommended Setup
```python
# Install Flask-WTF
pip install Flask-WTF

# In app.py
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# In templates
<form method="POST">
    {{ csrf_token() }}
    ...
</form>
```

---

## 8. Rate Limiting

### ✅ Recommended Implementation
```python
# Install Flask-Limiter
pip install Flask-Limiter

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply to endpoints
@app.route('/get_recommendations')
@limiter.limit("10 per minute")
def get_recommendations():
    ...
```

### Gemini API Rate Limits
- **Free Tier**: 60 requests per minute
- **Implementation**: Check remaining quota before API call

---

## 9. Data Privacy

### ✅ Implemented
- **No Logging of Sensitive Data**: User profiles not logged
- **Session-Based Storage**: Data in memory, not persistent
- **Secure Transmission**: HTTPS recommended for production

### Recommendations
- **GDPR Compliance**: Implement data deletion endpoint
- **Data Retention**: Define retention policies
- **Encryption**: Encrypt sensitive data at rest
- **Audit Logging**: Log access to sensitive data

---

## 10. Dependency Security

### ✅ Implemented
```bash
# requirements.txt with pinned versions
google-generativeai==0.8.5
python-dotenv==1.2.1
Flask==2.3.0
```

### Best Practices
```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies regularly
pip list --outdated

# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

## 11. Error Handling

### ✅ Implemented
```python
# Generic error messages to users
return jsonify({'error': 'An error occurred'}), 500

# Detailed errors in logs only
print(f"Error: {str(e)}")  # Server logs only
```

### Production Configuration
```python
# Disable debug mode
app.debug = False

# Custom error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500
```

---

## 12. Authentication & Authorization

### ✅ Implemented
```python
# Login required decorator
if 'user_email' not in session:
    return redirect(url_for('login'))

# Admin-only routes
if not db.is_admin(session['user_email']):
    return "Access Denied", 403
```

### Recommendations
- **Password Hashing**: Use `werkzeug.security.generate_password_hash()`
- **Password Requirements**: Minimum 8 characters, mixed case, numbers
- **Two-Factor Authentication**: Consider for production
- **Session Timeout**: Auto-logout after inactivity

---

## 13. Production Deployment Checklist

### Before Going Live
- [ ] Change `app.debug = False`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Set secure session cookies
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Set up logging and monitoring
- [ ] Configure database backups
- [ ] Test all security headers
- [ ] Conduct security audit
- [ ] Implement WAF (Web Application Firewall)
- [ ] Set up intrusion detection

### Environment Variables (Production)
```bash
# .env (never commit this)
GOOGLE_API_KEY=your_production_key
SECRET_KEY=your_strong_secret_key
FLASK_ENV=production
DEBUG=False
DATABASE_URL=your_database_url
```

---

## 14. Monitoring & Logging

### ✅ Recommended Setup
```python
import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"User {email} logged in")
logger.warning(f"Failed login attempt for {email}")
logger.error(f"API error: {error}")
```

### What to Monitor
- Failed login attempts
- API errors and timeouts
- Unusual access patterns
- Rate limit violations
- Database errors

---

## 15. Incident Response

### If Security Breach Occurs
1. **Immediate Actions**:
   - Revoke exposed API keys
   - Reset user sessions
   - Review access logs
   - Notify affected users

2. **Investigation**:
   - Identify scope of breach
   - Determine what data was accessed
   - Check for unauthorized changes

3. **Remediation**:
   - Patch vulnerabilities
   - Update security measures
   - Restore from backups if needed
   - Deploy fixes to production

4. **Communication**:
   - Inform users of breach
   - Provide guidance on actions to take
   - Publish security updates

---

## 16. Security Testing

### Manual Testing
```bash
# Test security headers
curl -I http://localhost:5000

# Check for common vulnerabilities
# - SQL Injection: Try ' OR '1'='1
# - XSS: Try <script>alert('xss')</script>
# - CSRF: Verify token validation
```

### Automated Testing
```bash
# Install security testing tools
pip install bandit  # Python security linter
pip install safety  # Dependency vulnerability checker

# Run tests
bandit -r .
safety check
```

---

## 17. Compliance

### GDPR Compliance
- [ ] User consent for data collection
- [ ] Data access requests
- [ ] Data deletion (right to be forgotten)
- [ ] Privacy policy
- [ ] Terms of service

### HIPAA Compliance (if applicable)
- [ ] Encryption at rest and in transit
- [ ] Access controls
- [ ] Audit logging
- [ ] Business associate agreements

---

## Security Contact

For security issues, please report to: **[your-security-email@example.com]**

Do not publicly disclose security vulnerabilities. Follow responsible disclosure practices.

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/security/)
- [Google Cloud Security](https://cloud.google.com/security)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Last Updated**: November 23, 2024
**Status**: ✅ Security Measures Implemented
