# NhoApp Backend (BE1)

## 🎯 Tổng quan

Backend cho ứng dụng **NhoApp** - Trợ lý AI chăm sóc người cao tuổi, hỗ trợ ghi nhật ký, lưu ký ức, theo dõi sức khỏe và trò chuyện thông minh.

### ✨ Tính năng chính

**🔐 Authentication & User Management**

- JWT-based authentication với refresh token
- CRUD User APIs với phân quyền
- User Profile management (thông tin cá nhân, bệnh lý, thuốc, sở thích)

**📝 Nhật ký & Ghi chú**

- Diary: Lưu nhật ký với AI tóm tắt và phân tích cảm xúc
- Smart Notes: Tự động phân tích nội dung (hẹn khám, thuốc), trích xuất thời gian, đánh giá độ ưu tiên
- Reminders: Tự động sinh nhắc nhở từ ghi chú, quản lý trạng thái hoàn thành

**💭 Ký ức (Memories)**

- Lưu ký ức dạng text với tags
- Lưu ảnh + audio chú thích (ảnh gia đình, con cháu)
- CRUD operations: Create, Read, Update, Delete
- Memory prompt AI: Gợi ý câu chuyện cá nhân hóa để người cao tuổi hồi tưởng

**🏥 Theo dõi sức khỏe**

- Health Logs: Ghi huyết áp, đường huyết, cân nặng, thuốc, triệu chứng
- AI Health Insights: Phân tích xu hướng sức khỏe và đưa ra tư vấn

**🤖 AI Features**

- OCR (Tesseract): Trích xuất text từ ảnh (tiếng Việt/Anh)
- Speech-to-Text (ASR): Chuyển giọng nói thành text (1600+ ngôn ngữ)
- AI Chat: Trò chuyện có ngữ cảnh, nhớ lịch sử, cá nhân hóa theo profile
- Groq/Llama 3: AI analysis và conversation

**🗄️ Database**

- Oracle Cloud Database
- SQLAlchemy ORM với custom Oracle adaptations
- Alembic migrations

**🐳 DevOps**

- Docker & Docker Compose
- Health check endpoints
- Logging & monitoring

## 📁 Cấu trúc project

```txt
BE1/
├── alembic/
│   ├── versions/
│   │   ├── initial_.py              # Base tables (users)
│   │   ├── add_diary_features.py    # Diary ecosystem tables
│   │   └── create_sequences.py      # Oracle sequences & triggers
│   └── env.py
├── app/
│   ├── api/
│   │   ├── api_auth.py              # Login, Register
│   │   ├── api_healthcheck.py       # Health check
│   │   └── v1/
│   │       ├── api_user.py          # User CRUD
│   │       ├── api_diary.py         # Diaries, Notes, Health, Chat
│   │       ├── api_test.py          # ASR endpoints
│   │       └── memories.py          # Memory CRUD + Photo/Audio
│   ├── core/
│   │   ├── config.py                # Environment config
│   │   ├── database.py              # Oracle DB connection
│   │   ├── security.py              # JWT & password hashing
│   │   └── router.py                # API routing
│   ├── models/
│   │   ├── model_user.py            # User model
│   │   ├── model_user_profile.py    # UserProfile
│   │   └── model_diary.py           # Diary, Note, Reminder, Memory, HealthLog, Conversation
│   ├── schemas/
│   │   ├── sche_auth.py             # Auth schemas
│   │   ├── sche_user.py             # User schemas
│   │   └── sche_diary.py            # All diary feature schemas
│   ├── services/
│   │   ├── srv_ai.py                # Groq AI services
│   │   ├── srv_ocr.py               # Tesseract OCR
│   │   ├── srv_storage.py           # File storage (images, audio)
│   │   └── srv_auth.py              # Auth logic
│   ├── utils/
│   │   ├── login_manager.py         # JWT authentication
│   │   ├── exception_handler.py     # Custom exceptions
│   │   └── paging.py                # Pagination
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── INTEGRATION_GUIDE.md             # 📖 Chi tiết API & flows
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd /home/ai_team/chung/BE/BE1
cp .env.example .env
# Điền thông tin Oracle DB, Groq API key vào .env
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt

# Cài Tesseract OCR
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### 3. Run với Docker

```bash
docker compose up -d
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Migration (nếu cần)

