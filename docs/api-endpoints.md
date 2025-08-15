# API Endpoints Documentation

Tài liệu chi tiết về tất cả API endpoints cho Math Service Website với 5 microservices.

## 📋 Tổng quan API Architecture

### Service URLs
- **User Service**: http://localhost:8001
- **Payment Service**: http://localhost:8002
- **Math Solver Service**: http://localhost:8003
- **Content Service**: http://localhost:8004
- **Admin Service**: http://localhost:8005

### API Standards
- **Version**: All APIs use `/api/v1/` prefix
- **Format**: JSON request/response
- **Authentication**: JWT Bearer tokens
- **Rate Limiting**: 100 requests/minute per user
- **CORS**: Enabled for frontend domains

### Common Response Format
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2024-08-14T10:30:00Z",
  "request_id": "uuid-string"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  },
  "timestamp": "2024-08-14T10:30:00Z",
  "request_id": "uuid-string"
}
```

## 👤 User Service API (Port 8001)

### Authentication Endpoints

#### POST /api/v1/auth/register
**Purpose**: Đăng ký tài khoản mới
**Authentication**: None required
**Rate Limit**: 5 requests/minute

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Nguyen Van A",
  "phone": "0901234567"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-string",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "is_verified": false,
    "created_at": "2024-08-14T10:30:00Z"
  },
  "message": "User registered successfully. Please check email for verification."
}
```

#### POST /api/v1/auth/login
**Purpose**: Đăng nhập và lấy JWT tokens
**Authentication**: None required
**Rate Limit**: 10 requests/minute

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "full_name": "Nguyen Van A",
      "role": "user"
    }
  }
}
```

#### POST /api/v1/auth/refresh
**Purpose**: Refresh JWT access token
**Authentication**: Refresh token required

**Request Body**:
```json
{
  "refresh_token": "jwt-refresh-token"
}
```

#### POST /api/v1/auth/logout
**Purpose**: Đăng xuất và invalidate tokens
**Authentication**: Bearer token required

### User Profile Endpoints

#### GET /api/v1/users/profile
**Purpose**: Lấy thông tin profile người dùng
**Authentication**: Bearer token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "phone": "0901234567",
    "role": "user",
    "is_verified": true,
    "balance": {
      "current_balance": 150000.00,
      "total_deposited": 200000.00,
      "total_spent": 50000.00
    },
    "created_at": "2024-08-14T10:30:00Z",
    "last_login": "2024-08-14T15:45:00Z"
  }
}
```

#### PUT /api/v1/users/profile
**Purpose**: Cập nhật thông tin profile
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "full_name": "Nguyen Van B",
  "phone": "0907654321"
}
```

#### POST /api/v1/users/change-password
**Purpose**: Đổi mật khẩu
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

### Health Check

#### GET /api/v1/health
**Purpose**: Health check endpoint
**Authentication**: None required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "service": "user-service",
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected",
    "redis": "connected"
  }
}
```

## 💳 Payment Service API (Port 8002)

### Payment Endpoints

#### POST /api/v1/payments/deposit
**Purpose**: Tạo yêu cầu nạp tiền
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "amount": 100000,
  "payment_method": "vnpay",
  "return_url": "http://localhost:3000/payment/success",
  "cancel_url": "http://localhost:3000/payment/cancel"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "uuid-string",
    "reference_code": "TXN_20240814_A1B2C3D4",
    "amount": 100000,
    "fee_amount": 2000,
    "net_amount": 98000,
    "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?...",
    "expires_at": "2024-08-14T11:00:00Z"
  }
}
```

#### POST /api/v1/payments/withdraw
**Purpose**: Tạo yêu cầu rút tiền
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "amount": 50000,
  "bank_account": {
    "bank_code": "VCB",
    "account_number": "1234567890",
    "account_name": "NGUYEN VAN A"
  }
}
```

#### GET /api/v1/payments/history
**Purpose**: Lấy lịch sử giao dịch
**Authentication**: Bearer token required

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `type`: Transaction type (deposit, withdrawal, service_payment)
- `status`: Transaction status (pending, completed, failed)
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "uuid-string",
        "type": "deposit",
        "amount": 100000,
        "fee_amount": 2000,
        "net_amount": 98000,
        "status": "completed",
        "reference_code": "TXN_20240814_A1B2C3D4",
        "payment_method": "vnpay",
        "created_at": "2024-08-14T10:30:00Z",
        "updated_at": "2024-08-14T10:35:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

