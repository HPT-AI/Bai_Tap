# Environment Variables Documentation

## Tổng quan

Tài liệu này mô tả chi tiết tất cả environment variables được sử dụng trong hệ thống Website Dịch vụ Toán học.

### File cấu hình
- **Development**: `.env.development`
- **Staging**: `.env.staging`
- **Production**: `.env.production`
- **Example**: `.env.example` (template)

---

## 🗄️ Database Configuration

### PostgreSQL Database URLs

#### USER_SERVICE_DB_URL
```bash
USER_SERVICE_DB_URL=postgresql://postgres:postgres123@postgres:5432/user_service_db
```
**Mô tả**: Connection string cho User Service database
**Format**: `postgresql://username:password@host:port/database_name`
**Sử dụng**: User authentication, profile management, balance tracking

#### PAYMENT_SERVICE_DB_URL
```bash
PAYMENT_SERVICE_DB_URL=postgresql://postgres:postgres123@postgres:5432/payment_service_db
```
**Mô tả**: Connection string cho Payment Service database
**Sử dụng**: Transaction processing, payment methods, audit logs

#### MATH_SOLVER_DB_URL
```bash
MATH_SOLVER_DB_URL=postgresql://postgres:postgres123@postgres:5432/math_solver_db
```
**Mô tả**: Connection string cho Math Solver Service database
**Sử dụng**: Problem catalog, solution storage, statistics

#### CONTENT_SERVICE_DB_URL
```bash
CONTENT_SERVICE_DB_URL=postgresql://postgres:postgres123@postgres:5432/content_service_db
```
**Mô tả**: Connection string cho Content Service database
**Sử dụng**: CMS pages, FAQs, categories, translations

#### ADMIN_SERVICE_DB_URL
```bash
ADMIN_SERVICE_DB_URL=postgresql://postgres:postgres123@postgres:5432/admin_service_db
```
**Mô tả**: Connection string cho Admin Service database
**Sử dụng**: Admin users, system settings, audit logs

### Database Pool Configuration

#### DB_POOL_SIZE
```bash
DB_POOL_SIZE=20
```
**Mô tả**: Số lượng connection pool cho database
**Default**: 20
**Range**: 10-50

#### DB_MAX_OVERFLOW
```bash
DB_MAX_OVERFLOW=30
```
**Mô tả**: Số connection tối đa có thể tạo thêm khi pool đầy
**Default**: 30

#### DB_POOL_TIMEOUT
```bash
DB_POOL_TIMEOUT=30
```
**Mô tả**: Timeout (giây) khi chờ connection từ pool
**Default**: 30 seconds

---

## 🔄 Redis Configuration

### Redis Connection URLs

#### User Service Redis (Database 0)
```bash
USER_SERVICE_REDIS_URL=redis://:redis123@redis:6379/0
```
**Mô tả**: Redis database 0 cho User Service caching
**Sử dụng**: Session storage, user profile cache

#### Payment Service Redis (Database 1)
```bash
PAYMENT_SERVICE_REDIS_URL=redis://:redis123@redis:6379/1
```
**Mô tả**: Redis database 1 cho Payment Service caching
**Sử dụng**: Transaction cache, payment method cache

#### Math Solver Service Redis (Database 2)
```bash
MATH_SOLVER_SERVICE_REDIS_URL=redis://:redis123@redis:6379/2
```
**Mô tả**: Redis database 2 cho Math Solver Service caching
**Sử dụng**: Problem cache, solution cache

#### Content Service Redis (Database 3)
```bash
CONTENT_SERVICE_REDIS_URL=redis://:redis123@redis:6379/3
```
**Mô tả**: Redis database 3 cho Content Service caching
**Sử dụng**: Page cache, FAQ cache

#### Admin Service Redis (Database 4)
```bash
ADMIN_SERVICE_REDIS_URL=redis://:redis123@redis:6379/4
```
**Mô tả**: Redis database 4 cho Admin Service và Message Queue
**Sử dụng**: Dashboard cache, system metrics, background jobs

### Redis Configuration

