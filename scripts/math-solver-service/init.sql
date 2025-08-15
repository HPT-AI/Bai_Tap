-- Math Solver Service Database Initialization Script
-- File: scripts/math-solver-service/init.sql
-- Tạo các bảng cho Math Solver Service: math_problems, solutions, solution_history

-- Enum types cho math solver service
CREATE TYPE problem_type AS ENUM ('quadratic_equation', 'system_equations', 'linear_equation', 'polynomial', 'calculus', 'statistics', 'geometry');
CREATE TYPE solution_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'timeout');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard', 'expert');

-- Bảng math_problems: Định nghĩa các loại bài toán
CREATE TABLE IF NOT EXISTS math_problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_type problem_type NOT NULL,
    problem_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    input_schema JSONB NOT NULL, -- Schema định nghĩa input cần thiết
    output_schema JSONB NOT NULL, -- Schema định nghĩa output trả về
    example_input JSONB, -- Ví dụ input
    example_output JSONB, -- Ví dụ output
    difficulty_level difficulty_level DEFAULT 'medium',
    base_price DECIMAL(10,2) NOT NULL CHECK (base_price >= 0),
    processing_time_seconds INTEGER DEFAULT 30,
    algorithm_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng solutions: Lưu trữ các lần giải toán
CREATE TABLE IF NOT EXISTS solutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Reference đến User Service
    problem_id UUID NOT NULL REFERENCES math_problems(id),
    input_data JSONB NOT NULL, -- Dữ liệu đầu vào từ user
    output_data JSONB, -- Kết quả giải toán
    status solution_status DEFAULT 'pending',
    error_message TEXT,
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_duration_ms INTEGER,
    cost_amount DECIMAL(10,2) NOT NULL,
    transaction_id UUID, -- Reference đến Payment Service
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng solution_history: Lịch sử truy cập lại kết quả
CREATE TABLE IF NOT EXISTS solution_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    solution_id UUID NOT NULL REFERENCES solutions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL, -- Để verify quyền truy cập
    access_type VARCHAR(50) DEFAULT 'view', -- view, download, share
    ip_address INET,
    user_agent TEXT,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng problem_statistics: Thống kê sử dụng các loại bài toán
CREATE TABLE IF NOT EXISTS problem_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id UUID NOT NULL REFERENCES math_problems(id),
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    successful_solutions INTEGER DEFAULT 0,
    failed_solutions INTEGER DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0.00,
    avg_processing_time_ms DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, date)
);

-- Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_math_problems_type ON math_problems(problem_type);
CREATE INDEX IF NOT EXISTS idx_math_problems_active ON math_problems(is_active);
CREATE INDEX IF NOT EXISTS idx_math_problems_difficulty ON math_problems(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_solutions_user_id ON solutions(user_id);
CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions(problem_id);
CREATE INDEX IF NOT EXISTS idx_solutions_status ON solutions(status);
CREATE INDEX IF NOT EXISTS idx_solutions_created_at ON solutions(created_at);
CREATE INDEX IF NOT EXISTS idx_solutions_transaction_id ON solutions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_solution_history_solution_id ON solution_history(solution_id);
CREATE INDEX IF NOT EXISTS idx_solution_history_user_id ON solution_history(user_id);
CREATE INDEX IF NOT EXISTS idx_problem_statistics_problem_date ON problem_statistics(problem_id, date);

-- Thêm dữ liệu mặc định cho math_problems
INSERT INTO math_problems (problem_type, problem_name, description, input_schema, output_schema, example_input, example_output, difficulty_level, base_price) VALUES
(
    'quadratic_equation',
    'Giải phương trình bậc 2',
    'Giải phương trình ax² + bx + c = 0 và trả về nghiệm chi tiết',
    '{"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}, "c": {"type": "number"}}, "required": ["a", "b", "c"]}',
    '{"type": "object", "properties": {"discriminant": {"type": "number"}, "roots": {"type": "array"}, "steps": {"type": "array"}}}',
    '{"a": 1, "b": -5, "c": 6}',
    '{"discriminant": 1, "roots": [3, 2], "steps": ["Δ = b² - 4ac = 25 - 24 = 1", "x₁ = (5 + 1)/2 = 3", "x₂ = (5 - 1)/2 = 2"]}',
    'easy',
    5000.00
),
(
    'system_equations',
    'Giải hệ phương trình tuyến tính',
    'Giải hệ phương trình tuyến tính 2 ẩn hoặc 3 ẩn',
    '{"type": "object", "properties": {"equations": {"type": "array"}, "variables": {"type": "array"}}, "required": ["equations", "variables"]}',
    '{"type": "object", "properties": {"solution": {"type": "object"}, "method": {"type": "string"}, "steps": {"type": "array"}}}',
    '{"equations": ["2x + 3y = 7", "x - y = 1"], "variables": ["x", "y"]}',
    '{"solution": {"x": 2, "y": 1}, "method": "substitution", "steps": ["Từ pt2: x = y + 1", "Thế vào pt1: 2(y+1) + 3y = 7", "5y = 5", "y = 1, x = 2"]}',
    'medium',
    8000.00
),
(
    'linear_equation',
    'Giải phương trình tuyến tính',
    'Giải phương trình tuyến tính ax + b = 0',
    '{"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}',
    '{"type": "object", "properties": {"solution": {"type": "number"}, "steps": {"type": "array"}}}',
    '{"a": 2, "b": -6}',
    '{"solution": 3, "steps": ["2x - 6 = 0", "2x = 6", "x = 3"]}',
    'easy',
    3000.00
)
ON CONFLICT DO NOTHING;

-- Tạo trigger để tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_math_problems_updated_at BEFORE UPDATE ON math_problems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solutions_updated_at BEFORE UPDATE ON solutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_problem_statistics_updated_at BEFORE UPDATE ON problem_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function để tính toán chi phí dựa trên độ khó và thời gian xử lý
CREATE OR REPLACE FUNCTION calculate_solution_cost(problem_id UUID, user_id UUID)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    base_cost DECIMAL(10,2);
    difficulty_multiplier DECIMAL(3,2) := 1.0;
BEGIN
    SELECT base_price INTO base_cost FROM math_problems WHERE id = problem_id;

    SELECT CASE difficulty_level
        WHEN 'easy' THEN 1.0
        WHEN 'medium' THEN 1.5
        WHEN 'hard' THEN 2.0
        WHEN 'expert' THEN 3.0
        ELSE 1.0
    END INTO difficulty_multiplier
    FROM math_problems WHERE id = problem_id;

    RETURN base_cost * difficulty_multiplier;
END;
$$ LANGUAGE plpgsql;
