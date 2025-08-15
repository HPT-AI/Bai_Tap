# Math Service Website

Website dịch vụ toán học với kiến trúc microservices, cung cấp các công cụ giải toán trực tuyến và quản lý thanh toán.

## 📋 Tổng quan dự án

### Kiến trúc hệ thống
- **5 FastAPI Microservices**: User, Payment, Math Solver, Content, Admin
- **1 Next.js Frontend**: Giao diện người dùng responsive
- **PostgreSQL**: 5 databases riêng biệt cho từng service
- **Redis**: Caching và message queue với 5 database instances
- **Docker**: Containerization cho toàn bộ hệ thống

### Công nghệ sử dụng
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 15, Redis 7
- **DevOps**: Docker, Docker Compose
- **Code Quality**: Black, Flake8, MyPy, Isort, Pytest, Pre-commit

## 🚀 Quick Start

### Yêu cầu hệ thống
- Docker và Docker Compose
- Python 3.11+
- Node.js 20+
- Git

### Cài đặt nhanh
```bash
# Clone repository
git clone <repository-url>
cd math-service-website

# Copy environment variables
cp .env.example .env.development

# Khởi động toàn bộ hệ thống
docker-compose up -d

# Khởi tạo databases
docker-compose exec postgres psql -U postgres -f /docker-entrypoint-initdb.d/init-databases.sql
```

### Truy cập ứng dụng
- **Frontend**: http://localhost:3000
- **User Service**: http://localhost:8001
- **Payment Service**: http://localhost:8002
- **Math Solver Service**: http://localhost:8003
- **Content Service**: http://localhost:8004
- **Admin Service**: http://localhost:8005
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🏗️ Cấu trúc dự án

```
math-service-website/
├── services/                    # Microservices
│   ├── user-service/           # User management & authentication
│   ├── payment-service/        # Payment processing & billing
│   ├── math-solver-service/    # Math problem solving
│   ├── content-service/        # CMS & content management
│   └── admin-service/          # Admin panel & system management
├── frontend/                   # Next.js application
├── scripts/                    # Database initialization scripts
│   ├── init-databases.sql     # Create all databases
│   ├── user-service/          # User service schemas
│   ├── payment-service/       # Payment service schemas
│   ├── math-solver-service/   # Math solver schemas
│   ├── content-service/       # Content service schemas
│   └── admin-service/         # Admin service schemas
├── docs/                      # Documentation
├── k8s/                       # Kubernetes deployment files
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Development environment
├── .env.development          # Development environment variables
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🛠️ Development Setup

### 1. Environment Setup
```bash
# Tạo Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt pre-commit hooks
pre-commit install
```

### 2. Database Setup
```bash
# Khởi động PostgreSQL và Redis
docker-compose up -d postgres redis

# Chạy database migrations
python scripts/run_migrations.py
```

### 3. Development Workflow
```bash
# Khởi động từng service riêng biệt
cd services/user-service
uvicorn app.main:app --reload --port 8001

# Hoặc khởi động tất cả với Docker
docker-compose up --build
```

## 🧪 Testing

### Chạy tests
```bash
# Tất cả tests
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

### Code Quality
```bash
# Format code
black .
isort .

# Linting
flake8 .

# Type checking
mypy services/

# Chạy tất cả quality checks
pre-commit run --all-files
```

## 📚 Documentation

- [Development Setup](docs/development-setup.md) - Chi tiết setup từng service
- [Database Schema](docs/database-schema.md) - ERD và schema documentation
- [API Endpoints](docs/api-endpoints.md) - API documentation cho tất cả services
- [Environment Variables](docs/environment-variables.md) - Hướng dẫn cấu hình

## 🔧 Configuration

### Environment Variables
Xem file `.env.example` để biết tất cả biến môi trường cần thiết.

Các biến quan trọng:
- `DATABASE_URL_*`: Connection strings cho từng service
- `REDIS_URL_*`: Redis connections cho từng service
- `JWT_SECRET_KEY`: Secret key cho JWT authentication
- `*_API_KEY`: API keys cho các dịch vụ bên ngoài

### Docker Configuration
- `docker-compose.yml`: Development environment
- `docker-compose.prod.yml`: Production environment
- `docker-compose.override.yml`: Local overrides (git ignored)

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 🤝 Contributing

### Quy trình phát triển
1. Tạo branch từ `develop`
2. Implement feature/bugfix
3. Chạy tests và quality checks
4. Tạo Pull Request
5. Code review
6. Merge sau khi approve

### Commit Convention
```
feat: add new math solver algorithm
fix: resolve payment gateway timeout
docs: update API documentation
test: add unit tests for user service
refactor: optimize database queries
```

### Pre-commit Hooks
Tự động chạy khi commit:
- Black formatting
- Isort import sorting
- Flake8 linting
- MyPy type checking
- Pytest unit tests

## 📞 Support

### Team Contacts
- **Tech Lead**: tech-lead@mathservice.com
- **DevOps**: devops@mathservice.com
- **Support**: support@mathservice.com

### Development Resources
- **Slack**: #math-service-dev
- **Jira**: [Project Board](https://mathservice.atlassian.net)
- **Confluence**: [Technical Docs](https://mathservice.atlassian.net/wiki)

## 📄 License

Copyright © 2024 Math Service Team. All rights reserved.

---

**Happy Coding! 🎉**