#### REDIS_PASSWORD
```bash
REDIS_PASSWORD=redis123
```
**Mô tả**: Password cho Redis authentication
**Bảo mật**: Thay đổi trong production

#### REDIS_MAX_CONNECTIONS
```bash
REDIS_MAX_CONNECTIONS=100
```
**Mô tả**: Số connection tối đa đến Redis
**Default**: 100

#### REDIS_TIMEOUT
```bash
REDIS_TIMEOUT=5
```
**Mô tả**: Connection timeout (giây)
**Default**: 5 seconds

---

## 🔐 Authentication & Security

### JWT Configuration

#### JWT_SECRET_KEY
```bash
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
```
**Mô tả**: Secret key để sign JWT access tokens
**Yêu cầu**: Minimum 32 characters, random string
**Bảo mật**: ⚠️ PHẢI thay đổi trong production

#### JWT_REFRESH_SECRET_KEY
```bash
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-here-change-in-production
```
**Mô tả**: Secret key để sign JWT refresh tokens
**Yêu cầu**: Khác với JWT_SECRET_KEY
**Bảo mật**: ⚠️ PHẢI thay đổi trong production

#### JWT_ACCESS_TOKEN_EXPIRE_MINUTES
```bash
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```
**Mô tả**: Thời gian hết hạn access token (phút)
**Default**: 60 minutes
**Range**: 15-120 minutes

#### JWT_REFRESH_TOKEN_EXPIRE_DAYS
```bash
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```
**Mô tả**: Thời gian hết hạn refresh token (ngày)
**Default**: 7 days
**Range**: 1-30 days

### Password Security

#### PASSWORD_MIN_LENGTH
```bash
PASSWORD_MIN_LENGTH=8
```
**Mô tả**: Độ dài tối thiểu của password
**Default**: 8 characters

#### PASSWORD_REQUIRE_SPECIAL_CHARS
```bash
PASSWORD_REQUIRE_SPECIAL_CHARS=true
```
**Mô tả**: Yêu cầu ký tự đặc biệt trong password
**Default**: true

#### BCRYPT_ROUNDS
```bash
BCRYPT_ROUNDS=12
```
**Mô tả**: Số rounds cho bcrypt hashing
**Default**: 12
**Range**: 10-15

---

## 💳 Payment Gateway Configuration

### VNPay Configuration

#### VNPAY_TMN_CODE
```bash
VNPAY_TMN_CODE=your-vnpay-tmn-code
```
**Mô tả**: VNPay Terminal Code
**Nguồn**: VNPay merchant dashboard
**Bảo mật**: Sensitive information

#### VNPAY_HASH_SECRET
```bash
VNPAY_HASH_SECRET=your-vnpay-hash-secret
```
**Mô tả**: VNPay Hash Secret Key
**Sử dụng**: Verify payment callbacks
**Bảo mật**: ⚠️ Cực kỳ quan trọng

#### VNPAY_API_URL
```bash
VNPAY_API_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
```
**Mô tả**: VNPay API endpoint
**Development**: sandbox.vnpayment.vn
**Production**: vnpayment.vn

### MoMo Configuration

#### MOMO_PARTNER_CODE
```bash
MOMO_PARTNER_CODE=your-momo-partner-code
```
**Mô tả**: MoMo Partner Code
**Nguồn**: MoMo Business Portal

#### MOMO_ACCESS_KEY
```bash
MOMO_ACCESS_KEY=your-momo-access-key
```
**Mô tả**: MoMo Access Key
**Bảo mật**: Sensitive information

#### MOMO_SECRET_KEY
```bash
MOMO_SECRET_KEY=your-momo-secret-key
```
**Mô tả**: MoMo Secret Key
**Sử dụng**: Sign requests và verify callbacks
**Bảo mật**: ⚠️ Cực kỳ quan trọng

#### MOMO_API_URL
```bash
MOMO_API_URL=https://test-payment.momo.vn/v2/gateway/api/create
```
**Mô tả**: MoMo API endpoint
**Development**: test-payment.momo.vn
**Production**: payment.momo.vn

