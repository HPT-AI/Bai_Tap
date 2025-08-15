-- Content Service Database Initialization Script
-- File: scripts/content-service/init.sql
-- Tạo các bảng cho Content Service: pages, faqs, content_categories, translations

-- Enum types cho content service
CREATE TYPE page_status AS ENUM ('draft', 'published', 'archived', 'scheduled');
CREATE TYPE content_type AS ENUM ('page', 'faq', 'tutorial', 'news', 'guide');
CREATE TYPE language_code AS ENUM ('vi', 'en', 'zh', 'ja', 'ko');

-- Bảng content_categories: Phân loại nội dung
CREATE TABLE IF NOT EXISTS content_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES content_categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    icon_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng pages: Nội dung trang web
CREATE TABLE IF NOT EXISTS pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    featured_image_url VARCHAR(500),
    content_type content_type DEFAULT 'page',
    status page_status DEFAULT 'draft',
    category_id UUID REFERENCES content_categories(id) ON DELETE SET NULL,
    author_id UUID, -- Reference đến User Service hoặc Admin Service
    view_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng faqs: Câu hỏi thường gặp
CREATE TABLE IF NOT EXISTS faqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category_id UUID REFERENCES content_categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]', -- Array of tags
    related_faqs JSONB DEFAULT '[]', -- Array of related FAQ IDs
    created_by UUID, -- Reference đến Admin Service
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bảng translations: Đa ngôn ngữ cho nội dung
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- 'page', 'faq', 'category'
    entity_id UUID NOT NULL, -- ID của bản ghi gốc
    language_code language_code NOT NULL,
    field_name VARCHAR(100) NOT NULL, -- 'title', 'content', 'description', etc.
    translated_value TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    translated_by UUID, -- Reference đến User hoặc Admin
    approved_by UUID, -- Reference đến Admin
    translation_quality_score DECIMAL(3,2) DEFAULT 0.00, -- 0.00 - 1.00
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, language_code, field_name)
);

-- Bảng page_views: Thống kê lượt xem trang
CREATE TABLE IF NOT EXISTS page_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    page_id UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    user_id UUID, -- NULL nếu anonymous
    ip_address INET,
    user_agent TEXT,
    referrer_url TEXT,
    session_id VARCHAR(255),
    view_duration_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tạo indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_content_categories_parent_id ON content_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_content_categories_slug ON content_categories(category_slug);
CREATE INDEX IF NOT EXISTS idx_content_categories_active ON content_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_pages_slug ON pages(slug);
CREATE INDEX IF NOT EXISTS idx_pages_status ON pages(status);
CREATE INDEX IF NOT EXISTS idx_pages_category_id ON pages(category_id);
CREATE INDEX IF NOT EXISTS idx_pages_content_type ON pages(content_type);
CREATE INDEX IF NOT EXISTS idx_pages_published_at ON pages(published_at);
CREATE INDEX IF NOT EXISTS idx_pages_featured ON pages(is_featured);
CREATE INDEX IF NOT EXISTS idx_faqs_category_id ON faqs(category_id);
CREATE INDEX IF NOT EXISTS idx_faqs_active ON faqs(is_active);
CREATE INDEX IF NOT EXISTS idx_faqs_featured ON faqs(is_featured);
CREATE INDEX IF NOT EXISTS idx_translations_entity ON translations(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language_code);
CREATE INDEX IF NOT EXISTS idx_page_views_page_id ON page_views(page_id);
CREATE INDEX IF NOT EXISTS idx_page_views_created_at ON page_views(created_at);

-- Thêm dữ liệu mặc định cho content_categories
INSERT INTO content_categories (category_name, category_slug, description, sort_order) VALUES
('Hướng dẫn sử dụng', 'huong-dan-su-dung', 'Các hướng dẫn sử dụng website và dịch vụ', 1),
('Toán học cơ bản', 'toan-hoc-co-ban', 'Kiến thức toán học cơ bản', 2),
('Toán học nâng cao', 'toan-hoc-nang-cao', 'Kiến thức toán học nâng cao', 3),
('Câu hỏi thường gặp', 'cau-hoi-thuong-gap', 'Các câu hỏi được hỏi nhiều nhất', 4),
('Tin tức', 'tin-tuc', 'Tin tức và cập nhật mới', 5)
ON CONFLICT (category_slug) DO NOTHING;