```bash
alembic upgrade head
```

## 📚 API Documentation

Chi tiết đầy đủ xem tại **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)**

### Endpoints chính

**Authentication**

- `POST /api/v1/auth/register` - Đăng ký
- `POST /api/v1/auth/login` - Login (lấy JWT token)

**Memories (CRUD)**

- `POST /api/v1/memory` - Tạo ký ức text
- `POST /api/v1/memory/photo_audio` - Lưu ảnh + audio ký ức
- `GET /api/v1/memory` - List ký ức
- `GET /api/v1/memory/{id}` - Chi tiết 1 ký ức
- `PUT /api/v1/memory/{id}` - Cập nhật ký ức
- `DELETE /api/v1/memory/{id}` - Xóa ký ức

**Diary & Notes**

- `POST /api/v1/diaries` - Tạo nhật ký (có AI analysis)
- `POST /api/v1/notes` - Tạo ghi chú (AI extract info)
- `GET /api/v1/notes` - List ghi chú

**Reminders**

- `POST /api/v1/reminders` - Tạo nhắc nhở
- `GET /api/v1/reminders?status=pending` - List reminders
- `PUT /api/v1/reminders/{id}` - Đánh dấu hoàn thành

**Health**

- `POST /api/v1/health/logs` - Ghi health metrics
- `GET /api/v1/health/insights` - AI phân tích sức khỏe

**AI Services**

- `POST /api/v1/ocr` - OCR extract text từ ảnh
- `POST /api/v1/asr/transcribe` - Speech to text
- `POST /api/v1/chat` - AI conversation
- `GET /api/v1/memory/prompt` - Gợi ý câu chuyện

## 🗄️ Database Models

**Core Tables**

- `users` - User accounts
- `user_profiles` - Thông tin chi tiết người dùng

**Diary Ecosystem**

- `diaries` - Nhật ký
- `notes` - Ghi chú thông minh
- `reminders` - Nhắc nhở
- `memories` - Ký ức (text + ảnh + audio)
- `health_logs` - Nhật ký sức khỏe
- `conversations` - Lịch sử chat AI

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: Oracle Cloud Database
- **ORM**: SQLAlchemy with Oracle dialect
- **Migration**: Alembic
- **AI**: Groq (Llama 3), OpenAI GPT
- **OCR**: Tesseract
- **ASR**: Meta Omnilingual ASR (1600+ languages)
- **Auth**: JWT (access + refresh tokens)
- **Container**: Docker, Docker Compose
- **Storage**: Local file system (images, audio)

## 🔧 Configuration

Key environment variables (`.env`):

```env
# Database
ORACLE_DSN=...
ORACLE_USER=...
ORACLE_PASSWORD=...
ORACLE_WALLET_DIR=...

# AI Services
GROQ_API_KEY=...
OPENAI_API_KEY=...

# OCR
TESSERACT_CMD=/usr/bin/tesseract

# JWT
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
```

## 🐛 Troubleshooting

**Common Issues:**

1. **Oracle connection fails**

   - Check wallet files in `app/db-oci/wallet/`
   - Verify `ORACLE_WALLET_DIR` path in .env

2. **OCR not working**

   - Install: `sudo apt-get install tesseract-ocr tesseract-ocr-vie`
   - Check path: `which tesseract`

3. **Migration errors**

   - Use sequences for Oracle: `create_sequences.py`
   - Stamp existing: `alembic stamp head`

4. **Memory API returns 422**
   - Ensure `tags` is array, not string
   - Check `note_id` is null/None, not 0

## 📖 Migrations

Migration là tính năng quản lý thay đổi schema database

```python
# alembic/versions/initial.py

...
"""empty message

Revision ID: initial
Revises:
Create Date: 2025-05-21 07:30:17.705859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

...
```
