import base64
import aiohttp
import os


class OCRService:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    
    @staticmethod
    async def extract_text_from_image(image_bytes: bytes, lang: str = "vi") -> str:
        try:
            if not OCRService.OPENAI_API_KEY:
                raise Exception("OPENAI_API_KEY chưa được cấu hình")
            
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {OCRService.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
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
