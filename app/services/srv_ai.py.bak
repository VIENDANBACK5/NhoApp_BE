"""
AI Service Layer - OpenAI Integration
Các tính năng AI thông minh cho ứng dụng hỗ trợ người cao tuổi
"""
import aiohttp
import re
import os
from typing import Optional, List, Dict
from datetime import datetime, timedelta


class AIService:
    """Service xử lý các tác vụ AI"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))
    
    @staticmethod
    async def call_ai_api(prompt: str, system_prompt: str = "", functions: List[Dict] = None, function_call: str = "auto") -> Optional[str]:
        """Gọi OpenAI API với hỗ trợ function calling"""
        try:
            if not AIService.OPENAI_API_KEY or AIService.OPENAI_API_KEY == "your_openai_api_key_here":
                print("⚠️  OPENAI_API_KEY không hợp lệ - sử dụng mock response")
                return "Xin chào! Tôi là trợ lý AI của ứng dụng hỗ trợ người cao tuổi. Tôi có thể giúp bạn ghi nhật ký, nhắc nhở uống thuốc, và trò chuyện thân thiện. Hiện tại tôi đang chạy ở chế độ demo vì chưa cấu hình OPENAI_API_KEY."
            
            headers = {
                "Authorization": f"Bearer {AIService.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": AIService.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": AIService.TEMPERATURE,
                "max_tokens": AIService.MAX_TOKENS
            }
            
            # Thêm functions nếu có
            if functions:
                payload["functions"] = functions
                payload["function_call"] = function_call
            
            async with aiohttp.ClientSession() as session:
                async with session.post(AIService.OPENAI_API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        message = data['choices'][0]['message']
                        
                        # Xử lý function call nếu có
                        if message.get('function_call'):
                            return message  # Return full message để xử lý function call
                        
                        return message.get('content')
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenAI API Error: {error_text}")
                        return "Xin lỗi, hiện tại hệ thống AI đang gặp sự cố. Vui lòng thử lại sau."
                        
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn."
    
    # ========== DIARY & NOTE ANALYSIS ==========
    
    @staticmethod
    def generate_summary_prompt(text: str) -> str:
        """Tạo prompt tóm tắt nhật ký"""
        return f"""Bạn là trợ lý AI giúp người cao tuổi ghi chép nhật ký. 

Hãy TÓM TẮT nhật ký sau đây một cách ngắn gọn, dễ hiểu, ấm áp và có cảm xúc. 
Nên giữ lại các chi tiết quan trọng về: người, địa điểm, cảm xúc, sự kiện đặc biệt.

Nhật ký gốc:
{text}

Tóm tắt (2-3 câu ngắn gọn):"""
    
    @staticmethod
    async def summarize_diary(text: str) -> Optional[str]:
        """Tóm tắt nội dung nhật ký"""
        return await AIService.call_ai_api(
            AIService.generate_summary_prompt(text),
            "Bạn là trợ lý tóm tắt nhật ký cho người cao tuổi."
        )
    
    @staticmethod
    async def analyze_emotion(text: str) -> Optional[str]:
        """Phân tích cảm xúc từ nhật ký/ghi chú"""
        prompt = f"""Phân tích cảm xúc chính trong đoạn text sau của người cao tuổi.
Trả lời CHỈ MỘT TỪ: vui_vẻ, hạnh_phúc, buồn, lo_lắng, bình_thường, nhớ_nhung, biết_ơn, cô_đơn

Text: {text}

Cảm xúc:"""
        
        result = await AIService.call_ai_api(prompt, "Bạn là chuyên gia phân tích cảm xúc.")
        return result.strip().lower() if result else "bình_thường"
    
    # ========== NOTE INTELLIGENCE ==========
    
    @staticmethod
    async def analyze_note(content: str, user_profile: Optional[Dict] = None) -> Dict:
        """
        Phân tích thông minh nội dung ghi chú
        - Phân loại (thuốc, sự kiện, hẹn khám, công việc...)
        - Trích xuất ngày/giờ
        - Đánh giá mức độ ưu tiên
        - Đề xuất tạo nhắc nhở
        """
        
        profile_context = ""
        if user_profile:
            profile_context = f"""
Thông tin người dùng:
- Tên: {user_profile.get('full_name', 'N/A')}
- Tuổi: {user_profile.get('age', 'N/A')}
- Bệnh lý: {', '.join(user_profile.get('medical_conditions', [])) or 'Không có'}
- Thuốc đang dùng: {', '.join([m.get('name', '') for m in user_profile.get('medications', [])]) or 'Không có'}
"""
        
        prompt = f"""{profile_context}

Phân tích ghi chú sau và trả lời CHÍNH XÁC theo format JSON (không thêm text nào khác):

Ghi chú: "{content}"

