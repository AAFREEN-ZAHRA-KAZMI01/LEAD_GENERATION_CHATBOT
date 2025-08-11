from openai import OpenAI
from config import Config
import json

class ChatbotCore:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.system_prompt = """You are a professional real estate assistant. Follow these rules:
        
        1. ONLY discuss property-related matters
        2. For property searches, show: Title, Price, Bedrooms, Location
        3. When asked for details, show ALL property information
        4. For off-topic questions respond: "I specialize in property assistance. How can I help with real estate?"
        5. Always maintain a polite, professional tone
        6. Never make up property information
        7. Guide users through: Type → Location → Properties → Details → Contact
        """
    
    def generate_response(self, conversation_history, property_data=None):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": "Current conversation history:"}
        ]
        
        # Add conversation history
        for entry in conversation_history:
            role = "assistant" if entry["speaker"] == "bot" else "user"
            messages.append({"role": role, "content": entry["text"]})
        
        # Add property data if available
        if property_data:
            messages.append({
                "role": "system",
                "content": f"Property data to use: {json.dumps(property_data)}"
            })
        
        response = self.client.chat.completions.create(
            model=Config.CHAT_MODEL,
            messages=messages,
            temperature=0.5  # More deterministic responses
        )
        
        return response.choices[0].message.content