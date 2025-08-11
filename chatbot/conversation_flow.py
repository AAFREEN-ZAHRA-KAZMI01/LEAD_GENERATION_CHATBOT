from enum import Enum, auto
import json
import re
from typing import Optional, Dict

class ConversationState(Enum):
    GREETING = auto()
    PROPERTY_TYPE_QUESTION = auto()
    LOCATION_QUESTION = auto()
    SHOWING_PROPERTIES = auto()
    SHOWING_DETAILS = auto()
    CONTACT_COLLECTION = auto()
    GOODBYE = auto()

class ConversationFlow:
    def __init__(self, redis_connector):
        self.redis = redis_connector
        self.current_state = ConversationState.GREETING
        self.property_types = {
            "house": "House", 
            "apartment": "Apartment",
            "commercial": "Commercial",
            "plot": "Plot"
        }

    def update_state(self, session_id: str, user_input: str) -> Optional[str]:
        user_input = user_input.lower().strip()
        
        if self.current_state == ConversationState.GREETING:
            return self._handle_greeting(user_input, session_id)
            
        elif self.current_state == ConversationState.PROPERTY_TYPE_QUESTION:
            return self._handle_property_type(user_input, session_id)
            
        elif self.current_state == ConversationState.LOCATION_QUESTION:
            return self._handle_location(user_input, session_id)
            
        elif self.current_state == ConversationState.SHOWING_PROPERTIES:
            return self._handle_property_response(user_input, session_id)
            
        elif self.current_state == ConversationState.SHOWING_DETAILS:
            return self._handle_details_response(user_input, session_id)
            
        elif self.current_state == ConversationState.CONTACT_COLLECTION:
            return self._handle_contact_collection(user_input, session_id)
            
        return None

    def _handle_greeting(self, user_input: str, session_id: str) -> str:
        if any(keyword in user_input for keyword in ["property", "house", "apartment", "commercial", "plot"]):
            prop_type = self._extract_property_type(user_input)
            if prop_type:
                self.redis.update_session_field(session_id, "property_type", prop_type)
                loc = self._extract_location(user_input)
                if loc:
                    self.redis.update_session_field(session_id, "location", loc)
                    self.current_state = ConversationState.SHOWING_PROPERTIES
                    return "SEARCH_PROPERTIES"
                self.current_state = ConversationState.LOCATION_QUESTION
                return "Which location are you interested in?"
            self.current_state = ConversationState.PROPERTY_TYPE_QUESTION
            return "What type of property are you looking for? (House, Apartment, Commercial, Plot)"
        return "I can help you find properties. What type are you interested in?"

    def _handle_property_type(self, user_input: str, session_id: str) -> str:
        prop_type = self._extract_property_type(user_input)
        if prop_type:
            self.redis.update_session_field(session_id, "property_type", prop_type)
            loc = self._extract_location(user_input)
            if loc:
                self.redis.update_session_field(session_id, "location", loc)
                self.current_state = ConversationState.SHOWING_PROPERTIES
                return "SEARCH_PROPERTIES"
            self.current_state = ConversationState.LOCATION_QUESTION
            return "Which location are you interested in?"
        return "Please choose from: House, Apartment, Commercial, or Plot"

    def _handle_location(self, user_input: str, session_id: str) -> str:
        location = self._clean_location_input(user_input)
        if location:
            self.redis.update_session_field(session_id, "location", location)
            self.current_state = ConversationState.SHOWING_PROPERTIES
            return "SEARCH_PROPERTIES"
        return "Please specify a location (e.g. 'I-8', 'DHA Phase 5')"

    def _handle_property_response(self, user_input: str, session_id: str) -> str:
        if any(word in user_input for word in ["detail", "more", "info", "show", "yes"]):
            self.current_state = ConversationState.SHOWING_DETAILS
            return "PROPERTY_DETAILS"
        elif any(word in user_input for word in ["contact", "interested", "connect"]):
            self.current_state = ConversationState.CONTACT_COLLECTION
            return "REQUEST_CONTACT"
        else:
            self.current_state = ConversationState.GOODBYE
            return "Thank you for your interest!"

    def _handle_details_response(self, user_input: str, session_id: str) -> str:
        self.current_state = ConversationState.CONTACT_COLLECTION
        return "REQUEST_CONTACT"

    def _handle_contact_collection(self, user_input: str, session_id: str) -> str:
        parts = [part.strip() for part in user_input.split(",")]
        if len(parts) >= 3:
            contact_info = {
                "name": parts[0],
                "phone": parts[1],
                "email": parts[2]
            }
            self.redis.update_session_field(session_id, "contact_info", json.dumps(contact_info))
            self.current_state = ConversationState.GOODBYE
            return "Thank you! Our agent will contact you shortly."
        return "Please provide: Name, Phone, Email (comma separated)"

    def _extract_property_type(self, text: str) -> Optional[str]:
        for key, value in self.property_types.items():
            if key in text.lower():
                return value
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        locations = ["i8", "dha", "gulberg", "bahria", "e11", "f11"]
        text = text.lower()
        for loc in locations:
            if loc in text:
                return loc.upper() if len(loc) <= 3 else loc.capitalize()
        return None

    def _clean_location_input(self, text: str) -> str:
        text = re.sub(r"\b(?:in|near|at|for|property|house|apartment|want|looking)\b", "", text, flags=re.IGNORECASE)
        return text.strip()