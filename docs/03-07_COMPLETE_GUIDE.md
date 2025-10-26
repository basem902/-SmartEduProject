# 📘 الدليل الشامل - الخطوات 3-7

---

# 3️⃣ Backup & Disaster Recovery

## الهدف
نسخ احتياطي يومي + اختبار استعادة شهري + تخزين خارجي مشفر

## الخطوات

### 1. Backup Script

`scripts/backup.sh`:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# Database
docker-compose exec -T postgres pg_dump smartedu | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Media
tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" /opt/smartedu/media/

# Encrypt
gpg --encrypt --recipient backup@smartedu.sa "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Upload to S3 (Wasabi)
aws s3 cp "$BACKUP_DIR/db_$TIMESTAMP.sql.gz.gpg" "s3://smartedu-backups/db/"

# Cleanup (keep 7 days local)
find "$BACKUP_DIR" -name "*.gz*" -mtime +7 -delete

echo "✅ Backup completed"
```

### 2. Restore Test

`scripts/test_restore.sh`:
```bash
#!/bin/bash
BACKUP_FILE=$1

# Download
aws s3 cp "$BACKUP_FILE" /tmp/test_backup.sql.gz.gpg

# Decrypt
gpg --decrypt /tmp/test_backup.sql.gz.gpg > /tmp/test_backup.sql.gz
gunzip /tmp/test_backup.sql.gz

# Create test DB
docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE test_restore;"

# Restore
docker-compose exec -T postgres psql -U postgres -d test_restore < /tmp/test_backup.sql

# Verify
RECORDS=$(docker-compose exec -T postgres psql -U postgres -d test_restore -t -c "SELECT COUNT(*) FROM auth_user;")
if [ "$RECORDS" -gt 0 ]; then
    echo "✅ Restore successful!"
else
    echo "❌ Restore failed!"
    exit 1
fi

# Cleanup
docker-compose exec -T postgres psql -U postgres -c "DROP DATABASE test_restore;"
```

### 3. Cron Jobs

```bash
# Daily backup at 2 AM
0 2 * * * /opt/smartedu/scripts/backup.sh >> /var/log/backup.log 2>&1

