# 🔄 CI/CD Pipeline - GitHub Actions

## 📋 نظرة عامة

إعداد CI/CD Pipeline آلي كامل مع:
- Automated Testing
- Docker Build
- Canary Deployment
- Auto Rollback

**الوقت المقدر:** 2-3 أيام  
**الصعوبة:** متوسطة  
**الأولوية:** 🔴 عالية جداً

---

## 🎯 الأهداف

- [x] Setup GitHub Actions workflow
- [x] Lint & code quality checks
- [x] Unit tests with coverage >80%
- [x] Integration tests
- [x] Docker image build
- [x] Canary deployment
- [x] Auto rollback on failure

---

## 📦 المتطلبات

```bash
# Tools
- Git
- Docker
- GitHub account
- SSH access to servers

# Python packages
pip install flake8 black isort pytest pytest-cov bandit safety

# Server setup
- Staging server
- Production server
- HAProxy configured
```

---

## 🛠️ خطوات التنفيذ

### **الخطوة 1: إعداد هيكل المشروع**

```bash
# إنشاء المجلدات
mkdir -p .github/workflows
mkdir -p tests/{unit,integration,e2e}
mkdir -p scripts
```

### **الخطوة 2: إنشاء GitHub Actions Workflow**

إنشاء `.github/workflows/main.yml`:

