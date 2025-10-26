# 🔐 Secrets Management - HashiCorp Vault

## 📋 نظرة عامة

إدارة احترافية للأسرار مع:
- HashiCorp Vault
- تدوير تلقائي كل 30 يوم
- تشفير end-to-end
- Audit logging

**الوقت المقدر:** 1-2 يوم  
**الصعوبة:** متوسطة  
**الأولوية:** 🔴 عالية

---

## 🎯 الأهداف

- [ ] Setup Vault server
- [ ] Configure Django integration
- [ ] Auto-rotation setup
- [ ] Secrets migration
- [ ] Audit logging

---

## 🛠️ التنفيذ السريع

### **1. تثبيت Vault**

```bash
# Docker Compose
docker run -d --name vault \
  -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=dev-token \
  vault:1.15

export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-token'

# Initialize
vault secrets enable -path=smartedu kv-v2
```

### **2. إضافة الأسرار**

```bash
# Database
vault kv put smartedu/database \
  host=localhost \
  port=5432 \
  name=smartedu \
  user=smartedu \
  password=SecurePass123

# Gemini API
vault kv put smartedu/ai/gemini \
  api_key=YOUR_GEMINI_KEY

# Telegram
vault kv put smartedu/telegram \
  bot_token=YOUR_BOT_TOKEN
```

### **3. Django Integration**

`backend/config/vault.py`:

```python
import hvac
from django.conf import settings

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN
        )
    
    def get_secret(self, path):
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point='smartedu'
        )
        return response['data']['data']

vault = VaultClient()
```

`backend/config/settings.py`:

```python
from config.vault import vault

# Database من Vault
db_config = vault.get_secret('database')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        **db_config
    }
}

# Gemini API Key
GEMINI_API_KEY = vault.get_secret('ai/gemini')['api_key']
```

### **4. Auto-Rotation Script**

`scripts/rotate_secrets.py`:

```python
import secrets
from datetime import datetime
from config.vault import vault

def rotate_database_password():
    # Generate new password
    new_password = secrets.token_urlsafe(32)
    
    # Update in database
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER USER smartedu WITH PASSWORD %s",
            [new_password]
        )
    
    # Update in Vault
    db_config = vault.get_secret('database')
    db_config['password'] = new_password
    db_config['rotated_at'] = datetime.now().isoformat()
    vault.client.secrets.kv.v2.create_or_update_secret(
        path='database',
        secret=db_config,
        mount_point='smartedu'
    )
    
    print(f"✅ Password rotated at {datetime.now()}")

if __name__ == '__main__':
    rotate_database_password()
```

---

## ✅ الاختبارات

```bash
# Test 1: Read secret
python -c "from config.vault import vault; print(vault.get_secret('database'))"

# Test 2: Rotation
python scripts/rotate_secrets.py

# Test 3: Django connection
python manage.py dbshell
```

---

## 📊 Checklist

- [ ] Vault installed
- [ ] Secrets migrated
- [ ] Django integrated
- [ ] Rotation tested
- [ ] Cron configured

---

**التالي:** [03 - Backup & DR →](./03_BACKUP_DISASTER_RECOVERY.md)