#### GET /api/v1/payments/methods
**Purpose**: Lấy danh sách phương thức thanh toán
**Authentication**: Bearer token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "method_type": "vnpay",
      "method_name": "VNPay",
      "fee_percentage": 2.0,
      "min_amount": 10000,
      "max_amount": 50000000,
      "is_active": true
    },
    {
      "id": "uuid-string",
      "method_type": "momo",
      "method_name": "MoMo",
      "fee_percentage": 1.5,
      "min_amount": 10000,
      "max_amount": 20000000,
      "is_active": true
    }
  ]
}
```

### Webhook Endpoints

#### POST /api/v1/payments/webhook/vnpay
**Purpose**: Webhook từ VNPay
**Authentication**: VNPay signature verification

#### POST /api/v1/payments/webhook/momo
**Purpose**: Webhook từ MoMo
**Authentication**: MoMo signature verification

## 🧮 Math Solver Service API (Port 8003)

### Problem Solving Endpoints

#### POST /api/v1/solve/quadratic
**Purpose**: Giải phương trình bậc 2
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "coefficients": {
    "a": 1,
    "b": -5,
    "c": 6
  },
  "show_steps": true
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "solution_id": "uuid-string",
    "problem_type": "quadratic_equation",
    "input": {
      "equation": "x² - 5x + 6 = 0",
      "coefficients": {"a": 1, "b": -5, "c": 6}
    },
    "solution": {
      "roots": [2, 3],
      "discriminant": 1,
      "vertex": {"x": 2.5, "y": -0.25},
      "steps": [
        "Phương trình: x² - 5x + 6 = 0",
        "Tính discriminant: Δ = b² - 4ac = 25 - 24 = 1",
        "Δ > 0, phương trình có 2 nghiệm phân biệt",
        "x₁ = (5 + 1) / 2 = 3",
        "x₂ = (5 - 1) / 2 = 2"
      ]
    },
    "cost_paid": 5000,
    "processing_time_ms": 125,
    "created_at": "2024-08-14T10:30:00Z"
  }
}
```

#### POST /api/v1/solve/system
**Purpose**: Giải hệ phương trình
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "equations": [
    {"coefficients": [2, 3], "constant": 7},
    {"coefficients": [1, -1], "constant": 1}
  ],
  "variables": ["x", "y"],
  "method": "elimination"
}
```

#### POST /api/v1/solve/calculus
**Purpose**: Giải tích phân, đạo hàm
**Authentication**: Bearer token required

**Request Body**:
```json
{
  "expression": "x^2 + 2*x + 1",
  "operation": "integrate",
  "variable": "x",
  "limits": {"lower": 0, "upper": 2}
}
```

### Solution Management

#### GET /api/v1/solutions/history
**Purpose**: Lấy lịch sử giải toán
**Authentication**: Bearer token required

**Query Parameters**:
- `page`: Page number
- `limit`: Items per page
- `problem_type`: Filter by problem type
- `status`: Filter by solution status

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "solutions": [
      {
        "id": "uuid-string",
        "problem_type": "quadratic_equation",
        "status": "completed",
        "cost_paid": 5000,
        "created_at": "2024-08-14T10:30:00Z",
        "preview": "x² - 5x + 6 = 0 → x = 2, 3"
      }
    ],
    "pagination": {...}
  }
}
```

#### GET /api/v1/solutions/{solution_id}
**Purpose**: Xem chi tiết solution
**Authentication**: Bearer token required

#### DELETE /api/v1/solutions/{solution_id}
**Purpose**: Xóa solution
**Authentication**: Bearer token required

### Problem Catalog

