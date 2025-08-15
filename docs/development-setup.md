# Development Setup Guide

Hướng dẫn chi tiết setup development environment cho Math Service Website.

## 📋 Tổng quan

Dự án sử dụng kiến trúc microservices với 5 FastAPI services và 1 Next.js frontend. Mỗi service có database riêng và Redis cache riêng.

## 🛠️ Yêu cầu hệ thống

### Phần mềm bắt buộc
- **Docker**: 20.10+ và Docker Compose 2.0+
- **Python**: 3.11+
- **Node.js**: 20.18.0+
- **Git**: 2.30+

### Phần mềm khuyến nghị
- **IDE**: VS Code với Python và TypeScript extensions
- **Database Client**: pgAdmin, DBeaver, hoặc TablePlus
- **Redis Client**: RedisInsight hoặc Redis CLI
- **API Testing**: Postman hoặc Insomnia

## 🚀 Setup nhanh (Recommended)

### 1. Clone và setup cơ bản
```bash
# Clone repository
git clone <repository-url>
cd math-service-website

# Copy environment variables
cp .env.example .env.development

# Khởi động toàn bộ hệ thống với Docker
docker-compose up -d

# Chờ services khởi động (30-60 giây)
docker-compose logs -f
```

### 2. Khởi tạo databases
```bash
# Chạy database initialization scripts
docker-compose exec postgres psql -U postgres -c "\i /docker-entrypoint-initdb.d/init-databases.sql"

# Chạy migrations cho từng service
docker-compose exec user-service python -m alembic upgrade head
docker-compose exec payment-service python -m alembic upgrade head
docker-compose exec math-solver-service python -m alembic upgrade head
docker-compose exec content-service python -m alembic upgrade head
docker-compose exec admin-service python -m alembic upgrade head
```

### 3. Verify setup
```bash
# Kiểm tra tất cả services đang chạy
docker-compose ps

# Test API endpoints
curl http://localhost:8001/health  # User Service
curl http://localhost:8002/health  # Payment Service
curl http://localhost:8003/health  # Math Solver Service
curl http://localhost:8004/health  # Content Service
curl http://localhost:8005/health  # Admin Service

# Test frontend
curl http://localhost:3000
```

## 🔧 Setup chi tiết từng service

### User Service (Port 8001)

#### Chức năng
- User registration và authentication
- JWT token management
- User profile management
- Role-based access control

#### Database Schema
- **users**: Thông tin người dùng
- **user_roles**: Phân quyền
- **user_sessions**: JWT sessions
- **user_balance**: Số dư tài khoản

#### Environment Variables
```bash
DATABASE_URL_USER_SERVICE=postgresql://postgres:postgres123@postgres:5432/user_service_db
REDIS_URL_USER_SERVICE=redis://:redis123@redis:6379/0
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### Development Setup
```bash
# Chạy riêng User Service
cd services/user-service

# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy development server
uvicorn app.main:app --reload --port 8001

# Chạy tests
pytest tests/ -v

# Chạy migrations
alembic upgrade head
```

#### API Endpoints chính
- `POST /api/v1/auth/register` - Đăng ký user
- `POST /api/v1/auth/login` - Đăng nhập
- `GET /api/v1/users/profile` - Lấy profile
- `PUT /api/v1/users/profile` - Cập nhật profile

### Payment Service (Port 8002)

#### Chức năng
- Payment gateway integration (VNPay, MoMo, ZaloPay)
- Transaction management
- Balance management
- Payment history

#### Database Schema
- **transactions**: Giao dịch thanh toán
- **payment_methods**: Phương thức thanh toán
- **transaction_logs**: Audit logs
- **balances**: Lịch sử số dư

#### Environment Variables
```bash
DATABASE_URL_PAYMENT_SERVICE=postgresql://postgres:postgres123@postgres:5432/payment_service_db
REDIS_URL_PAYMENT_SERVICE=redis://:redis123@redis:6379/1
VNPAY_TMN_CODE=your-vnpay-tmn-code
VNPAY_SECRET_KEY=your-vnpay-secret-key
MOMO_PARTNER_CODE=your-momo-partner-code
ZALOPAY_APP_ID=your-zalopay-app-id
```

#### Development Setup
```bash
cd services/payment-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

#### API Endpoints chính
- `POST /api/v1/payments/deposit` - Nạp tiền
- `POST /api/v1/payments/withdraw` - Rút tiền
- `GET /api/v1/payments/history` - Lịch sử giao dịch
- `POST /api/v1/payments/callback` - Webhook từ payment gateway

### Math Solver Service (Port 8003)

#### Chức năng
- Giải các bài toán: phương trình bậc 2, hệ phương trình, tích phân
- Lưu trữ lịch sử giải toán
- Pricing và billing cho từng loại toán
- Statistics và analytics

#### Database Schema
- **math_problems**: Catalog các loại toán
- **solutions**: Kết quả giải toán
- **solution_history**: Lịch sử truy cập
- **problem_statistics**: Thống kê usage

#### Environment Variables
```bash
DATABASE_URL_MATH_SOLVER_SERVICE=postgresql://postgres:postgres123@postgres:5432/math_solver_db
REDIS_URL_MATH_SOLVER_SERVICE=redis://:redis123@redis:6379/2
MATH_SOLVER_API_KEY=your-math-api-key
WOLFRAM_ALPHA_API_KEY=your-wolfram-api-key
```

#### Development Setup
```bash
cd services/math-solver-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install sympy numpy scipy  # Math libraries
uvicorn app.main:app --reload --port 8003
```

