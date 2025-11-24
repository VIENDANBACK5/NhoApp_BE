# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.model_base import Base  # noqa
from app.models.model_user import User  # noqa
from app.models.model_diary import Diary, Note, Reminder, Memory, HealthLog, Conversation  # noqa
from app.models.model_user_profile import UserProfile  # noqa