# Monthly restore test
0 3 1 * * /opt/smartedu/scripts/test_restore.sh $(aws s3 ls s3://smartedu-backups/db/ | tail -1 | awk '{print $4}')
```

## الاختبارات

```bash
# Test backup
bash scripts/backup.sh

# Test restore
bash scripts/test_restore.sh s3://smartedu-backups/db/latest.sql.gz.gpg

# Verify S3
aws s3 ls s3://smartedu-backups/db/
```

---

# 4️⃣ Load Testing

## الهدف
اختبار تحميل منهجي باستخدام K6

## الخطوات

### 1. Install K6

```bash
# macOS
brew install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### 2. Stress Test

`tests/load/stress-test.js`:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://smartedu.sa';

export default function () {
  // Test homepage
  let res = http.get(`${BASE_URL}/`);
  check(res, { 'status 200': (r) => r.status === 200 });
  
  sleep(1);
  
  // Test API
  res = http.get(`${BASE_URL}/api/health/`);
  check(res, {
    'health status 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500,
  });
  
  sleep(2);
}
```

### 3. Run Tests

```bash
# Stress test
k6 run --vus 100 --duration 10m tests/load/stress-test.js

# Spike test
k6 run --vus 500 --duration 30s tests/load/stress-test.js

# Soak test (8 hours)
k6 run --vus 50 --duration 8h tests/load/stress-test.js
```

---

# 5️⃣ SLA/SLO Monitoring

## الهدف
تعريف SLOs ومراقبتها مع compensation plan

## Service Level Objectives

```yaml
availability:
  target: 99.9%
  measurement: 30 days
  
latency:
  p95: 500ms
  p99: 1000ms
  measurement: 24h
  
error_rate:
  target: 0.1%
  measurement: 24h
```

## SLA Compensation

```yaml
uptime_guarantees:
  - 99.9%+: No credit
  - 99.0-99.9%: 10% refund
  - 98.0-99.0%: 25% refund
  - <98.0%: 50% refund
```

## Monitoring

`backend/apps/monitoring/slo.py`:
```python
from prometheus_client import Gauge, Counter

availability_gauge = Gauge('slo_availability', 'Availability')
latency_histogram = Histogram('slo_latency', 'Latency')
error_counter = Counter('slo_errors', 'Errors')

class SLOTracker:
    def track_availability(self):
        uptime = self.calculate_uptime_percentage()
        availability_gauge.set(uptime)
        
        if uptime < 99.9:
            self.send_alert(f"Availability: {uptime}%")
    
    def track_latency(self):
        p95 = self.get_p95_latency()
        latency_histogram.observe(p95)
        
        if p95 > 500:
            self.send_alert(f"P95 latency: {p95}ms")
```

---

# 6️⃣ Log Retention

## الهدف
إدارة احترافية للـ logs مع Loki + Grafana

## Setup Loki Stack

`docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./promtail-config.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  loki_data:
  grafana_data:
```

## Retention Policy

```yaml
logs:
  error: 90 days
  access: 30 days
  audit: 1 year
  debug: 7 days

storage_budget:
  loki: 5GB/month = 0.075 ريال
  prometheus: 10GB/month = 0.15 ريال
```

## Django Logging

`settings.py`:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'loki': {
            'class': 'logging_loki.LokiHandler',
            'url': 'http://loki:3100/loki/api/v1/push',
            'tags': {'app': 'smartedu'},
        }
    },
    'loggers': {
        'django': {
            'handlers': ['loki'],
            'level': 'INFO',
        }
    }
}
```

---

# 7️⃣ Privacy & Compliance

## الهدف
الامتثال للخصوصية والقوانين السعودية + GDPR

## تشفير البيانات

### At Rest
```python
# models.py
from django_cryptography.fields import encrypt

class Student(models.Model):
    name = encrypt(models.CharField(max_length=100))
    phone = encrypt(models.CharField(max_length=20))
```

### At Transit
```nginx
# nginx.conf
ssl_protocols TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

## Data Retention

```python
# Delete inactive data after 3 years
from datetime import timedelta
from django.utils import timezone

def cleanup_old_data():
    cutoff = timezone.now() - timedelta(days=365*3)
    
    Student.objects.filter(
        last_active__lt=cutoff
    ).delete()
```

## User Consent

`templates/consent.html`:
```html
<form>
  <h3>نموذج الموافقة</h3>
  
  <label>
    <input type="checkbox" required>
    أوافق على جمع ومعالجة بياناتي التعليمية
  </label>
  
  <label>
    <input type="checkbox" required>
    أوافق على استخدام AI لتقييم المشاريع
  </label>
  
  <label>
    <input type="checkbox">
    أوافق على تلقي إشعارات Telegram
  </label>
  
  <p>
    يمكنك سحب موافقتك في أي وقت من إعدادات الحساب.
  </p>
  
  <button type="submit">تأكيد الموافقة</button>
</form>
```

## GDPR Rights

```python
# views.py
@api_view(['GET'])
def export_my_data(request):
    """Right to access"""
    data = {
        'profile': StudentSerializer(request.user.student).data,
        'projects': ProjectSerializer(request.user.projects.all(), many=True).data,
        'submissions': SubmissionSerializer(request.user.submissions.all(), many=True).data,
    }
    return Response(data)

@api_view(['DELETE'])
def delete_my_data(request):
    """Right to be forgotten"""
    request.user.student.delete()
    request.user.delete()
    return Response({'message': 'Data deleted'})
```

## Saudi Data Residency

```yaml
hosting:
  primary: Saudi Arabia / GCC
  backup: GCC region only
  no_data_transfer: outside GCC
```

---

# ✅ Checklist النهائي

```
□ 03 - Backup & DR
  □ Daily backups configured
  □ Restore tested
  □ S3 storage setup
  □ Encryption enabled

□ 04 - Load Testing
  □ K6 installed
  □ Stress test passed
  □ Soak test passed
  □ Thresholds defined

□ 05 - SLA/SLO
  □ SLOs defined
  □ Monitoring active
  □ Alerts configured
  □ Compensation plan

□ 06 - Logging
  □ Loki + Grafana setup
  □ Retention policy
  □ Dashboards created
  □ Alerts working

□ 07 - Privacy
  □ Encryption (rest + transit)
  □ Consent forms
  □ GDPR rights
  □ Saudi compliance
```

---

**الخطوة التالية:** [08 - Deployment Checklist →](./08_DEPLOYMENT_CHECKLIST.md)