### ZaloPay Configuration

#### ZALOPAY_APP_ID
```bash
ZALOPAY_APP_ID=your-zalopay-app-id
```
**Mô tả**: ZaloPay Application ID

#### ZALOPAY_KEY1
```bash
ZALOPAY_KEY1=your-zalopay-key1
```
**Mô tả**: ZaloPay Key1 for signing
**Bảo mật**: Sensitive information

#### ZALOPAY_KEY2
```bash
ZALOPAY_KEY2=your-zalopay-key2
```
**Mô tả**: ZaloPay Key2 for callback verification
**Bảo mật**: ⚠️ Cực kỳ quan trọng

#### ZALOPAY_API_URL
```bash
ZALOPAY_API_URL=https://sb-openapi.zalopay.vn/v2/create
```
**Mô tả**: ZaloPay API endpoint
**Development**: sb-openapi.zalopay.vn
**Production**: openapi.zalopay.vn

---

## 📧 Email Configuration

### SMTP Settings

#### SMTP_HOST
```bash
SMTP_HOST=smtp.gmail.com
```
**Mô tả**: SMTP server hostname
**Ví dụ**: smtp.gmail.com, smtp.outlook.com

#### SMTP_PORT
```bash
SMTP_PORT=587
```
**Mô tả**: SMTP server port
**TLS**: 587
**SSL**: 465

#### SMTP_USERNAME
```bash
SMTP_USERNAME=your-email@gmail.com
```
**Mô tả**: SMTP authentication username

#### SMTP_PASSWORD
```bash
SMTP_PASSWORD=your-app-password
```
**Mô tả**: SMTP authentication password
**Gmail**: Sử dụng App Password
**Bảo mật**: Sensitive information

#### SMTP_USE_TLS
```bash
SMTP_USE_TLS=true
```
**Mô tả**: Sử dụng TLS encryption
**Default**: true

### Email Templates

#### FROM_EMAIL
```bash
FROM_EMAIL=noreply@mathservice.com
```
**Mô tả**: Default sender email address

#### FROM_NAME
```bash
FROM_NAME=Math Service
```
**Mô tả**: Default sender name

#### SUPPORT_EMAIL
```bash
SUPPORT_EMAIL=support@mathservice.com
```
**Mô tả**: Support contact email

---

## 🌐 Frontend Configuration

### Next.js Environment Variables

#### NEXT_PUBLIC_API_BASE_URL
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
**Mô tả**: Base URL cho API calls từ frontend
**Development**: http://localhost:8000
**Production**: https://api.mathservice.com

#### NEXT_PUBLIC_USER_SERVICE_URL
```bash
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:8001
```
**Mô tả**: User Service API URL

#### NEXT_PUBLIC_PAYMENT_SERVICE_URL
```bash
NEXT_PUBLIC_PAYMENT_SERVICE_URL=http://localhost:8002
```
**Mô tả**: Payment Service API URL

#### NEXT_PUBLIC_MATH_SOLVER_SERVICE_URL
```bash
NEXT_PUBLIC_MATH_SOLVER_SERVICE_URL=http://localhost:8003
```
**Mô tả**: Math Solver Service API URL

#### NEXT_PUBLIC_CONTENT_SERVICE_URL
```bash
NEXT_PUBLIC_CONTENT_SERVICE_URL=http://localhost:8004
```
**Mô tả**: Content Service API URL

#### NEXT_PUBLIC_ADMIN_SERVICE_URL
```bash
NEXT_PUBLIC_ADMIN_SERVICE_URL=http://localhost:8005
```
**Mô tả**: Admin Service API URL

### Frontend Features

#### NEXT_PUBLIC_ENABLE_ANALYTICS
```bash
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```
**Mô tả**: Bật/tắt Google Analytics
**Development**: false
**Production**: true

#### NEXT_PUBLIC_GOOGLE_ANALYTICS_ID
```bash
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
```
**Mô tả**: Google Analytics Measurement ID
**Format**: G-XXXXXXXXXX

