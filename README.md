# GitHub Webhook Listener

A production-ready FastAPI server that receives and processes GitHub webhook events, stores them in PostgreSQL, and sends real-time notifications via Telegram and Email.

Project Explanation: GitHub Webhook Listener
---
How It Works
flowchart LR
    A[GitHub Events] -->|POST| B[FastAPI /webhook/github]
    B --> C[PostgreSQL Database]
    B --> D[Notifications]
    D --> E[Telegram]
    D --> F[Email]

## Features

- **Receive GitHub Webhooks** - Handles push, pull_request, and issues events
- **Security** - HMAC SHA256 signature verification
- **Idempotency** - Prevents duplicate event processing
- **Database Storage** - PostgreSQL with SQLAlchemy ORM
- **Notifications** - Telegram bot and Email alerts
- **Clean Architecture** - Modular structure with routes, services, utils
- **JSON Logging** - Structured logging for production
- **Error Handling** - Proper HTTP responses and validation

---

## Project Structure

```
project/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── database/
│   │   └── connection.py           # Database connection
│   ├── models/
│   │   └── webhook_event.py        # SQLAlchemy model
│   ├── routes/
│   │   └── webhook.py             # API endpoints
│   ├── schemas/
│   │   ├── webhook.py              # Pydantic schemas
│   │   └── notification.py
│   ├── services/
│   │   ├── event_processor.py      # Event handling logic
│   │   └── notification_service.py # Telegram & Email
│   └── utils/
│       ├── signature.py            # HMAC verification
│       ├── logging.py              # JSON logging setup
│       └── formatters.py           # Message formatting
├── tests/
│   └── test_webhook.py            # Unit tests
├── .env                           # Environment variables
├── requirements.txt               # Dependencies
└── README.md
```

---

## Installation

### 1. Clone and Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# GitHub Webhook Secret (from GitHub settings)
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=alerts@example.com

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE webhook_db;"
```

---

## Usage

### Start the Server

```bash
# Development
python3 -m uvicorn app.main:app --reload --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Local Testing with ngrok

For local development, use ngrok to expose your server:

```bash
# Terminal 1: Start server
python3 -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start ngrok
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok-free.app`)

---

## GitHub Webhook Setup

### 1. Create ngrok URL

```
https://abc123.ngrok-free.app/webhook/github
```

### 2. Configure in GitHub

1. Go to your repository: `Settings > Webhooks > Add webhook`
2. Fill in:
   - **Payload URL**: Your ngrok URL
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret
   - **Events**: Select events to receive (push, pull_request, issues)
3. Click **Add webhook**

### 3. Test Webhook

Push to your repository and check:
- Telegram notification received
- Logs show the event
- Database has the record

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhook/github` | Receive GitHub webhook |
| GET | `/webhook/health` | Health check |
| GET | `/` | API info |

### Webhook Headers

| Header | Required | Description |
|--------|----------|-------------|
| `X-GitHub-Event` | Yes | Event type (push, pull_request, issues) |
| `X-GitHub-Delivery` | Yes | Unique event ID |
| `X-Hub-Signature-256` | Yes | HMAC signature |

### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Event processed successfully |
| 400 | Missing required headers or invalid JSON |
| 401 | Invalid signature |
| 500 | Server error |

---

## Telegram Setup

### 1. Create a Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts to get your bot token

### 2. Get Your Chat ID

1. Start a chat with your new bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find your chat ID in the response

### 3. Configure

Add to `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## Email Setup (Gmail)

### 1. Enable 2-Factor Authentication

Go to your Google Account > Security > 2-Step Verification

### 2. Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Create a new app password
3. Copy the 16-character password

### 3. Configure

Add to `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

---

## Event Payloads

### Push Event

```json
{
  "event_type": "push",
  "repository": "owner/repo",
  "branch": "main",
  "commits": [
    {
      "message": "fix: bug in login",
      "author": "John Doe",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Pull Request Event

```json
{
  "event_type": "pull_request",
  "action": "opened",
  "pr_title": "Add new feature",
  "pr_user": "username",
  "repository": "owner/repo"
}
```

### Issue Event

```json
{
  "event_type": "issues",
  "action": "opened",
  "issue_title": "Bug: something is broken",
  "issue_user": "username",
  "repository": "owner/repo"
}
```

---

## Database Schema

```sql
CREATE TABLE webhook_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    delivery_status VARCHAR(20) DEFAULT 'received',
    payload TEXT NOT NULL,
    commit_messages TEXT,
    author VARCHAR(100),
    timestamp VARCHAR(50),
    pr_title VARCHAR(500),
    pr_action VARCHAR(50),
    pr_user VARCHAR(100),
    issue_title VARCHAR(500),
    issue_status VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Testing

```bash
# Run tests
pytest tests/ -v

# Test locally with curl
curl -X POST http://localhost:8000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-123" \
  -d '{"ref": "refs/heads/main", "commits": []}'
```

---

## Security

### Signature Verification

Every webhook request is verified using HMAC SHA256:

```python
signature = hmac.new(
    secret.encode(),
    payload,
    hashlib.sha256
).hexdigest()
```

### Best Practices

1. **Use HTTPS** - Always use SSL/TLS
2. **Keep secrets safe** - Never commit `.env` to git
3. **Validate payloads** - Check required fields
4. **Rate limiting** - Add rate limiting for production
5. **Log everything** - Monitor for suspicious activity

---

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  webhook:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/webhook/health
```

### Logs

Logs are output in JSON format:

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "name": "webhook_listener",
  "message": "Event processed successfully"
}
```

---

## Troubleshooting

### Server won't start

```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Check environment variables
cat .env
```

### Telegram not working

```bash
# Test bot directly
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Test"
```

### ngrok errors

```bash
# Restart ngrok
ngrok http 8000

# Check if port is in use
lsof -i :8000
```

---

## License

MIT License - See LICENSE file for details

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## Support

For issues or questions, please open an issue on GitHub.