#### GET /api/v1/problems
**Purpose**: Lấy danh sách loại bài toán
**Authentication**: Bearer token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "problem_type": "quadratic_equation",
      "problem_name": "Phương trình bậc 2",
      "description": "Giải phương trình dạng ax² + bx + c = 0",
      "base_price": 5000,
      "difficulty_level": "easy",
      "input_schema": {...},
      "output_schema": {...}
    }
  ]
}
```

#### GET /api/v1/problems/pricing
**Purpose**: Bảng giá các loại toán
**Authentication**: Bearer token required

## 📝 Content Service API (Port 8004)

### Content Pages

#### GET /api/v1/pages
**Purpose**: Lấy danh sách pages
**Authentication**: None required

**Query Parameters**:
- `category`: Filter by category slug
- `status`: published, draft (admin only)
- `search`: Search in title and content
- `page`, `limit`: Pagination

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "id": "uuid-string",
        "title": "Hướng dẫn giải phương trình bậc 2",
        "slug": "huong-dan-giai-phuong-trinh-bac-2",
        "excerpt": "Tìm hiểu cách giải phương trình bậc 2 một cách dễ hiểu...",
        "category": {
          "name": "Hướng dẫn",
          "slug": "huong-dan"
        },
        "featured_image_url": "https://example.com/image.jpg",
        "view_count": 1250,
        "published_at": "2024-08-14T10:30:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

#### GET /api/v1/pages/{slug}
**Purpose**: Lấy chi tiết page theo slug
**Authentication**: None required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Hướng dẫn giải phương trình bậc 2",
    "slug": "huong-dan-giai-phuong-trinh-bac-2",
    "content": "<h1>Phương trình bậc 2</h1><p>Phương trình bậc 2...</p>",
    "meta_title": "Hướng dẫn giải phương trình bậc 2 | Math Service",
    "meta_description": "Tìm hiểu cách giải phương trình bậc 2...",
    "category": {...},
    "view_count": 1251,
    "published_at": "2024-08-14T10:30:00Z",
    "updated_at": "2024-08-14T15:20:00Z"
  }
}
```

### FAQ Management

#### GET /api/v1/faqs
**Purpose**: Lấy danh sách FAQ
**Authentication**: None required

**Query Parameters**:
- `category`: Filter by category
- `featured`: true/false
- `search`: Search in question and answer

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "question": "Làm thế nào để nạp tiền vào tài khoản?",
      "answer": "Bạn có thể nạp tiền thông qua VNPay, MoMo hoặc ZaloPay...",
      "category": {
        "name": "Thanh toán",
        "slug": "thanh-toan"
      },
      "is_featured": true,
      "view_count": 890,
      "tags": ["payment", "deposit"]
    }
  ]
}
```

### Categories

#### GET /api/v1/categories
**Purpose**: Lấy danh sách categories
**Authentication**: None required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "category_name": "Hướng dẫn",
      "category_slug": "huong-dan",
      "description": "Các bài hướng dẫn sử dụng dịch vụ",
      "parent_id": null,
      "children": [
        {
          "id": "uuid-string",
          "category_name": "Toán cơ bản",
          "category_slug": "toan-co-ban"
        }
      ]
    }
  ]
}
```

### Admin Content Management (Requires admin role)

#### POST /api/v1/pages
**Purpose**: Tạo page mới
**Authentication**: Admin Bearer token required

#### PUT /api/v1/pages/{id}
**Purpose**: Cập nhật page
**Authentication**: Admin Bearer token required

#### DELETE /api/v1/pages/{id}
**Purpose**: Xóa page
**Authentication**: Admin Bearer token required

## 🔧 Admin Service API (Port 8005)

### Dashboard

