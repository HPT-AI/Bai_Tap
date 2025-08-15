# Database Schema Documentation

Tài liệu chi tiết về database schema cho Math Service Website với 5 databases riêng biệt cho từng microservice.

## 📋 Tổng quan Database Architecture

### Database Distribution
- **user_service_db**: User management và authentication
- **payment_service_db**: Payment processing và billing
- **math_solver_db**: Math problem solving và history
- **content_service_db**: Content management và CMS
- **admin_service_db**: Admin panel và system management

### Database Technology
- **RDBMS**: PostgreSQL 15
- **Connection Pooling**: SQLAlchemy với async support
- **Migrations**: Alembic
- **Backup Strategy**: Daily automated backups
- **Monitoring**: pg_stat_statements enabled

## 🗄️ User Service Database (user_service_db)

### Entity Relationship Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ user_roles  │    │    users    │    │user_balance │
│─────────────│    │─────────────│    │─────────────│
│ id (PK)     │◄──┐│ id (PK)     │───►│ user_id(FK) │
│ role_name   │   └│ role_id(FK) │    │ current_bal │
│ permissions │    │ email       │    │ total_dep   │
│ created_at  │    │ password_h  │    │ total_spent │
│ updated_at  │    │ full_name   │    │ created_at  │
└─────────────┘    │ phone       │    │ updated_at  │
                   │ is_active   │    └─────────────┘
                   │ created_at  │           │
                   │ updated_at  │           │
                   └─────────────┘           │
                          │                  │
                          ▼                  │
                   ┌─────────────┐           │
                   │user_sessions│           │
                   │─────────────│           │
                   │ id (PK)     │           │
                   │ user_id(FK) │───────────┘
                   │ session_tok │
                   │ refresh_tok │
                   │ device_info │
                   │ ip_address  │
                   │ expires_at  │
                   │ created_at  │
                   └─────────────┘