#### API Endpoints chính
- `POST /api/v1/solve/quadratic` - Giải phương trình bậc 2
- `POST /api/v1/solve/system` - Giải hệ phương trình
- `GET /api/v1/solutions/history` - Lịch sử giải toán
- `GET /api/v1/problems/pricing` - Bảng giá

### Content Service (Port 8004)

#### Chức năng
- Content Management System (CMS)
- FAQ management
- Multi-language support
- SEO optimization

#### Database Schema
- **pages**: Trang web content
- **faqs**: Câu hỏi thường gặp
- **content_categories**: Phân loại content
- **translations**: Đa ngôn ngữ

#### Environment Variables
```bash
DATABASE_URL_CONTENT_SERVICE=postgresql://postgres:postgres123@postgres:5432/content_service_db
REDIS_URL_CONTENT_SERVICE=redis://:redis123@redis:6379/3
CONTENT_CACHE_TTL=3600
DEFAULT_LANGUAGE=vi
SUPPORTED_LANGUAGES=vi,en
```

#### Development Setup
```bash
cd services/content-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

#### API Endpoints chính
- `GET /api/v1/pages/{slug}` - Lấy content page
- `GET /api/v1/faqs` - Danh sách FAQ
- `POST /api/v1/pages` - Tạo page mới (admin)
- `PUT /api/v1/pages/{id}` - Cập nhật page

### Admin Service (Port 8005)

#### Chức năng
- Admin dashboard
- System monitoring
- User management
- Audit logs

#### Database Schema
- **admin_users**: Admin accounts
- **system_settings**: Cấu hình hệ thống
- **audit_logs**: Logs hoạt động

#### Environment Variables
```bash
DATABASE_URL_ADMIN_SERVICE=postgresql://postgres:postgres123@postgres:5432/admin_service_db
REDIS_URL_ADMIN_SERVICE=redis://:redis123@redis:6379/4
ADMIN_SECRET_KEY=your-admin-secret-key
ENABLE_AUDIT_LOGGING=true
```

#### Development Setup
```bash
cd services/admin-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

#### API Endpoints chính
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/users` - Quản lý users
- `GET /api/v1/audit-logs` - Audit logs
- `PUT /api/v1/settings` - Cập nhật system settings

### Frontend (Port 3000)

#### Công nghệ
- Next.js 14 với App Router
- React 18 với TypeScript
- Tailwind CSS cho styling
- Axios cho API calls

#### Environment Variables
```bash
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_PAYMENT_SERVICE_URL=http://localhost:8002
NEXT_PUBLIC_MATH_SOLVER_SERVICE_URL=http://localhost:8003
NEXT_PUBLIC_CONTENT_SERVICE_URL=http://localhost:8004
NEXT_PUBLIC_ADMIN_SERVICE_URL=http://localhost:8005
```

#### Development Setup
```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev

# Build production
npm run build

# Chạy tests
npm test
```

## 🗄️ Database Setup

### PostgreSQL Configuration
```bash
# Kết nối đến PostgreSQL
docker-compose exec postgres psql -U postgres

# Liệt kê databases
\l

# Kết nối đến database cụ thể
\c user_service_db

# Liệt kê tables
\dt

# Xem schema của table
\d users
```

### Redis Configuration
```bash
# Kết nối đến Redis
docker-compose exec redis redis-cli -a redis123

# Chọn database
SELECT 0  # User Service cache
SELECT 1  # Payment Service cache
SELECT 2  # Math Solver cache
SELECT 3  # Content Service cache
SELECT 4  # Admin Service cache

# Xem keys
KEYS *

# Xem giá trị
GET key_name
```

## 🧪 Testing Setup

### Unit Tests
```bash
# Chạy tests cho tất cả services
pytest

# Tests cho service cụ thể
pytest services/user-service/tests/

# Tests với coverage
pytest --cov=services --cov-report=html

# Chỉ unit tests
pytest -m unit

# Chỉ integration tests
pytest -m integration
```

### API Testing
```bash
# Sử dụng curl
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Sử dụng httpie (cài đặt: pip install httpie)
http POST localhost:8001/api/v1/auth/register email=test@example.com password=password123
```

## 🔧 Code Quality Setup

### Pre-commit Hooks
```bash
# Cài đặt pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Chạy tất cả hooks
pre-commit run --all-files

# Chạy hook cụ thể
pre-commit run black
pre-commit run flake8
```

### Manual Quality Checks
```bash
# Format code
black .
isort .

# Linting
flake8 .

# Type checking
mypy services/

# Security scanning
bandit -r services/
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port conflicts
```bash
# Kiểm tra ports đang sử dụng
netstat -tulpn | grep :8001

# Kill process sử dụng port
sudo kill -9 $(lsof -t -i:8001)
```

#### 2. Database connection errors
```bash
# Kiểm tra PostgreSQL đang chạy
docker-compose ps postgres

# Xem logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### 3. Redis connection errors
```bash
# Kiểm tra Redis
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli -a redis123 ping
```

#### 4. Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose up --build -d

# Clean up
docker system prune -a
docker volume prune
```

### Performance Monitoring
```bash
# Xem resource usage
docker stats

# Xem logs real-time
docker-compose logs -f user-service

# Database performance
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

## 📞 Support

Nếu gặp vấn đề trong quá trình setup:

1. Kiểm tra [Troubleshooting](#-troubleshooting) section
2. Xem logs: `docker-compose logs <service-name>`
3. Liên hệ team qua Slack: #math-service-dev
4. Tạo issue trên GitHub repository

---

**Happy Development! 🚀**
