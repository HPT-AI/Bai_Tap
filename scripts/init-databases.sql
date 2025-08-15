-- Script khởi tạo tất cả databases cho Math Service Website
-- Chạy khi PostgreSQL container khởi động lần đầu

-- Tạo database cho User Service
CREATE DATABASE user_service_db;
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO postgres;

-- Tạo database cho Payment Service
CREATE DATABASE payment_service_db;
GRANT ALL PRIVILEGES ON DATABASE payment_service_db TO postgres;

-- Tạo database cho Math Solver Service
CREATE DATABASE math_solver_db;
GRANT ALL PRIVILEGES ON DATABASE math_solver_db TO postgres;

-- Tạo database cho Content Service
CREATE DATABASE content_service_db;
GRANT ALL PRIVILEGES ON DATABASE content_service_db TO postgres;

-- Tạo database cho Admin Service
CREATE DATABASE admin_service_db;
GRANT ALL PRIVILEGES ON DATABASE admin_service_db TO postgres;

-- Tạo extension UUID cho tất cả databases (để generate UUID keys)
\c user_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c payment_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c math_solver_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c content_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c admin_service_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Quay về database mặc định
\c postgres;
