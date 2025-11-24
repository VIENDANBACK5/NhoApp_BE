# Tích hợp BackendNhoApp vào BE1

> Tài liệu hợp nhất mô tả quá trình tích hợp, hướng dẫn setup và toàn bộ API test flow sau khi hợp nhất BackendNhoApp vào BE1.

## 🧭 Điều hướng nhanh
- [I. Tổng quan tích hợp](#i-tong-quan-tich-hop)
- [II. Cấu trúc & Components](#ii-cau-truc--components)
- [III. Thiết lập môi trường](#iii-thiet-lap-moi-truong)
- [IV. Cấu hình & Secrets](#iv-cau-hinh--secrets)
- [V. Database & Migration](#v-database--migration)
- [VI. So sánh BackendNhoApp vs BE1](#vi-so-sanh-backendnhoapp-vs-be1)
- [VII. API Reference + Scenarios](#vii-api-reference--scenarios)
- [VIII. Tips, Tools & Status Codes](#viii-tips-tools--status-codes)
- [IX. Troubleshooting](#ix-troubleshooting)
- [X. Checklist & Tài liệu](#x-checklist--tai-lieu)

---

## I. Tổng quan tích hợp

### ✨ Các năng lực đã hợp nhất
1. **OCR (Tesseract)** – Trích xuất text đa ngôn ngữ (vi/en) từ ảnh.
2. **Speech-to-Text (Omnilingual ASR)** – Chuyển đổi giọng nói thành text, hỗ trợ 1600+ ngôn ngữ với Meta's Omnilingual ASR.
3. **Diaries** – Tạo nhật ký từ ảnh, AI tóm tắt, phân tích cảm xúc.
4. **Smart Notes** – Nhận diện nội dung (hẹn khám, thuốc…), trích xuất thời gian, đánh giá ưu tiên.
5. **Reminders** – Tự sinh nhắc nhở từ ghi chú, quản lý trạng thái hoàn thành.
6. **Memories** – Lưu ký ức có tag, dễ truy vấn.
7. **Health Logs & Insights** – Ghi huyết áp/đường huyết/cân nặng, AI phân tích xu hướng và tư vấn.
8. **AI Chat** – Hội thoại có ngữ cảnh, nhớ lịch sử, cá nhân hóa theo profile.
9. **User Profile** – Thông tin cá nhân, bệnh lý, thuốc, sở thích, ngày quan trọng.

---

## II. Cấu trúc & Components

```
BE1/
├── app/
│   ├── models/
│   │   ├── model_diary.py          # Diary, Note, Reminder, Memory, HealthLog, Conversation
│   │   └── model_user_profile.py   # UserProfile
│   ├── schemas/
│   │   └── sche_diary.py           # Pydantic schemas cho toàn bộ feature mới
│   ├── services/
│   │   ├── srv_ocr.py              # Tesseract wrapper
│   │   └── srv_ai.py               # Groq/Llama 3 AI helper
│   └── api/
│       └── v1/
│           └── api_diary.py        # Routes cho diaries/notes/health/chat...
├── alembic/
│   └── versions/
│       └── add_diary_features.py   # Migration tạo bảng mới
├── requirements.txt                # Bổ sung pytesseract, Pillow, aiohttp
└── .env.example                    # Thêm config cho OCR & Groq
```

---

## III. Thiết lập môi trường

### 1. Cài dependencies Python
```bash
cd /home/ai_team/chung/BE/BE1
pip install -r requirements.txt
```

### 2. Cài Tesseract OCR
- **Ubuntu/Debian**
  ```bash
  sudo apt-get update
  sudo apt-get install tesseract-ocr tesseract-ocr-vie
  ```
- **macOS**
  ```bash
  brew install tesseract tesseract-lang
  ```
- **Windows** – tải bộ cài từ https://github.com/UB-Mannheim/tesseract/wiki

### 3. Khởi tạo file `.env`
```bash
cp .env.example .env
```

### 4. Chạy migration & start server
```bash
alembic upgrade head
uvicorn app.main:app --reload
```

---

## IV. Cấu hình & Secrets

Thêm các biến sau vào `.env` (đã có trong `.env.example`).

```env
# OCR
TESSERACT_CMD=/usr/bin/tesseract

# Groq AI (lấy key tại https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama3-8b-8192
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024
```

### Hướng dẫn lấy Groq API Key
1. Đăng nhập https://console.groq.com/
2. Tạo API key mới trong mục **API Keys**
3. Dán vào `.env` và reload dịch vụ.

---

## V. Database & Migration

- Migration `add_diary_features` tạo các bảng: `user_profiles`, `diaries`, `notes`, `reminders`, `memories`, `health_logs`, `conversations` (FK tới `users.id`, `ON DELETE CASCADE`).
- Sử dụng PostgreSQL thay vì JSON storage cũ, hỗ trợ scale & truy vấn phức tạp.

### Reset migration khi lỗi
```bash
alembic downgrade base
alembic upgrade head
```

---

## VI. So sánh BackendNhoApp vs BE1

| Feature | BackendNhoApp | BE1 (Sau tích hợp) |
|---------|---------------|-------------------|
| Storage | JSON files | PostgreSQL + Alembic |
| Authentication | Không có | JWT (Keycloak-ready) |
| API Structure | Flat routes | Versioned `/api/v1`, `/api/v2` |
| Scalability | Giới hạn | Production-ready, Docker Compose |
| OCR/AI | Local scripts | Service chuẩn hóa, config qua `.env` |
| Testing | Không có | Pytest, API guide chi tiết |

---

## VII. API Reference & Scenarios

### 1. Tổng quan nhanh
- **Base URL:** `http://localhost:8000`
- **Docs:** `/docs`, `/redoc`, `/api/openapi.json`
- **Auth:** Bearer token cho mọi endpoint `/api/v1/*`

| Nhóm | Method | Endpoint | Auth | Mục đích |
| --- | --- | --- | --- | --- |
| Auth | POST | `/api/auth/register` | ❌ | Đăng ký |
| Auth | POST | `/api/auth/login` | ❌ | Lấy JWT |
| Monitoring | GET | `/api/health-check` | ❌ | Kiểm tra service |
| OCR | POST | `/api/v1/ocr` | ✅ | Trích xuất text |
| Diary | POST/GET | `/api/v1/diaries` | ✅ | Lưu / xem nhật ký |
| Notes | POST/GET | `/api/v1/notes` | ✅ | Ghi chú từ ảnh |
| Reminders | POST/GET/PUT | `/api/v1/reminders` | ✅ | Quản lý nhắc nhở |
| Memories | POST/GET | `/api/v1/memories` | ✅ | Lưu ký ức |
| Health | POST/GET | `/api/v1/health/logs` | ✅ | Nhật ký sức khỏe |
| Insights | GET | `/api/v1/health/insights` | ✅ | AI phân tích |
| AI Chat | POST | `/api/v1/chat` | ✅ | Trò chuyện |
| Memory Prompt | GET | `/api/v1/memory-prompt` | ✅ | Gợi ý hồi tưởng |
| Profile | GET/POST | `/api/v1/profile` | ✅ | Hồ sơ người dùng |
| Users | GET | `/api/v1/users` | ✅ | Admin APIs |
| **ASR** | POST | `/api/v1/asr/transcribe` | ✅ | **Chuyển giọng nói thành text** |
| **ASR Batch** | POST | `/api/v1/asr/transcribe/batch` | ✅ | **Xử lý nhiều file âm thanh** |
| **ASR Languages** | GET | `/api/v1/asr/languages` | ✅ | **Danh sách ngôn ngữ hỗ trợ** |

### 2. Public APIs (không cần token)

**Register**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test@123","full_name":"Test User"}'
```

**Login (lấy token)**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}'
```

**Health Check**
```bash
curl http://localhost:8000/api/health-check
```

### 3. APIs cần Authentication

#### OCR
```bash
curl -X POST "http://localhost:8000/api/v1/ocr" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

#### Diaries
- **Create**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/diaries" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "file=@diary.jpg" \
    -F "auto_analyze=true"
  ```
- **List**
  ```bash
  curl -X GET "http://localhost:8000/api/v1/diaries?limit=10" \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

#### Notes
```bash
curl -X POST "http://localhost:8000/api/v1/notes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@note.jpg" \
  -F "auto_analyze=true"
```

#### Reminders
```bash
curl -X POST "http://localhost:8000/api/v1/reminders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Uống thuốc","description":"Huyết áp","remind_at":"2025-11-17T20:00:00"}'
curl -X GET "http://localhost:8000/api/v1/reminders?status=pending" -H "Authorization: Bearer YOUR_TOKEN"
curl -X PUT "http://localhost:8000/api/v1/reminders/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

#### Speech-to-Text (ASR)
```bash
# Transcribe single audio file
curl -X POST "http://localhost:8000/api/v1/asr/transcribe" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.wav" \
  -F "language=vie_Latn"

# Transcribe batch
curl -X POST "http://localhost:8000/api/v1/asr/transcribe/batch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@audio1.wav" \
  -F "files=@audio2.mp3" \
  -F "languages=eng_Latn,vie_Latn" \
  -F "batch_size=2"

# Get supported languages
curl -X GET "http://localhost:8000/api/v1/asr/languages" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check if language is supported
curl -X GET "http://localhost:8000/api/v1/asr/languages/check/vie_Latn" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response mẫu:**
```json
{
  "success": true,
  "text": "Xin chào, đây là bản ghi âm thử nghiệm",
  "language": "vie_Latn",
  "filename": "audio.wav",
  "duration": 2.5
}
```

**Ngôn ngữ phổ biến:**
- English: `eng_Latn`
- Vietnamese: `vie_Latn`
- Spanish: `spa_Latn`
- French: `fra_Latn`
- Chinese (Simplified): `cmn_Hans`
- Japanese: `jpn_Jpan`
- Korean: `kor_Hang`

#### Memories, Health Logs, AI Chat, Profile, User Management
- Các câu lệnh `curl` giữ nguyên như phần API Testing Guide trước đây (đã gom trong nhóm tương ứng và có response mẫu cho Notes, Diaries, Health Insights, AI Chat).

### 4. Response mẫu tiêu biểu
- **Diaries/Notes/Reminders**: gồm trường `summary`, `emotion`, `reminders_created` như tài liệu cũ.
- **Health Insights**
  ```json
  {
    "success": true,
    "total_logs": 15,
    "insights": "Huyết áp ổn định...",
    "recent_logs": [{"log_type": "blood_pressure", "value": "120/80", "created_at": "2025-11-17T08:00:00"}]
  }
  ```
- **AI Chat**
  ```json
  {
    "success": true,
    "response": "Chào bác!...",
    "conversation_id": 1
  }
  ```

### 5. Scenario: Người cao tuổi dùng app 1 ngày
```bash
# 1. Đăng ký
curl -X POST "http://localhost:8000/api/auth/register" -H "Content-Type: application/json" -d '{"username":"nguyen_van_a","email":"a@example.com","password":"Test@123","full_name":"Nguyễn Văn A"}'

# 2. Đăng nhập, lưu token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/json" -d '{"username":"nguyen_van_a","password":"Test@123"}' | jq -r '.access_token')

# 3. Cập nhật profile
curl -X POST "http://localhost:8000/api/v1/profile" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"full_name":"Nguyễn Văn A","age":70,"medical_conditions":["Cao huyết áp"],"hobbies":["Câu cá","Đọc báo"]}'

# 4. Health log buổi sáng
curl -X POST "http://localhost:8000/api/v1/health/logs" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"log_type":"blood_pressure","value":"130/85","note":"Sau tập"}'

# 5. Ghi chú từ ảnh (tùy chọn)
# curl -X POST "http://localhost:8000/api/v1/notes" -H "Authorization: Bearer $TOKEN" -F "file=@note.jpg" -F "auto_analyze=true"

# 6. Tạo nhắc nhở uống thuốc
curl -X POST "http://localhost:8000/api/v1/reminders" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"title":"⏰ Uống thuốc huyết áp","description":"Sau bữa sáng","remind_at":"2025-11-17T08:30:00"}'

# 7. Lưu ký ức & chat với AI
curl -X POST "http://localhost:8000/api/v1/memories" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"content":"Gặp bạn cũ ở công viên","tags":["công viên","bạn bè"]}'
curl -X POST "http://localhost:8000/api/v1/chat" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"message":"Hôm nay tôi thấy vui"}'

# 8. Insights & reminders
curl -X GET "http://localhost:8000/api/v1/health/insights" -H "Authorization: Bearer $TOKEN"
curl -X GET "http://localhost:8000/api/v1/reminders?status=pending" -H "Authorization: Bearer $TOKEN"
```

---

## VIII. Tips, Tools & Status Codes

### Lưu token & tái sử dụng
```bash
export TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@123"}' | jq -r '.access_token')
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/profile
```

### Test nhanh OCR bằng ảnh synthetic
```bash
echo "Khám bệnh ngày 20/11 lúc 9h" > test.txt
convert -size 800x600 xc:white -pointsize 30 -annotate +50+300 "$(cat test.txt)" test.jpg
curl -X POST "http://localhost:8000/api/v1/ocr" -H "Authorization: Bearer $TOKEN" -F "file=@test.jpg"
```

### Format JSON cho dễ nhìn
```bash
curl ... | jq '.'
curl ... | python3 -m json.tool
```

### Truy cập tài liệu API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `curl http://localhost:8000/api/openapi.json | jq '.'`

### Status codes phổ biến
- `200` OK, `201` Created
- `400` Bad Request (input sai)
- `401` Unauthorized (token hết hạn/chưa login)
- `403` Forbidden (không đủ quyền)
- `404` Not Found
- `422` Validation Error
- `500` Internal Server Error

---

## IX. Troubleshooting

### Token hết hạn
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" ... | jq -r '.access_token')
```

### Lỗi upload file
```bash
ls -lh image.jpg
file image.jpg
curl -F "file=@/full/path/to/image.jpg" ...
```

### Tesseract không tìm thấy
```bash
which tesseract
# Cập nhật trong .env tùy hệ điều hành
TESSERACT_CMD=/usr/local/bin/tesseract   # macOS
TESSERACT_CMD=/usr/bin/tesseract         # Linux
```

### Groq API lỗi
- Kiểm tra `GROQ_API_KEY` trong `.env`
- Test gọi API Groq trực tiếp để xác minh
- Kiểm tra network outbound

### Migration lỗi
```bash
alembic downgrade base
alembic upgrade head
```

---

## X. Checklist & Tài liệu

### Checklist triển khai
- [x] Models & schemas
- [x] OCR service (Tesseract)
- [x] Speech-to-Text service (Omnilingual ASR)
- [x] AI service (Groq/Llama3)
- [x] API endpoints & routing
- [x] Alembic migration
- [x] Update `requirements.txt` và `.env.example`
- [ ] `alembic upgrade head`
- [ ] Install PyTorch: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`
- [ ] Install ASR dependencies: `pip install omnilingual-asr`
- [ ] Test toàn bộ endpoints (sử dụng scenario ở trên)
- [ ] Deploy production

### Tài liệu tham khảo
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Omnilingual ASR: https://github.com/facebookresearch/omnilingual-asr
- Groq API: https://console.groq.com/docs
- FastAPI: https://fastapi.tiangolo.com/
- Alembic: https://alembic.sqlalchemy.org/

---

**Hoàn thành tích hợp & tài liệu test!** 🚀