#### GET /api/v1/dashboard/stats
**Purpose**: Lấy thống kê dashboard
**Authentication**: Admin Bearer token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 1250,
      "new_today": 15,
      "active_today": 89
    },
    "transactions": {
      "total_today": 45,
      "revenue_today": 2500000,
      "pending_count": 3
    },
    "solutions": {
      "solved_today": 128,
      "success_rate": 95.5,
      "avg_processing_time": 1250
    },
    "system": {
      "uptime": "5 days, 12 hours",
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 23.1
    }
  }
}
```

### User Management

#### GET /api/v1/users
**Purpose**: Lấy danh sách users
**Authentication**: Admin Bearer token required

**Query Parameters**:
- `page`, `limit`: Pagination
- `search`: Search by email, name
- `role`: Filter by role
- `status`: active, inactive
- `sort`: created_at, last_login

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "uuid-string",
        "email": "user@example.com",
        "full_name": "Nguyen Van A",
        "role": "user",
        "is_active": true,
        "is_verified": true,
        "balance": 150000,
        "total_spent": 50000,
        "last_login": "2024-08-14T15:45:00Z",
        "created_at": "2024-08-14T10:30:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

#### PUT /api/v1/users/{user_id}/status
**Purpose**: Cập nhật trạng thái user
**Authentication**: Admin Bearer token required

**Request Body**:
```json
{
  "is_active": false,
  "reason": "Violation of terms of service"
}
```

### System Settings

#### GET /api/v1/settings
**Purpose**: Lấy system settings
**Authentication**: Admin Bearer token required

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "general": {
      "site_name": "Math Service",
      "site_description": "Website dịch vụ toán học",
      "maintenance_mode": false
    },
    "payment": {
      "min_deposit": 10000,
      "max_deposit": 50000000,
      "vnpay_enabled": true,
      "momo_enabled": true
    },
    "email": {
      "smtp_host": "smtp.gmail.com",
      "from_address": "noreply@mathservice.com"
    }
  }
}
```

#### PUT /api/v1/settings
**Purpose**: Cập nhật system settings
**Authentication**: Super admin Bearer token required

### Audit Logs

#### GET /api/v1/audit-logs
**Purpose**: Lấy audit logs
**Authentication**: Admin Bearer token required

**Query Parameters**:
- `page`, `limit`: Pagination
- `action`: create, update, delete, login
- `entity_type`: user, transaction, solution
- `user_id`: Filter by user
- `from_date`, `to_date`: Date range

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "uuid-string",
        "user_id": "uuid-string",
        "action": "update",
        "entity_type": "user",
        "entity_id": "uuid-string",
        "old_values": {"is_active": true},
        "new_values": {"is_active": false},
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-08-14T10:30:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

## 🔒 Authentication & Authorization

### JWT Token Structure
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "user",
  "permissions": ["read:profile", "write:profile"],
  "iat": 1692014400,
  "exp": 1692018000
}
```

### Permission Levels
- **user**: Basic user permissions
- **premium_user**: Enhanced features access
- **admin**: Admin panel access
- **super_admin**: Full system access

### Rate Limiting
- **General**: 100 requests/minute per user
- **Auth endpoints**: 10 requests/minute
- **Registration**: 5 requests/minute
- **Admin endpoints**: 200 requests/minute

## 📊 Error Codes

### Common Error Codes
- `VALIDATION_ERROR`: Invalid input data
- `AUTHENTICATION_REQUIRED`: Missing or invalid token
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_SERVER_ERROR`: Server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

### Payment Specific Errors
- `INSUFFICIENT_BALANCE`: Not enough balance
- `PAYMENT_GATEWAY_ERROR`: External payment error
- `TRANSACTION_EXPIRED`: Payment session expired
- `INVALID_PAYMENT_METHOD`: Unsupported payment method

### Math Solver Specific Errors
- `INVALID_EQUATION`: Malformed equation input
- `UNSUPPORTED_PROBLEM_TYPE`: Problem type not supported
- `PROCESSING_TIMEOUT`: Solution took too long
- `CALCULATION_ERROR`: Error in mathematical computation

## 🧪 Testing APIs

### Using cURL
```bash
# Register user
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Password123!", "full_name": "Test User"}'

# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Password123!"}'

# Get profile (with token)
curl -X GET http://localhost:8001/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using HTTPie
```bash
# Register user
http POST localhost:8001/api/v1/auth/register email=test@example.com password=Password123! full_name="Test User"

# Login
http POST localhost:8001/api/v1/auth/login email=test@example.com password=Password123!

# Get profile
http GET localhost:8001/api/v1/users/profile Authorization:"Bearer YOUR_JWT_TOKEN"
```

### Postman Collection
Import the Postman collection available at `/docs/postman/Math-Service-APIs.json` for complete API testing.

---

**API Documentation Version: 1.0.0**
**Last Updated: 2024-08-14**
