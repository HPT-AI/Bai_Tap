-- Admin Service Database Initialization Script
-- File: scripts/admin-service/init.sql
-- Tạo các bảng cho Admin Service: admin_users, system_settings, audit_logs

-- Enum types cho admin service
CREATE TYPE admin_role AS ENUM ('super_admin', 'admin', 'moderator', 'support');
CREATE TYPE setting_type AS ENUM ('string', 'number', 'boolean', 'json', 'text');
CREATE TYPE audit_action AS ENUM ('create', 'update', 'delete', 'login', 'logout', 'view', 'export', 'import');
CREATE TYPE audit_entity AS ENUM ('user', 'transaction', 'solution', 'page', 'faq', 'admin_user', 'system_setting');

-- Bảng admin_users: Quản lý tài khoản admin
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role admin_role DEFAULT 'support',
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    department VARCHAR(100),
    permissions JSONB DEFAULT '{}', -- Quyền chi tiết
    is_active BOOLEAN DEFAULT TRUE,
    is_2fa_enabled BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng system_settings: Cấu hình hệ thống
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type setting_type DEFAULT 'string',
    category VARCHAR(100) DEFAULT 'general',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- Có thể truy cập từ frontend không
    is_encrypted BOOLEAN DEFAULT FALSE, -- Có mã hóa giá trị không
    validation_rules JSONB DEFAULT '{}', -- Rules để validate giá trị
    default_value TEXT,
    created_by UUID REFERENCES admin_users(id),
    updated_by UUID REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng audit_logs: Nhật ký hoạt động hệ thống
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- NULL nếu là system action
    admin_user_id UUID REFERENCES admin_users(id), -- NULL nếu là user action
    action audit_action NOT NULL,
    entity_type audit_entity NOT NULL,
    entity_id UUID, -- ID của đối tượng bị tác động
    old_values JSONB, -- Giá trị cũ (cho update/delete)
    new_values JSONB, -- Giá trị mới (cho create/update)
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(100), -- Để trace request
    execution_time_ms INTEGER, -- Thời gian thực thi
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}', -- Thông tin bổ sung
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng admin_sessions: Quản lý phiên đăng nhập admin
CREATE TABLE IF NOT EXISTS admin_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng system_notifications: Thông báo hệ thống
CREATE TABLE IF NOT EXISTS system_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'info', -- info, warning, error, success
    target_audience VARCHAR(50) DEFAULT 'all', -- all, admins, users, specific_role
    target_criteria JSONB DEFAULT '{}', -- Điều kiện để hiển thị
    is_active BOOLEAN DEFAULT TRUE,
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
CREATE INDEX IF NOT EXISTS idx_admin_users_active ON admin_users(is_active);
CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON system_settings(category);
CREATE INDEX IF NOT EXISTS idx_system_settings_public ON system_settings(is_public);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_user_id ON audit_logs(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_admin_user_id ON admin_sessions(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_token ON admin_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_expires_at ON admin_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_system_notifications_active ON system_notifications(is_active);
CREATE INDEX IF NOT EXISTS idx_system_notifications_dates ON system_notifications(start_date, end_date);

-- Thêm dữ liệu mặc định cho system_settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, category, description, is_public) VALUES
('site_name', 'Website Dịch Vụ Toán Học', 'string', 'general', 'Tên website hiển thị', TRUE),
('site_description', 'Nền tảng giải toán trực tuyến hàng đầu Việt Nam', 'string', 'general', 'Mô tả website', TRUE),
('maintenance_mode', 'false', 'boolean', 'system', 'Chế độ bảo trì', FALSE),
('max_file_upload_size', '10485760', 'number', 'system', 'Kích thước file upload tối đa (bytes)', FALSE),
('default_language', 'vi', 'string', 'localization', 'Ngôn ngữ mặc định', TRUE),
('supported_languages', '["vi", "en"]', 'json', 'localization', 'Các ngôn ngữ được hỗ trợ', TRUE),
('email_from_address', 'noreply@mathservice.com', 'string', 'email', 'Email gửi đi mặc định', FALSE),
('smtp_host', 'localhost', 'string', 'email', 'SMTP server host', FALSE),
('smtp_port', '587', 'number', 'email', 'SMTP server port', FALSE),
('payment_methods_enabled', '["bank_transfer", "momo", "vnpay"]', 'json', 'payment', 'Phương thức thanh toán được bật', FALSE),
('min_deposit_amount', '10000', 'number', 'payment', 'Số tiền nạp tối thiểu (VND)', TRUE),
('max_deposit_amount', '50000000', 'number', 'payment', 'Số tiền nạp tối đa (VND)', TRUE),
('session_timeout_minutes', '60', 'number', 'security', 'Thời gian timeout session (phút)', FALSE),
('max_login_attempts', '5', 'number', 'security', 'Số lần đăng nhập sai tối đa', FALSE),
('account_lockout_minutes', '30', 'number', 'security', 'Thời gian khóa tài khoản (phút)', FALSE)
ON CONFLICT (setting_key) DO NOTHING;

-- Tạo admin user mặc định (password: Admin123!)
INSERT INTO admin_users (username, email, password_hash, full_name, role, permissions) VALUES
(
    'admin',
    'admin@mathservice.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBzpvWGKwxKjyG', -- Admin123!
    'System Administrator',
    'super_admin',
    '{"all": true}'
),
(
    'support',
    'support@mathservice.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBzpvWGKwxKjyG', -- Admin123!
    'Support Staff',
    'support',
    '{"view_users": true, "view_transactions": true, "manage_content": true}'
)
ON CONFLICT (username) DO NOTHING;

-- Tạo trigger để tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_notifications_updated_at BEFORE UPDATE ON system_notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function để log audit tự động
CREATE OR REPLACE FUNCTION log_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    action_type audit_action;
    old_data JSONB;
    new_data JSONB;
BEGIN
    -- Xác định loại action
    IF TG_OP = 'INSERT' THEN
        action_type := 'create';
        old_data := NULL;
        new_data := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'update';
        old_data := row_to_json(OLD)::JSONB;
        new_data := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'delete';
        old_data := row_to_json(OLD)::JSONB;
        new_data := NULL;
    END IF;

    -- Insert audit log
    INSERT INTO audit_logs (
        action,
        entity_type,
        entity_id,
        old_values,
        new_values,
        description
    ) VALUES (
        action_type,
        TG_TABLE_NAME::audit_entity,
        COALESCE(NEW.id, OLD.id),
        old_data,
        new_data,
        TG_OP || ' operation on ' || TG_TABLE_NAME
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Tạo triggers để tự động log audit cho các bảng quan trọng
CREATE TRIGGER audit_admin_users AFTER INSERT OR UPDATE OR DELETE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION log_audit_trigger();

CREATE TRIGGER audit_system_settings AFTER INSERT OR UPDATE OR DELETE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION log_audit_trigger();

-- Function để kiểm tra quyền admin
CREATE OR REPLACE FUNCTION check_admin_permission(admin_id UUID, required_permission TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    admin_permissions JSONB;
    admin_role_name admin_role;
BEGIN
    SELECT permissions, role INTO admin_permissions, admin_role_name
    FROM admin_users
    WHERE id = admin_id AND is_active = TRUE;

    -- Super admin có tất cả quyền
    IF admin_role_name = 'super_admin' OR admin_permissions ? 'all' THEN
        RETURN TRUE;
    END IF;

    -- Kiểm tra quyền cụ thể
    RETURN admin_permissions ? required_permission;
END;
$$ LANGUAGE plpgsql;
