-- Payment Service Database Initialization Script
-- File: scripts/payment-service/init.sql
-- Tạo các bảng cho Payment Service: transactions, payment_methods, transaction_logs, balances

-- Enum types cho payment service
CREATE TYPE transaction_type AS ENUM ('deposit', 'withdrawal', 'service_payment', 'refund', 'bonus');
CREATE TYPE transaction_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE payment_method_type AS ENUM ('bank_transfer', 'momo', 'zalopay', 'vnpay', 'qr_code', 'credit_card');

-- Bảng payment_methods: Các phương thức thanh toán
CREATE TABLE IF NOT EXISTS payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_type payment_method_type NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    description TEXT,
    config JSONB DEFAULT '{}', -- Cấu hình API keys, endpoints
    is_active BOOLEAN DEFAULT TRUE,
    min_amount DECIMAL(15,2) DEFAULT 0.00,
    max_amount DECIMAL(15,2) DEFAULT 999999999.99,
    fee_percentage DECIMAL(5,4) DEFAULT 0.0000, -- Phí theo %
    fee_fixed DECIMAL(15,2) DEFAULT 0.00, -- Phí cố định
    processing_time_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng transactions: Giao dịch chính
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Reference đến User Service
    transaction_type transaction_type NOT NULL,
    status transaction_status DEFAULT 'pending',
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    fee_amount DECIMAL(15,2) DEFAULT 0.00,
    net_amount DECIMAL(15,2) NOT NULL, -- amount - fee_amount
    currency VARCHAR(3) DEFAULT 'VND',
    payment_method_id UUID REFERENCES payment_methods(id),
    external_transaction_id VARCHAR(255), -- ID từ cổng thanh toán
    reference_code VARCHAR(100) UNIQUE, -- Mã tham chiếu duy nhất
    description TEXT,
    metadata JSONB DEFAULT '{}', -- Thông tin bổ sung
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng transaction_logs: Lịch sử thay đổi trạng thái giao dịch
CREATE TABLE IF NOT EXISTS transaction_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    old_status transaction_status,
    new_status transaction_status NOT NULL,
    reason TEXT,
    changed_by VARCHAR(100), -- System hoặc User ID
    ip_address INET,
    user_agent TEXT,
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng balances: Snapshot số dư theo thời gian (cho audit)
CREATE TABLE IF NOT EXISTS balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    change_amount DECIMAL(15,2) NOT NULL,
    transaction_id UUID REFERENCES transactions(id),
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_reference_code ON transactions(reference_code);
CREATE INDEX IF NOT EXISTS idx_transactions_external_id ON transactions(external_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_transaction_id ON transaction_logs(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_logs_created_at ON transaction_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_balances_user_id ON balances(user_id);
CREATE INDEX IF NOT EXISTS idx_balances_created_at ON balances(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_methods_type ON payment_methods(method_type);
CREATE INDEX IF NOT EXISTS idx_payment_methods_active ON payment_methods(is_active);

-- Thêm dữ liệu mặc định cho payment_methods
INSERT INTO payment_methods (method_type, method_name, description, min_amount, max_amount, fee_percentage) VALUES
('bank_transfer', 'Chuyển khoản ngân hàng', 'Chuyển khoản qua QR Code VietQR', 10000.00, 50000000.00, 0.0000),
('momo', 'Ví MoMo', 'Thanh toán qua ví điện tử MoMo', 10000.00, 20000000.00, 0.0150),
('zalopay', 'ZaloPay', 'Thanh toán qua ví điện tử ZaloPay', 10000.00, 20000000.00, 0.0150),
('vnpay', 'VNPay', 'Cổng thanh toán VNPay', 10000.00, 50000000.00, 0.0200),
('qr_code', 'Quét mã QR', 'Thanh toán bằng quét mã QR', 10000.00, 10000000.00, 0.0000)
ON CONFLICT DO NOTHING;

-- Tạo trigger để tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_methods_updated_at BEFORE UPDATE ON payment_methods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function để tạo reference_code duy nhất
CREATE OR REPLACE FUNCTION generate_reference_code()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TXN_' || TO_CHAR(NOW(), 'YYYYMMDD') || '_' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
END;
$$ LANGUAGE plpgsql;

-- Trigger để tự động tạo reference_code
CREATE OR REPLACE FUNCTION set_reference_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reference_code IS NULL THEN
        NEW.reference_code = generate_reference_code();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_transaction_reference_code BEFORE INSERT ON transactions
    FOR EACH ROW EXECUTE FUNCTION set_reference_code();