-- Thêm dữ liệu mẫu cho pages
INSERT INTO pages (title, slug, content, excerpt, content_type, status, category_id, published_at) VALUES
(
    'Hướng dẫn sử dụng dịch vụ giải toán',
    'huong-dan-su-dung-dich-vu-giai-toan',
    '<h2>Cách sử dụng dịch vụ giải toán</h2><p>Để sử dụng dịch vụ giải toán, bạn cần:</p><ol><li>Đăng ký tài khoản</li><li>Nạp tiền vào tài khoản</li><li>Chọn loại bài toán cần giải</li><li>Nhập dữ liệu đầu vào</li><li>Nhận kết quả chi tiết</li></ol>',
    'Hướng dẫn chi tiết cách sử dụng dịch vụ giải toán trực tuyến',
    'guide',
    'published',
    (SELECT id FROM content_categories WHERE category_slug = 'huong-dan-su-dung' LIMIT 1),
    CURRENT_TIMESTAMP
),
(
    'Giới thiệu về website dịch vụ toán học',
    'gioi-thieu-ve-website-dich-vu-toan-hoc',
    '<h2>Về chúng tôi</h2><p>Website dịch vụ toán học là nền tảng giải toán trực tuyến hàng đầu, cung cấp các dịch vụ:</p><ul><li>Giải phương trình bậc 2</li><li>Giải hệ phương trình tuyến tính</li><li>Giải phương trình tuyến tính</li><li>Và nhiều loại toán khác</li></ul>',
    'Giới thiệu về website và các dịch vụ toán học chúng tôi cung cấp',
    'page',
    'published',
    NULL,
    CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING;

-- Thêm dữ liệu mẫu cho faqs
INSERT INTO faqs (question, answer, category_id, sort_order, is_featured) VALUES
(
    'Làm thế nào để đăng ký tài khoản?',
    'Bạn có thể đăng ký tài khoản bằng cách click vào nút "Đăng ký" ở góc phải trên cùng, sau đó điền thông tin email, mật khẩu và xác nhận email.',
    (SELECT id FROM content_categories WHERE category_slug = 'cau-hoi-thuong-gap' LIMIT 1),
    1,
    TRUE
),
(
    'Các phương thức thanh toán nào được hỗ trợ?',
    'Chúng tôi hỗ trợ các phương thức thanh toán: Chuyển khoản ngân hàng, MoMo, ZaloPay, VNPay và quét mã QR.',
    (SELECT id FROM content_categories WHERE category_slug = 'cau-hoi-thuong-gap' LIMIT 1),
    2,
    TRUE
),
(
    'Giá cả dịch vụ giải toán như thế nào?',
    'Giá dịch vụ phụ thuộc vào độ khó của bài toán: Dễ (3,000-5,000 VND), Trung bình (8,000 VND), Khó (tính theo hệ số nhân). Bạn sẽ thấy giá chính xác trước khi thanh toán.',
    (SELECT id FROM content_categories WHERE category_slug = 'cau-hoi-thuong-gap' LIMIT 1),
    3,
    TRUE
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

CREATE TRIGGER update_content_categories_updated_at BEFORE UPDATE ON content_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pages_updated_at BEFORE UPDATE ON pages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faqs_updated_at BEFORE UPDATE ON faqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function để tự động tạo slug từ title
CREATE OR REPLACE FUNCTION generate_slug(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                TRANSLATE(input_text, 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ',
                                    'aaaaaaaaaaaaaaaaaeeeeeeeeeeiiiiiooooooooooooooouuuuuuuuuuuyyyyyd'),
                '[^a-z0-9\s-]', '', 'g'
            ),
            '\s+', '-', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger để tự động tạo slug cho pages nếu chưa có
CREATE OR REPLACE FUNCTION set_page_slug()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.slug IS NULL OR NEW.slug = '' THEN
        NEW.slug = generate_slug(NEW.title);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_pages_slug BEFORE INSERT ON pages
    FOR EACH ROW EXECUTE FUNCTION set_page_slug();