```yaml
name: SmartEdu CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ═══════════ Stage 1: Lint ═══════════
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install flake8 black isort pylint bandit safety
          pip install -r backend/requirements.txt
      
      - name: Run flake8
        run: |
          cd backend
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127
      
      - name: Check code formatting
        run: |
          cd backend
          black --check .
          isort --check-only .
      
      - name: Run pylint
        run: |
          cd backend
          pylint apps/ --exit-zero
      
      - name: Security check (Bandit)
        run: |
          cd backend
          bandit -r . -f json -o bandit-report.json || true
      
      - name: Dependency security (Safety)
        run: |
          safety check --json || true
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: lint-reports
          path: backend/bandit-report.json

  # ═══════════ Stage 2: Unit Tests ═══════════
  unit-tests:
    needs: lint
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: test_smartedu
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-django pytest-asyncio
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_smartedu
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test-secret-key-for-ci
        run: |
          cd backend
          python manage.py migrate --noinput
      
      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_smartedu
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test-secret-key-for-ci
        run: |
          cd backend
          pytest tests/unit/ -v --cov=. --cov-report=xml --cov-report=html --cov-report=term
      
      - name: Check coverage threshold
        run: |
          cd backend
          coverage report --fail-under=80
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: unittests
          fail_ci_if_error: true
      
      - name: Upload coverage HTML
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: backend/htmlcov/

  # ═══════════ Stage 3: Integration Tests ═══════════
  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: test_smartedu
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-django
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_smartedu
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test-secret-key-for-ci
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY_TEST }}
        run: |
          cd backend
          python manage.py migrate --noinput
          pytest tests/integration/ -v --maxfail=3

  # ═══════════ Stage 4: Build Docker ═══════════
  build:
    needs: integration-tests
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    outputs:
      tags: ${{ steps.meta.outputs.tags }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}

  # ═══════════ Stage 5: Deploy Staging ═══════════
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.smartedu.sa
    
    steps:
      - name: Deploy to staging server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          port: 22
          script: |
            set -e
            cd /opt/smartedu
            
            echo "📥 Pulling latest image..."
            docker-compose pull
            
            echo "🔄 Restarting services..."
            docker-compose up -d
            
            echo "🗄️ Running migrations..."
            docker-compose exec -T web python manage.py migrate --noinput
            
            echo "📦 Collecting static files..."
            docker-compose exec -T web python manage.py collectstatic --noinput
            
            echo "🧹 Cleaning old images..."
            docker image prune -f
            
            echo "✅ Deployment completed!"
      
      - name: Wait for services to be ready
        run: |
          echo "⏳ Waiting for services..."
          sleep 30
      
      - name: Run smoke tests
        run: |
          echo "🧪 Running smoke tests..."
          curl -f https://staging.smartedu.sa/health/ || exit 1
          curl -f https://staging.smartedu.sa/api/health/ || exit 1
          echo "✅ Smoke tests passed!"
      
      - name: Send Telegram notification
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_ADMIN_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ✅ **Deployed to Staging**
            
            Branch: `${{ github.ref }}`
            Commit: `${{ github.sha }}`
            Author: ${{ github.actor }}
            
            🔗 https://staging.smartedu.sa

  # ═══════════ Stage 6: Deploy Production ═══════════
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://smartedu.sa
    
    steps:
      - name: Canary deployment (10% traffic)
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            set -e
            cd /opt/smartedu
            
            echo "🐤 Starting canary deployment..."
            
            # Backup current version
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml config > docker-compose.previous.yml
            
            # Deploy canary
            docker-compose -f docker-compose.canary.yml pull
            docker-compose -f docker-compose.canary.yml up -d
            
            # Route 10% traffic to canary
            /usr/local/bin/update-haproxy-canary.sh 10
            
            echo "✅ Canary deployed with 10% traffic"
      
      - name: Monitor canary for 5 minutes
        run: |
          echo "📊 Monitoring canary deployment..."
          for i in {1..10}; do
            echo "Check $i/10..."
            
            # Get error rate from metrics endpoint
            ERROR_RATE=$(curl -s https://smartedu.sa/metrics | grep 'http_requests_total{status="5' | awk '{sum+=$2} END {print sum}')
            TOTAL_REQUESTS=$(curl -s https://smartedu.sa/metrics | grep 'http_requests_total' | awk '{sum+=$2} END {print sum}')
            
            if [ "$TOTAL_REQUESTS" -gt 0 ]; then
              ERROR_PERCENT=$(echo "scale=4; $ERROR_RATE / $TOTAL_REQUESTS * 100" | bc)
              echo "Error rate: $ERROR_PERCENT%"
              
              if (( $(echo "$ERROR_PERCENT > 1.0" | bc -l) )); then
                echo "❌ Error rate too high: $ERROR_PERCENT%"
                exit 1
              fi
            fi
            
            sleep 30
          done
          
          echo "✅ Canary is healthy!"
      
      - name: Full rollout
        if: success()
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            set -e
            cd /opt/smartedu
            
            echo "🚀 Promoting canary to production..."
            
            # Route 50% traffic
            /usr/local/bin/update-haproxy-canary.sh 50
            sleep 60
            
            # Route 100% traffic
            /usr/local/bin/update-haproxy-canary.sh 100
            
            # Update main deployment
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
            
            # Run migrations
            docker-compose exec -T web python manage.py migrate --noinput
            
            # Remove canary
            docker-compose -f docker-compose.canary.yml down
            
            # Cleanup
            docker image prune -f
            
            echo "✅ Production deployment completed!"
      
      - name: Send success notification
        if: success()
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_ADMIN_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            🚀 **Deployed to Production**
            
            Version: `${{ github.sha }}`
            Author: ${{ github.actor }}
            Time: ${{ github.event.head_commit.timestamp }}
            
            🔗 https://smartedu.sa
            📊 https://status.smartedu.sa

  # ═══════════ Stage 7: Rollback ═══════════
  rollback:
    needs: deploy-production
    runs-on: ubuntu-latest
    if: failure()
    
    steps:
      - name: Rollback to previous version
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            set -e
            cd /opt/smartedu
            
            echo "🔄 Rolling back to previous version..."
            
            # Stop current deployment
            docker-compose down
            
            # Start previous version
            docker-compose -f docker-compose.previous.yml up -d
            
            echo "✅ Rollback completed!"
      
      - name: Send rollback notification
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_ADMIN_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ⚠️ **ROLLBACK EXECUTED**
            
            Deployment failed, reverted to previous version.
            
            Branch: `${{ github.ref }}`
            Commit: `${{ github.sha }}`
            Author: ${{ github.actor }}
            
            Please check logs: https://smartedu.sa/logs
```

