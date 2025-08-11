import streamlit as st
from database.redis_connector import RedisConnector
from database.qdrant_connector import QdrantConnector
from chatbot.conversation_flow import ConversationFlow
from chatbot.lead_management import LeadManager
from utils.embeddings import get_embedding
import json
import time
from datetime import datetime
from config import Config

class RealEstateChatbot:
    def __init__(self):
        self.redis = RedisConnector()
        self.qdrant = QdrantConnector()
        self.flow = ConversationFlow(self.redis)
        self.lead_manager = LeadManager()

    def process_user_input(self, session_id: str, user_input: str) -> str:
        # Get or create session
        session = self.redis.get_session(session_id)
        if not session:
            session = {
                "session_id": session_id,
                "conversation_history": json.dumps([]),
                "property_type": "",
                "location": "",
                "contact_info": "",
                "viewed_properties": "[]",
                "conversation_summary": ""
            }
            self.redis.store_session(session_id, session)

        # Process through conversation flow
        flow_response = self.flow.update_state(session_id, user_input)
        
        # Handle system signals
        if flow_response == "SEARCH_PROPERTIES":
            return self._handle_property_search(session_id)
        elif flow_response == "PROPERTY_DETAILS":
            return self._handle_property_details(session_id)
        elif flow_response == "REQUEST_CONTACT":
            return "Please share your contact details:\nName, Phone, Email (comma separated)"
        elif flow_response == "LEAD_SCORING":
            return self._handle_lead_scoring(session_id)
        else:
            return flow_response or "I didn't understand that. Could you please rephrase?"

    def _handle_property_search(self, session_id: str) -> str:
        session = self.redis.get_session(session_id)
        property_type = session.get("property_type", "")
        location = session.get("location", "")

        # Get embedding for semantic search
        query = f"{property_type} in {location}"
        query_embedding = get_embedding(query)

        # Search Qdrant
        results = self.qdrant.search_properties(
            query_embedding,
            filters={
                "must": [
                    {"key": "type", "match": {"value": property_type}},
                    {"key": "location", "match": {"value": location}}
                ]
            },
            limit=3
        )

        # Format results
        properties = []
        property_ids = []
        for result in results:
            properties.append({
                "id": result.id,
                "title": result.payload['title'],
                "price": result.payload['price'],
                "type": result.payload['type'],
                "bedrooms": result.payload['bedrooms'],
                "location": result.payload['location']
            })
            property_ids.append(result.id)

        # Update session
        self.redis.update_session_field(session_id, "viewed_properties", json.dumps(property_ids))

        # Generate response
        if not properties:
            return "No properties found matching your criteria. Please try different search terms."
            
        response = "Here are some properties I found:\n\n"
        for i, prop in enumerate(properties, 1):
            response += f"{i}. {prop['title']}\n"
            response += f"   Price: PKR {prop['price']:,}\n"
            response += f"   Type: {prop['type']}\n"
            response += f"   Bedrooms: {prop['bedrooms']}\n"
            response += f"   Location: {prop['location']}\n\n"
        
        response += "Would you like more details about any of these?"
        return response

    def _handle_property_details(self, session_id: str) -> str:
        session = self.redis.get_session(session_id)
        property_ids = json.loads(session.get("viewed_properties", "[]"))

        # Get full details from Qdrant
        detailed_properties = []
        for prop_id in property_ids:
            result = self.qdrant.client.retrieve(
                collection_name=Config.QDRANT_COLLECTION,
                ids=[prop_id]
            )
            if result:
                detailed_properties.append(result[0].payload)

        # Format detailed response
        if not detailed_properties:
            return "I couldn't find the property details. Please try again."
        
        response = "Here are the complete details:\n\n"
        for prop in detailed_properties:
            response += f"====== {prop['title']} ======\n"
            response += f"Type: {prop['type']}\n"
            response += f"Price: PKR {prop['price']:,}\n"
            response += f"Bedrooms: {prop['bedrooms']}\n"
            response += f"Area: {prop.get('area', 'N/A')} sq.yd\n"
            response += f"Location: {prop['location']}\n"
            response += f"Features: {prop.get('features', 'N/A')}\n"
            response += f"Description: {prop['description']}\n"
            response += f"Contact: {prop.get('contact', 'N/A')}\n"
            response += "--------------------------\n\n"
        
        response += "Would you like me to connect you with the seller?"
        return response

    def _handle_lead_scoring(self, session_id: str) -> str:
        session = self.redis.get_session(session_id)
        self.lead_manager.save_lead(session)
        return "Thank you! Our team will contact you shortly."

def display_conversation_memory(session_data):
    st.sidebar.title("Conversation Context")
    if session_data:
        st.sidebar.subheader("Current Search")
        st.sidebar.write(f"**Property Type:** {session_data.get('property_type', 'Not specified')}")
        st.sidebar.write(f"**Location:** {session_data.get('location', 'Not specified')}")
        
        if session_data.get('contact_info'):
            st.sidebar.subheader("Contact Information")
            try:
                contact = json.loads(session_data['contact_info'])
                st.sidebar.write(f"Name: {contact.get('name', '')}")
                st.sidebar.write(f"Phone: {contact.get('phone', '')}")
            except:
                st.sidebar.write("Contact info saved")

def main():
    st.set_page_config(
        page_title="Real Estate Lead Gen Chatbot",
        page_icon="🏠",
        layout="wide"
    )

    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = RealEstateChatbot()

    # Create session ID
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"user_{int(time.time())}"

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Ask me about properties in your area!"})

    # Display sidebar with memory
    session_data = st.session_state.chatbot.redis.get_session(st.session_state.session_id)
    display_conversation_memory(session_data)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get chatbot response
        response = st.session_state.chatbot.process_user_input(
            st.session_state.session_id,
            prompt
        )
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the UI
        st.rerun()

if __name__ == "__main__":
    main()