---

## 🔧 System Configuration

### Application Settings

#### APP_NAME
```bash
APP_NAME=Math Service
```
**Mô tả**: Tên ứng dụng hiển thị

#### APP_VERSION
```bash
APP_VERSION=1.0.0
```
**Mô tả**: Phiên bản ứng dụng

#### APP_ENVIRONMENT
```bash
APP_ENVIRONMENT=development
```
**Mô tả**: Môi trường chạy
**Values**: development, staging, production

#### DEBUG
```bash
DEBUG=true
```
**Mô tả**: Bật/tắt debug mode
**Development**: true
**Production**: false

### Logging Configuration

#### LOG_LEVEL
```bash
LOG_LEVEL=INFO
```
**Mô tả**: Mức độ logging
**Values**: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### LOG_FORMAT
```bash
LOG_FORMAT=json
```
**Mô tả**: Format của log output
**Values**: json, text

#### LOG_FILE_PATH
```bash
LOG_FILE_PATH=/app/logs/app.log
```
**Mô tả**: Đường dẫn file log

### Performance Settings

#### WORKER_PROCESSES
```bash
WORKER_PROCESSES=4
```
**Mô tả**: Số worker processes cho Gunicorn
**Calculation**: (CPU cores * 2) + 1

#### MAX_REQUESTS_PER_WORKER
```bash
MAX_REQUESTS_PER_WORKER=1000
```
**Mô tả**: Số request tối đa mỗi worker xử lý trước khi restart

#### REQUEST_TIMEOUT
```bash
REQUEST_TIMEOUT=30
```
**Mô tả**: Timeout cho HTTP requests (giây)

---

## 🧮 Math Solver Configuration

### Solver Settings

#### MAX_CONCURRENT_SOLUTIONS
```bash
MAX_CONCURRENT_SOLUTIONS=100
```
**Mô tả**: Số lượng bài toán có thể giải đồng thời
**Default**: 100

#### SOLUTION_TIMEOUT_SECONDS
```bash
SOLUTION_TIMEOUT_SECONDS=30
```
**Mô tả**: Timeout cho việc giải toán (giây)
**Default**: 30 seconds

#### ENABLE_STEP_BY_STEP
```bash
ENABLE_STEP_BY_STEP=true
```
**Mô tả**: Bật/tắt tính năng giải từng bước
**Default**: true

#### ENABLE_GRAPH_GENERATION
```bash
ENABLE_GRAPH_GENERATION=true
```
**Mô tả**: Bật/tắt tạo đồ thị cho kết quả
**Default**: true

### Pricing Configuration

#### BASE_PRICE_QUADRATIC
```bash
BASE_PRICE_QUADRATIC=5000
```
**Mô tả**: Giá cơ bản cho phương trình bậc 2 (VND)

#### BASE_PRICE_SYSTEM
```bash
BASE_PRICE_SYSTEM=8000
```
**Mô tả**: Giá cơ bản cho hệ phương trình (VND)

#### BASE_PRICE_CALCULUS
```bash
BASE_PRICE_CALCULUS=12000
```
**Mô tả**: Giá cơ bản cho tích phân/đạo hàm (VND)

---

## 🔒 Security Configuration

### Rate Limiting

#### RATE_LIMIT_PER_MINUTE
```bash
RATE_LIMIT_PER_MINUTE=100
```
**Mô tả**: Số request tối đa mỗi phút per user
**Default**: 100

#### RATE_LIMIT_PER_HOUR
```bash
RATE_LIMIT_PER_HOUR=1000
```
**Mô tả**: Số request tối đa mỗi giờ per user
**Default**: 1000

### CORS Configuration

#### CORS_ORIGINS
```bash
CORS_ORIGINS=http://localhost:3000,https://mathservice.com
```
**Mô tả**: Danh sách origins được phép CORS
**Format**: Comma-separated URLs

#### CORS_ALLOW_CREDENTIALS
```bash
CORS_ALLOW_CREDENTIALS=true
```
**Mô tả**: Cho phép gửi credentials trong CORS requests

