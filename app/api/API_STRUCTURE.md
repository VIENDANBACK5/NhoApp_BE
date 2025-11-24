# 📁 Cấu trúc API - Hướng dẫn

## 🗂️ Tổ chức thư mục

```
app/api/
├── healthcheck.py          # Health check endpoint
└── v1/                     # API Version 1
    ├── auth.py             # 🔐 Xác thực (Login, Register)
    ├── users.py            # 👥 Quản lý người dùng (CRUD)
    ├── ocr.py              # 📸 OCR - Trích xuất text từ ảnh
    ├── diaries.py          # 📔 Nhật ký
    ├── notes.py            # 📝 Ghi chú
    ├── reminders.py        # ⏰ Nhắc nhở
    ├── memories.py         # 💭 Ký ức
    ├── health.py           # 🏥 Sức khỏe
    ├── chat.py             # 💬 Chat với AI
    └── profile.py          # 👤 Hồ sơ cá nhân
```

## 📋 Danh sách API theo module

### 🔐 Authentication (`auth.py`)
- `POST /v1/auth/login` - Đăng nhập
- `POST /v1/auth/register` - Đăng ký tài khoản

### 👥 Users (`users.py`)
- `GET /v1/users/all` - Lấy tất cả người dùng
- `GET /v1/users` - Lấy danh sách có phân trang
- `POST /v1/users` - Tạo người dùng mới
- `GET /v1/users/{user_id}` - Lấy thông tin theo ID
- `PUT /v1/users/{user_id}` - Cập nhật đầy đủ
- `PATCH /v1/users/{user_id}` - Cập nhật một phần
- `DELETE /v1/users/{user_id}` - Xóa người dùng

### 📸 OCR (`ocr.py`)
- `POST /v1/ocr` - Trích xuất text từ ảnh

### 📔 Diaries (`diaries.py`)
- `POST /v1/diaries` - Tạo nhật ký từ ảnh (có AI phân tích)
- `GET /v1/diaries` - Lấy danh sách nhật ký

### 📝 Notes (`notes.py`)
- `POST /v1/notes` - Tạo ghi chú từ ảnh (AI phân tích + tự động tạo reminder)
- `GET /v1/notes` - Lấy danh sách ghi chú

### ⏰ Reminders (`reminders.py`)
- `POST /v1/reminders` - Tạo nhắc nhở thủ công
- `GET /v1/reminders` - Lấy danh sách nhắc nhở
- `PUT /v1/reminders/{reminder_id}` - Cập nhật trạng thái

### 💭 Memories (`memories.py`)
- `POST /v1/memories` - Lưu ký ức
- `GET /v1/memories` - Lấy danh sách ký ức
- `GET /v1/memories/prompt` - Gợi ý hồi tưởng cá nhân hóa

### 🏥 Health (`health.py`)
- `POST /v1/health/logs` - Ghi nhật ký sức khỏe
- `GET /v1/health/logs` - Lấy nhật ký sức khỏe
- `GET /v1/health/insights` - Phân tích xu hướng sức khỏe (AI)

### 💬 Chat (`chat.py`)
- `POST /v1/chat` - Chat với AI có ngữ cảnh

### 👤 Profile (`profile.py`)
- `GET /v1/profile` - Lấy thông tin profile
- `POST /v1/profile` - Tạo/cập nhật profile

### ❤️ Health Check (`healthcheck.py`)
- `GET /health-check` - Kiểm tra trạng thái dịch vụ

## ✨ Ưu điểm của cấu trúc mới

### 1️⃣ **Dễ đọc**
- Mỗi file chỉ tập trung vào 1 chức năng
- Dễ tìm kiếm: muốn sửa API chat → mở file `chat.py`

### 2️⃣ **Dễ học**
- Người mới có thể học từng module nhỏ
- Code ngắn gọn, dễ hiểu (mỗi file ~50-150 dòng)

### 3️⃣ **Dễ bảo trì**
- Sửa lỗi ở 1 module không ảnh hưởng module khác
- Test độc lập cho từng module

### 4️⃣ **Dễ mở rộng**
- Thêm chức năng mới → tạo file mới
- Router tự động load (không cần config thủ công)

### 5️⃣ **Phân quyền rõ ràng**
- Các endpoint có `login_required` được đánh dấu rõ ràng
- Dễ audit security

## 🚀 Cách thêm API mới

1. Tạo file mới trong `app/api/v1/`, ví dụ: `notifications.py`
2. Định nghĩa router với prefix và tags:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def list_notifications():
    return {"notifications": []}
```
3. **Không cần config gì thêm!** Router tự động load.

## 📖 API Documentation

Sau khi khởi động server, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Tìm kiếm nhanh

| Muốn làm gì | Xem file |
|------------|----------|
| Thêm endpoint OCR | `api/v1/ocr.py` |
| Sửa logic chat AI | `api/v1/chat.py` |
| Thêm field cho User | `api/v1/users.py` + `models/model_user.py` |
| Sửa phân tích sức khỏe | `api/v1/health.py` + `services/srv_ai.py` |
| Thêm loại reminder mới | `api/v1/reminders.py` |

## 🎯 Best Practices

1. **Mỗi file = 1 resource** (users, notes, reminders...)
2. **Dùng tags** để nhóm API trong Swagger
3. **Docstring** cho mỗi endpoint (hiển thị trong docs)
4. **Dependency injection** (`Depends()`) cho auth, database
5. **Exception handling** nhất quán với `CustomException`

---

**Cấu trúc cũ** (1 file 600 dòng) → **Cấu trúc mới** (10 file, mỗi file ~50-100 dòng) ✨
