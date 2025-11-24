"""  
Extended User Profile Model
"""
import json
from sqlalchemy import Column, String, Integer, Text, Date
from sqlalchemy.orm import relationship
from app.models.model_base import BareBaseModel
class UserProfile(BareBaseModel):
    """Thông tin chi tiết người dùng"""
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, nullable=False, unique=True)  # Link to User model
    full_name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    birth_date = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    
    # Medical information (stored as JSON strings for Oracle compatibility)
    medical_conditions = Column(Text, default='[]')  # List of medical conditions
    medications = Column(Text, default='[]')  # List of medications [{"name": "", "dosage": "", "frequency": ""}]
    allergies = Column(Text, default='[]')  # List of allergies
    
    # Personal information
    hobbies = Column(Text, default='[]')  # List of hobbies
    important_dates = Column(Text, default='[]')  # List of important dates
    daily_routine = Column(Text, nullable=True)
    
    # Property helpers for JSON fields
    @property
    def medical_conditions_list(self):
        try:
            return json.loads(self.medical_conditions) if self.medical_conditions else []
        except:
            return []
    
    @medical_conditions_list.setter
    def medical_conditions_list(self, value):
        self.medical_conditions = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def medications_list(self):
        try:
            return json.loads(self.medications) if self.medications else []
        except:
            return []
    
    @medications_list.setter
    def medications_list(self, value):
        self.medications = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def allergies_list(self):
        try:
            return json.loads(self.allergies) if self.allergies else []
        except:
            return []
    
    @allergies_list.setter
    def allergies_list(self, value):
        self.allergies = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def hobbies_list(self):
        try:
            return json.loads(self.hobbies) if self.hobbies else []
        except:
            return []
    
    @hobbies_list.setter
    def hobbies_list(self, value):
        self.hobbies = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def important_dates_list(self):
        try:
            return json.loads(self.important_dates) if self.important_dates else []
        except:
            return []
    
    @important_dates_list.setter
    def important_dates_list(self, value):
        self.important_dates = json.dumps(value) if isinstance(value, list) else value