### Security Headers

#### ENABLE_SECURITY_HEADERS
```bash
ENABLE_SECURITY_HEADERS=true
```
**Mô tả**: Bật/tắt security headers
**Production**: true

#### CONTENT_SECURITY_POLICY
```bash
CONTENT_SECURITY_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline'"
```
**Mô tả**: Content Security Policy header

---

## 📊 Monitoring & Analytics

### Health Check Configuration

#### HEALTH_CHECK_INTERVAL
```bash
HEALTH_CHECK_INTERVAL=30
```
**Mô tả**: Interval kiểm tra health (giây)
**Default**: 30 seconds

#### HEALTH_CHECK_TIMEOUT
```bash
HEALTH_CHECK_TIMEOUT=5
```
**Mô tả**: Timeout cho health check (giây)
**Default**: 5 seconds

### Metrics Configuration

#### ENABLE_METRICS
```bash
ENABLE_METRICS=true
```
**Mô tả**: Bật/tắt metrics collection
**Default**: true

#### METRICS_PORT
```bash
METRICS_PORT=9090
```
**Mô tả**: Port cho Prometheus metrics
**Default**: 9090

---

## 🌍 Environment-Specific Values

### Development Environment
```bash
# Database
DB_POOL_SIZE=5
DEBUG=true
LOG_LEVEL=DEBUG

# Security (relaxed for development)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
CORS_ORIGINS=http://localhost:3000

# External APIs (sandbox)
VNPAY_API_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
MOMO_API_URL=https://test-payment.momo.vn/v2/gateway/api/create
```

### Staging Environment
```bash
# Database
DB_POOL_SIZE=15
DEBUG=false
LOG_LEVEL=INFO

# Security (production-like)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://staging.mathservice.com

# External APIs (sandbox)
VNPAY_API_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
MOMO_API_URL=https://test-payment.momo.vn/v2/gateway/api/create
```

### Production Environment
```bash
# Database
DB_POOL_SIZE=30
DEBUG=false
LOG_LEVEL=WARNING

# Security (strict)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://mathservice.com

# External APIs (production)
VNPAY_API_URL=https://vnpayment.vn/paymentv2/vpcpay.html
MOMO_API_URL=https://payment.momo.vn/v2/gateway/api/create

# Performance
WORKER_PROCESSES=8
MAX_CONCURRENT_SOLUTIONS=200
```

---

## 🔧 Setup Instructions

### 1. Copy Environment Template
```bash
cp .env.example .env.development
```

### 2. Update Required Variables
```bash
# Thay đổi các giá trị sau:
JWT_SECRET_KEY=your-unique-secret-key
JWT_REFRESH_SECRET_KEY=your-unique-refresh-key
VNPAY_TMN_CODE=your-vnpay-code
VNPAY_HASH_SECRET=your-vnpay-secret
```

### 3. Validate Configuration
```bash
# Chạy validation script
python scripts/validate-env.py
```

### 4. Load Environment
```bash
# Docker Compose
docker-compose --env-file .env.development up

# Manual
export $(cat .env.development | xargs)
```

---

## ⚠️ Security Best Practices

### 1. Secret Management
- ✅ Sử dụng strong random strings cho JWT secrets
- ✅ Thay đổi default passwords
- ✅ Không commit secrets vào Git
- ✅ Sử dụng environment-specific secrets

### 2. Database Security
- ✅ Sử dụng strong database passwords
- ✅ Limit database connections
- ✅ Enable SSL/TLS cho production

### 3. API Security
- ✅ Validate tất cả API keys
- ✅ Sử dụng HTTPS cho production
- ✅ Enable rate limiting
- ✅ Configure CORS properly

### 4. Monitoring
- ✅ Enable logging cho tất cả environments
- ✅ Monitor failed authentication attempts
- ✅ Set up alerts cho security events

---

## 📚 References

- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [Redis Configuration](https://redis.io/topics/config)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

---

**Tài liệu này được cập nhật thường xuyên. Phiên bản hiện tại: v1.0.0**
