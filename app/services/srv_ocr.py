"""
OCR Service - Text extraction from images using OpenAI Vision
"""
import base64
import aiohttp
import os


class OCRService:
    """Service xử lý OCR với OpenAI Vision API"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    
    @staticmethod
    async def extract_text_from_image(image_bytes: bytes, lang: str = "vi") -> str:
        """
        Trích xuất text từ ảnh bằng OpenAI Vision API
        
        Args:
            image_bytes: Dữ liệu ảnh dạng bytes
            lang: Ngôn ngữ (không dùng, OpenAI tự nhận dạng)
            
        Returns:
            Text đã trích xuất
        """
        try:
            if not OCRService.OPENAI_API_KEY:
                raise Exception("OPENAI_API_KEY chưa được cấu hình")
            
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Call OpenAI Vision API
            headers = {
                "Authorization": f"Bearer {OCRService.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",  # Model Vision rẻ nhất
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Trích xuất TẤT CẢ văn bản trong ảnh này. Chỉ trả về text thuần túy, không giải thích, không format markdown. Nếu có nhiều đoạn, xuống dòng giữa các đoạn."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(OCRService.OPENAI_API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        extracted_text = data['choices'][0]['message']['content']
                        return extracted_text.strip()
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {error_text}")
                        
        except Exception as e:
            raise Exception(f"Lỗi OCR: {str(e)}")
