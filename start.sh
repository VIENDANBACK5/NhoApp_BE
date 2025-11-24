#!/bin/bash

# Script khởi động BE1 với Docker Compose
# Bao gồm kiểm tra và setup tự động

set -e

echo "🚀 Starting BE1 with Docker Compose..."
echo ""

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker chưa được cài đặt!"
    echo "Cài đặt Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Kiểm tra Docker Compose (v1 hoặc v2)
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose chưa được cài đặt!"
    echo "Cài đặt: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker và Docker Compose đã sẵn sàng"
echo ""

# Kiểm tra .env
if [ ! -f .env ]; then
    echo "📝 Tạo file .env từ .env.example..."
    cp .env.example .env
    echo "✅ File .env đã được tạo"
    echo ""
    echo "⚠️  CHÚ Ý: Cần cập nhật GROQ_API_KEY trong file .env"
    echo "   Lấy API key tại: https://console.groq.com/"
    echo ""
    read -p "Nhấn Enter để tiếp tục hoặc Ctrl+C để dừng và cập nhật .env..."
else
    echo "✅ File .env đã tồn tại"
fi

# Kiểm tra GROQ_API_KEY
if grep -q "GROQ_API_KEY=your_groq_api_key_here" .env || grep -q "GROQ_API_KEY=$" .env; then
    echo ""
    echo "⚠️  CẢNH BÁO: GROQ_API_KEY chưa được cấu hình!"
    echo "   Các tính năng AI sẽ không hoạt động."
    echo "   Lấy key miễn phí tại: https://console.groq.com/"
    echo ""
fi

# Stop các container cũ nếu có
echo "🛑 Dừng các container cũ (nếu có)..."
$COMPOSE_CMD down 2>/dev/null || true
echo ""

# Build và start
echo "🔨 Building Docker images..."
$COMPOSE_CMD build
echo ""

echo "▶️  Starting services..."
$COMPOSE_CMD up -d
echo ""

# Đợi services khởi động
echo "⏳ Đợi services khởi động..."
sleep 5

# Kiểm tra trạng thái
echo "📊 Trạng thái services:"
$COMPOSE_CMD ps
echo ""

# Kiểm tra health
echo "🏥 Kiểm tra health check..."
for i in {1..10}; do
    if curl -s http://localhost:8000/healthcheck > /dev/null 2>&1; then
        echo "✅ API đã sẵn sàng!"
        echo ""
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  API chưa sẵn sàng, kiểm tra logs..."
        echo ""
    else
        echo "   Thử lại ($i/10)..."
        sleep 2
    fi
done

# Kiểm tra Tesseract
echo "🔍 Kiểm tra Tesseract OCR..."
if $COMPOSE_CMD exec -T app tesseract --version > /dev/null 2>&1; then
    echo "✅ Tesseract đã được cài đặt"
    LANGS=$($COMPOSE_CMD exec -T app tesseract --list-langs 2>&1 | grep -E "vie|eng" || true)
    if echo "$LANGS" | grep -q "vie"; then
        echo "✅ Tiếng Việt OCR đã sẵn sàng"
    else
        echo "⚠️  Chưa có language pack tiếng Việt"
    fi
else
    echo "⚠️  Tesseract chưa sẵn sàng"
fi
echo ""

# Thông tin truy cập
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ BE1 đã khởi động thành công!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📡 API Endpoints:"
echo "   • API:          http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/healthcheck"
echo ""
echo "🗄️  Database:"
echo "   • Host: localhost"
echo "   • Port: 5555"
echo "   • User: postgres"
echo "   • Pass: postgres"
echo "   • DB:   postgres"
echo ""
echo "📝 Xem logs:"
echo "   $COMPOSE_CMD logs -f"
echo "   $COMPOSE_CMD logs -f app"
echo ""
echo "🛑 Dừng services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