```

### Tables Detail

#### user_roles
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '{}',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Quản lý phân quyền hệ thống
**Data**: admin, user, premium_user với permissions khác nhau

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role_id UUID REFERENCES user_roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Lưu trữ thông tin người dùng
**Indexes**: email, phone, role_id, is_active

#### user_sessions
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Quản lý JWT sessions và device tracking
**TTL**: Auto cleanup expired sessions

#### user_balance
```sql
CREATE TABLE user_balance (
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_balance DECIMAL(15,2) DEFAULT 0.00,
    total_deposited DECIMAL(15,2) DEFAULT 0.00,
    total_spent DECIMAL(15,2) DEFAULT 0.00,
    last_transaction_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Theo dõi số dư và lịch sử tài chính user

## 💳 Payment Service Database (payment_service_db)

### Entity Relationship Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ payment_methods │    │  transactions   │    │transaction_logs │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (PK)         │◄──┐│ id (PK)         │───►│ id (PK)         │
│ method_type     │   └│ payment_method  │    │ transaction_id  │
│ method_name     │    │ user_id         │    │ old_status      │
│ config          │    │ amount          │    │ new_status      │
│ fee_percentage  │    │ status          │    │ reason          │
│ min_amount      │    │ reference_code  │    │ changed_by      │
│ max_amount      │    │ external_tx_id  │    │ changed_at      │
│ is_active       │    │ created_at      │    └─────────────────┘
└─────────────────┘    │ updated_at      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │    balances     │
                       │─────────────────│
                       │ id (PK)         │
                       │ user_id         │
                       │ transaction_id  │
                       │ balance_before  │
                       │ balance_after   │
                       │ change_amount   │
                       │ created_at      │
                       └─────────────────┘
```

### Tables Detail

#### payment_methods
```sql
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_type payment_method_type NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    config JSONB DEFAULT '{}',
    fee_percentage DECIMAL(5,4) DEFAULT 0.0000,
    min_amount DECIMAL(15,2) DEFAULT 10000.00,
    max_amount DECIMAL(15,2) DEFAULT 50000000.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Cấu hình các phương thức thanh toán
**Data**: VNPay, MoMo, ZaloPay, Bank Transfer, QR Code

#### transactions
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    transaction_type transaction_type NOT NULL,
    payment_method_id UUID REFERENCES payment_methods(id),
    amount DECIMAL(15,2) NOT NULL,
    fee_amount DECIMAL(15,2) DEFAULT 0.00,
    net_amount DECIMAL(15,2) NOT NULL,
    status transaction_status DEFAULT 'pending',
    reference_code VARCHAR(100) UNIQUE,
    external_transaction_id VARCHAR(255),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Lưu trữ tất cả giao dịch thanh toán
**Indexes**: user_id, status, reference_code, created_at

#### transaction_logs
```sql
CREATE TABLE transaction_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    old_status transaction_status,
    new_status transaction_status NOT NULL,
    reason TEXT,
    changed_by VARCHAR(100),
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Audit trail cho mọi thay đổi transaction status

#### balances
```sql
CREATE TABLE balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    transaction_id UUID REFERENCES transactions(id),
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    change_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Snapshot số dư cho reconciliation và audit

## 🧮 Math Solver Database (math_solver_db)

### Entity Relationship Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  math_problems  │    │   solutions     │    │solution_history │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (PK)         │◄──┐│ id (PK)         │───►│ id (PK)         │
│ problem_type    │   └│ problem_id (FK) │    │ solution_id(FK) │
│ problem_name    │    │ user_id         │    │ user_id         │
│ input_schema    │    │ input_data      │    │ access_type     │
│ output_schema   │    │ solution_data   │    │ accessed_at     │
│ base_price      │    │ status          │    └─────────────────┘
│ difficulty      │    │ cost_paid       │
│ is_active       │    │ processing_time │
└─────────────────┘    │ created_at      │
                       │ updated_at      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │problem_statistics│
                       │─────────────────│
                       │ id (PK)         │
                       │ problem_id (FK) │
                       │ date            │
                       │ total_requests  │
                       │ successful_sols │
                       │ failed_solutions│
                       │ total_revenue   │
                       │ avg_proc_time   │
                       └─────────────────┘
```

### Tables Detail

#### math_problems
```sql
CREATE TABLE math_problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_type problem_type NOT NULL,
    problem_name VARCHAR(255) NOT NULL,
    description TEXT,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    difficulty_level difficulty_level DEFAULT 'medium',
    processing_timeout_seconds INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Catalog các loại bài toán có thể giải
**Data**: quadratic_equation, system_equations, calculus, etc.

#### solutions
```sql
CREATE TABLE solutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    problem_id UUID NOT NULL REFERENCES math_problems(id),
    input_data JSONB NOT NULL,
    solution_data JSONB,
    status solution_status DEFAULT 'pending',
    cost_paid DECIMAL(10,2) NOT NULL,
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Lưu trữ kết quả giải toán và input data
**Indexes**: user_id, problem_id, status, created_at

#### solution_history
```sql
CREATE TABLE solution_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    solution_id UUID NOT NULL REFERENCES solutions(id),
    user_id UUID NOT NULL,
    access_type VARCHAR(50) DEFAULT 'view',
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Theo dõi việc user xem lại kết quả đã giải

#### problem_statistics
```sql
CREATE TABLE problem_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID NOT NULL REFERENCES math_problems(id),
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    successful_solutions INTEGER DEFAULT 0,
    failed_solutions INTEGER DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0.00,
    avg_processing_time_ms DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, date)
);
```
**Purpose**: Thống kê hàng ngày cho analytics và business intelligence

## 📝 Content Service Database (content_service_db)

### Entity Relationship Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│content_categories│    │     pages       │    │  translations   │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (PK)         │◄──┐│ id (PK)         │───►│ id (PK)         │
│ category_name   │   └│ category_id(FK) │    │ entity_type     │
│ category_slug   │    │ title           │    │ entity_id       │
│ parent_id (FK)  │    │ slug            │    │ language_code   │
│ sort_order      │    │ content         │    │ field_name      │
│ is_active       │    │ status          │    │ translated_text │
└─────────────────┘    │ meta_title      │    │ created_at      │
                       │ meta_desc       │    │ updated_at      │
                       │ view_count      │    └─────────────────┘
                       │ created_at      │
                       │ updated_at      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │      faqs       │
                       │─────────────────│
                       │ id (PK)         │
                       │ category_id(FK) │
                       │ question        │
                       │ answer          │
                       │ sort_order      │
                       │ is_featured     │
                       │ view_count      │
                       │ created_at      │
                       │ updated_at      │
                       └─────────────────┘
```

### Tables Detail

#### content_categories
```sql
CREATE TABLE content_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id UUID REFERENCES content_categories(id),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Phân loại content theo cây thư mục
**Structure**: Hướng dẫn > Toán cơ bản > Phương trình bậc 2

#### pages
```sql
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES content_categories(id),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    status page_status DEFAULT 'draft',
    meta_title VARCHAR(255),
    meta_description TEXT,
    featured_image_url TEXT,
    view_count INTEGER DEFAULT 0,
    author_id UUID,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Lưu trữ trang web, bài viết, hướng dẫn
**SEO**: meta_title, meta_description, slug cho SEO optimization

#### faqs
```sql
CREATE TABLE faqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES content_categories(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Quản lý câu hỏi thường gặp
**Features**: Featured FAQs, view tracking, tagging

#### translations
```sql
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    translated_text TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    translator_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, language_code, field_name)
);
```
**Purpose**: Hỗ trợ đa ngôn ngữ cho content
**Languages**: vi (Vietnamese), en (English)

## 🔧 Admin Service Database (admin_service_db)

### Entity Relationship Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  admin_users    │    │ system_settings │    │   audit_logs    │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ username        │    │ setting_key     │    │ user_id         │
│ email           │    │ setting_value   │    │ action          │
│ password_hash   │    │ setting_type    │    │ entity_type     │
│ full_name       │    │ category        │    │ entity_id       │
│ permissions     │    │ is_public       │    │ old_values      │
│ is_active       │    │ is_encrypted    │    │ new_values      │
│ last_login      │    │ description     │    │ ip_address      │
│ created_at      │    │ created_at      │    │ user_agent      │
│ updated_at      │    │ updated_at      │    │ execution_time  │
└─────────────────┘    └─────────────────┘    │ created_at      │
                                              └─────────────────┘
```

### Tables Detail

#### admin_users
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_super_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Quản lý admin accounts với fine-grained permissions
**Security**: Login attempts tracking, account locking

#### system_settings
```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type setting_type DEFAULT 'string',
    category VARCHAR(50) DEFAULT 'general',
    is_public BOOLEAN DEFAULT FALSE,
    is_encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    validation_rules JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Cấu hình hệ thống động
**Categories**: general, payment, email, security, maintenance

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action audit_action NOT NULL,
    entity_type audit_entity NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
**Purpose**: Comprehensive audit trail cho security và compliance
**Retention**: 2 years for compliance requirements

## 🔄 Database Relationships

### Cross-Service Relationships
```
User Service (users.id) ←→ Payment Service (transactions.user_id)
User Service (users.id) ←→ Math Solver (solutions.user_id)
User Service (users.id) ←→ Admin Service (audit_logs.user_id)
```

### Data Consistency Strategy
- **Eventual Consistency**: Cross-service references
- **Event-Driven**: Database changes trigger events
- **Saga Pattern**: Distributed transactions
- **Compensation**: Rollback mechanisms

## 📊 Performance Considerations

### Indexing Strategy
```sql
-- User Service
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_active ON users(role_id, is_active);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);

-- Payment Service
CREATE INDEX idx_transactions_user_status ON transactions(user_id, status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_reference ON transactions(reference_code);

-- Math Solver
CREATE INDEX idx_solutions_user_created ON solutions(user_id, created_at DESC);
CREATE INDEX idx_solutions_problem_status ON solutions(problem_id, status);

-- Content Service
CREATE INDEX idx_pages_slug ON pages(slug);
CREATE INDEX idx_pages_status_published ON pages(status, published_at DESC);

-- Admin Service
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

### Partitioning Strategy
```sql
-- Partition audit_logs by month
CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Partition transactions by quarter
CREATE TABLE transactions_y2024q1 PARTITION OF transactions
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

### Connection Pooling
```python
# SQLAlchemy configuration
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

## 🔒 Security Considerations

### Data Encryption
- **At Rest**: PostgreSQL TDE (Transparent Data Encryption)
- **In Transit**: SSL/TLS connections
- **Application Level**: Sensitive fields encrypted (passwords, API keys)

### Access Control
- **Database Level**: Role-based access control
- **Application Level**: Service-specific database users
- **Network Level**: VPC isolation, security groups

### Backup Strategy
```bash
# Daily automated backups
pg_dump -h postgres -U postgres user_service_db > backup_user_$(date +%Y%m%d).sql
pg_dump -h postgres -U postgres payment_service_db > backup_payment_$(date +%Y%m%d).sql
# ... for all databases

# Point-in-time recovery enabled
# Retention: 30 days for daily, 12 months for monthly
```

## 📈 Monitoring & Maintenance

### Database Monitoring
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long running queries
SELECT query, query_start, state
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 minutes';

-- Database sizes
SELECT datname, pg_size_pretty(pg_database_size(datname))
FROM pg_database;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Maintenance Tasks
- **VACUUM ANALYZE**: Weekly automated
- **REINDEX**: Monthly for heavily updated tables
- **Statistics Update**: Daily automated
- **Log Rotation**: Weekly cleanup

---

**Database Schema Version: 1.0.0**
**Last Updated: 2024-08-14**
