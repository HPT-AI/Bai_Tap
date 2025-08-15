# Dockerfile template cho FastAPI services
# Sử dụng Python 3.11 slim image để giảm kích thước container
FROM python:3.11-slim

# Thiết lập working directory trong container
WORKDIR /app

# Cài đặt system dependencies cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt trước để tận dụng Docker layer caching
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Expose port 8000 (port mặc định của FastAPI)
EXPOSE 8000

# Thiết lập environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command để chạy FastAPI application với uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