{{
  "category": "medication|event|appointment|task|health|other",
  "extracted_datetime": "YYYY-MM-DD HH:MM hoặc null",
  "priority": "high|medium|low",
  "should_create_reminder": true|false,
  "reminder_suggestion": "Gợi ý tiêu đề nhắc nhở (nếu có)",
  "analysis": "Giải thích ngắn gọn"
}}"""
        
        result = await AIService.call_ai_api(
            prompt,
            "Bạn là AI phân tích ghi chú thông minh. Trả lời CHỈ JSON, không có text khác."
        )
        
        if result:
            try:
                # Loại bỏ markdown code block nếu có
                cleaned = result.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
                    cleaned = re.sub(r'\n?```$', '', cleaned)
                
                import json
                return json.loads(cleaned)
            except:
                pass
        
        # Fallback
        return {
            "category": "other",
            "extracted_datetime": None,
            "priority": "medium",
            "should_create_reminder": False,
            "reminder_suggestion": None,
            "analysis": "Không thể phân tích"
        }
    
    # ========== REMINDER GENERATION ==========
    
    @staticmethod
    def generate_reminders_from_note(note_id: int, note_content: str, analysis: Dict, user_id: int) -> List[Dict]:
        """Tạo danh sách nhắc nhở từ ghi chú (trả về dict để tạo trong DB)"""
        reminders = []
        
        if not analysis.get('should_create_reminder'):
            return reminders
        
        extracted_dt = analysis.get('extracted_datetime')
        if not extracted_dt:
            return reminders
        
        try:
            # Parse datetime
            remind_time = datetime.fromisoformat(extracted_dt)
            
            # Tạo các nhắc nhở theo loại
            category = analysis.get('category')
            
            if category == 'medication':
                # Nhắc trước 30 phút
                reminders.append({
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": f"🔔 {analysis.get('reminder_suggestion', 'Uống thuốc')}",
                    "description": note_content,
                    "remind_at": remind_time - timedelta(minutes=30),
                    "is_completed": False
                })
            
            elif category == 'appointment':
                # Nhắc trước 1 ngày và 1 giờ
                reminders.append({
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": f"📅 Nhắc lịch hẹn ngày mai",
                    "description": note_content,
                    "remind_at": remind_time - timedelta(days=1),
                    "is_completed": False
                })
                reminders.append({
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": f"⏰ {analysis.get('reminder_suggestion', 'Chuẩn bị đi khám')}",
                    "description": note_content,
                    "remind_at": remind_time - timedelta(hours=1),
                    "is_completed": False
                })
            
            elif category == 'event':
                # Nhắc trước 1 ngày
                reminders.append({
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": f"🎉 {analysis.get('reminder_suggestion', 'Sự kiện sắp diễn ra')}",
                    "description": note_content,
                    "remind_at": remind_time - timedelta(days=1),
                    "is_completed": False
                })
            
            else:
                # Default: nhắc đúng giờ
                reminders.append({
                    "user_id": user_id,
                    "note_id": note_id,
                    "title": analysis.get('reminder_suggestion', 'Nhắc nhở'),
                    "description": note_content,
                    "remind_at": remind_time,
                    "is_completed": False
                })
        
        except Exception as e:
            print(f"Error generating reminders: {e}")
        
        return reminders
    
    # ========== MEMORY PROMPTS ==========
    
    @staticmethod
    async def generate_memory_prompt_text(diaries: List, memories: List, user_profile: Optional[Dict] = None) -> Optional[str]:
        """Tạo câu hỏi gợi nhớ dựa trên dữ liệu"""
        
        recent_diaries = sorted(diaries, key=lambda x: x.created_at, reverse=True)[:3]
        diary_context = "\n".join([f"- {d.summary or d.content[:100]}" for d in recent_diaries])
        
        recent_memories = sorted(memories, key=lambda x: x.created_at, reverse=True)[:3]
        memory_context = "\n".join([f"- {m.content[:100]}" for m in recent_memories])
        
        profile_context = ""
        if user_profile:
            hobbies = user_profile.hobbies or []
            important_dates = user_profile.important_dates or []
            profile_context = f"""
Thông tin cá nhân:
- Sở thích: {', '.join(hobbies) if hobbies else 'Chưa có'}
- Ngày quan trọng: {', '.join([str(d) for d in important_dates]) if important_dates else 'Chưa có'}
"""
        
        prompt = f"""Bạn là trợ lý AI thân thiện giúp người cao tuổi gợi nhớ lại kỷ niệm.

{profile_context}

Nhật ký gần đây:
{diary_context if diary_context else "Chưa có nhật ký"}

Ký ức đã lưu:
{memory_context if memory_context else "Chưa có ký ức"}

Yêu cầu:
- Tạo MỘT câu hỏi gợi mở sâu sắc, ấm áp để khơi gợi ký ức đẹp
- Câu hỏi phải tự nhiên, thân mật như cháu hỏi ông bà
- Liên kết với thông tin cá nhân, sở thích, nhật ký gần đây
- Gợi mở về: gia đình, tuổi thơ, món ăn, địa điểm, con người...