### **الخطوة 3: إعداد Scripts المساعدة**

إنشاء `scripts/update-haproxy-canary.sh`:

```bash
#!/bin/bash
# Update HAProxy to route traffic to canary

CANARY_PERCENT=$1

if [ -z "$CANARY_PERCENT" ]; then
    echo "Usage: $0 <percentage>"
    exit 1
fi

# Update HAProxy config
cat > /etc/haproxy/haproxy.cfg <<EOF
backend django_backend
    balance roundrobin
    
    # Production servers
    server django1 django1:8000 check weight $((100 - CANARY_PERCENT))
    server django2 django2:8000 check weight $((100 - CANARY_PERCENT))
    
    # Canary server
    server canary canary:8000 check weight $CANARY_PERCENT
EOF

# Reload HAProxy
systemctl reload haproxy

echo "✅ HAProxy updated: $CANARY_PERCENT% to canary"
```

جعله قابل للتنفيذ:
```bash
chmod +x scripts/update-haproxy-canary.sh
sudo mv scripts/update-haproxy-canary.sh /usr/local/bin/
```

### **الخطوة 4: إعداد GitHub Secrets**

في GitHub Repository → Settings → Secrets and variables → Actions:

```bash
# Server access
STAGING_HOST=staging.smartedu.sa
PROD_HOST=smartedu.sa
SSH_USERNAME=deploy
SSH_PRIVATE_KEY=<your-ssh-private-key>

# API keys
GEMINI_API_KEY_TEST=<test-api-key>

# Notifications
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_ADMIN_CHAT_ID=<your-chat-id>
```

### **الخطوة 5: إنشاء Dockerfile المحسّن**

`backend/Dockerfile`:

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Make sure scripts are executable
RUN chmod +x docker-entrypoint.sh

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python manage.py health_check || exit 1

# Run as non-root user
RUN useradd -m -u 1000 smartedu && chown -R smartedu:smartedu /app
USER smartedu

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## ✅ الاختبارات

### **Test 1: Lint Check**

```bash
cd backend
flake8 .
black --check .
isort --check .
```

**النتيجة المتوقعة:** ✅ No errors

### **Test 2: Unit Tests**

```bash
cd backend
pytest tests/unit/ -v --cov=. --cov-report=term
```

**النتيجة المتوقعة:** ✅ Coverage >80%

### **Test 3: Integration Tests**

```bash
cd backend
pytest tests/integration/ -v
```

**النتيجة المتوقعة:** ✅ All tests pass

### **Test 4: Docker Build**

```bash
docker build -t smartedu:test backend/
docker run --rm smartedu:test python manage.py check
```

**النتيجة المتوقعة:** ✅ Build success

### **Test 5: Pipeline Test**

```bash
# Push to develop branch
git checkout -b test/ci-cd
git add .
git commit -m "test: CI/CD pipeline"
git push origin test/ci-cd
```

**النتيجة المتوقعة:** ✅ All stages pass

---

## 📊 معايير النجاح

- [ ] All lint checks pass
- [ ] Unit test coverage >80%
- [ ] Integration tests pass
- [ ] Docker image builds successfully
- [ ] Staging deployment works
- [ ] Canary deployment works
- [ ] Rollback works
- [ ] Notifications sent

---

## 🐛 Troubleshooting

### مشكلة: Tests fail locally

```bash
# الحل
python manage.py test --settings=config.settings.test
```

### مشكلة: Docker build fails

```bash
# الحل
docker system prune -a
docker build --no-cache -t smartedu backend/
```

### مشكلة: SSH connection fails

```bash
# الحل
ssh-keygen -R staging.smartedu.sa
ssh deploy@staging.smartedu.sa
```

---

## 📚 الموارد

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [pytest Documentation](https://docs.pytest.org/)

---

**التالي:** [02 - Secrets Management →](./02_SECRETS_MANAGEMENT.md)