Câu hỏi gợi nhớ:"""
        
        return await AIService.call_ai_api(
            prompt,
            "Bạn là trợ lý tạo câu hỏi gợi nhớ cho người cao tuổi."
        )
    
    # ========== HEALTH INSIGHTS ==========
    
    @staticmethod
    async def analyze_health_trend(health_logs: List, user_profile: Optional[Dict] = None) -> Optional[str]:
        """Phân tích xu hướng sức khỏe"""
        
        if not health_logs:
            return None
        
        # Lấy 10 logs gần nhất
        from datetime import datetime
        recent_logs = sorted(health_logs, key=lambda x: x.created_at, reverse=True)[:10]
        log_summary = "\n".join([
            f"- {log.log_type}: {log.value} ({datetime.fromtimestamp(log.created_at).strftime('%Y-%m-%d') if isinstance(log.created_at, (int, float)) else log.created_at.strftime('%Y-%m-%d')})"
            for log in recent_logs
        ])
        
        medical_context = ""
        if user_profile and user_profile.medical_conditions:
            medical_context = f"Bệnh lý hiện tại: {', '.join(user_profile.medical_conditions)}"
        
        prompt = f"""{medical_context}

Dữ liệu sức khỏe gần đây:
{log_summary}

Hãy phân tích xu hướng sức khỏe và đưa ra lời khuyên ngắn gọn (2-3 câu), thân thiện, dễ hiểu cho người cao tuổi.
Nếu thấy dấu hiệu bất thường, khuyên nên gặp bác sĩ."""
        
        return await AIService.call_ai_api(
            prompt,
            "Bạn là trợ lý sức khỏe AI, không phải bác sĩ, chỉ đưa ra lời khuyên tham khảo."
        )
    
    # ========== HELPER FUNCTIONS ==========
    
    @staticmethod
    def get_current_datetime_info() -> Dict:
        """Lấy thông tin ngày giờ hiện tại chi tiết"""
        from datetime import datetime
        now = datetime.now()
        
        # Tên các ngày trong tuần và tháng tiếng Việt
        weekdays_vi = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        weekday = weekdays_vi[now.weekday()]
        
        return {
            "datetime": now.strftime('%Y-%m-%d %H:%M:%S'),
            "date": now.strftime('%d/%m/%Y'),
            "time": now.strftime('%H:%M'),
            "weekday": weekday,
            "day": now.day,
            "month": now.month,
            "year": now.year,
            "formatted": f"{now.strftime('%H:%M')}, {weekday}, ngày {now.day} tháng {now.month} năm {now.year}"
        }
    
    @staticmethod
    def convert_to_lunar_date(day: int, month: int, year: int) -> Dict:
        """Chuyển đổi dương lịch sang âm lịch"""
        try:
            from lunarcalendar import Converter, Lunar
            solar_date = Converter.Solar2Lunar(year, month, day)
            
            return {
                "lunar_day": solar_date.day,
                "lunar_month": solar_date.month,
                "lunar_year": solar_date.year,
                "is_leap": solar_date.isleap,
                "formatted": f"Ngày {solar_date.day} tháng {solar_date.month} năm {solar_date.year} âm lịch"
            }
        except Exception as e:
            print(f"Lỗi chuyển đổi lịch âm: {e}")
            return {
                "lunar_day": day,
                "lunar_month": month,
                "lunar_year": year,
                "formatted": "Không thể chuyển đổi lịch âm"
            }
    
    # ========== CONVERSATIONAL AI ==========
    
    @staticmethod
    async def chat_with_context(
        user_message: str,
        conversation_history: List[Dict],
        user_profile: Optional[Dict] = None
    ) -> Optional[str]:
        """Chat AI thuần túy - chỉ gọi OpenAI"""
        
        # Build system prompt
        system_prompt = "Bạn là trợ lý AI hỗ trợ người cao tuổi. Luôn xưng 'cháu' và gọi người dùng là 'bác/ông/bà'. Lịch sự, kính trọng, thân thiện. Trả lời ngắn gọn 1-3 câu."
        
        # Build messages cho OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Thêm lịch sử hội thoại (5 tin nhắn gần nhất)
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        # Thêm tin nhắn hiện tại
        messages.append({"role": "user", "content": user_message})
        
        # Gọi OpenAI
        try:
            if not AIService.OPENAI_API_KEY or AIService.OPENAI_API_KEY == "your_openai_api_key_here":
                return "Dạ bác, cháu đang gặp sự cố với hệ thống. Bác vui lòng thử lại sau ạ."
            
            headers = {
                "Authorization": f"Bearer {AIService.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": AIService.OPENAI_MODEL,
                "messages": messages,
                "temperature": AIService.TEMPERATURE,
                "max_tokens": AIService.MAX_TOKENS
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(AIService.OPENAI_API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        return "Dạ bác, cháu đang gặp chút vấn đề. Bác thử lại sau nhé ạ."
        except Exception as e:
            print(f"Chat error: {e}")
            return "Dạ bác, có lỗi xảy ra rồi ạ. Bác thử lại sau nhé."
