import json
import csv
from datetime import datetime
from config import Config

class LeadManager:
    def __init__(self):
        self.leads_file = "data/leads.csv"
        self._init_lead_file()
    
    def _init_lead_file(self):
        try:
            with open(self.leads_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "name", "phone", "email", 
                    "property_type", "location", "lead_score", 
                    "interested_properties", "conversation_summary"
                ])
        except FileExistsError:
            pass
    
    def save_lead(self, session_data):
        lead_score = self._calculate_lead_score(session_data)
        
        with open(self.leads_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                json.loads(session_data.get("contact_info", "{}")).get("name", ""),
                json.loads(session_data.get("contact_info", "{}")).get("phone", ""),
                json.loads(session_data.get("contact_info", "{}")).get("email", ""),
                session_data.get("property_type", ""),
                session_data.get("location", ""),
                lead_score,
                session_data.get("viewed_properties", ""),
                session_data.get("conversation_summary", "")
            ])
    
    def _calculate_lead_score(self, session_data):
        score = 0
        # Check if contact info was shared
        if session_data.get("contact_info"):
            score += Config.LEAD_SCORE_WEIGHTS['contact_shared']
        
        # Check for detailed questions
        if "details" in session_data.get("conversation_summary", "").lower():
            score += Config.LEAD_SCORE_WEIGHTS['detailed_questions']
        
        # Check for multiple properties viewed
        viewed_props = session_data.get("viewed_properties", "").split(",")
        if len(viewed_props) > 2:
            score += Config.LEAD_SCORE_WEIGHTS['multiple_properties_viewed']
        
        return score
    
    def generate_report(self):
        with open(self.leads_file, 'r') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
        
        report = {
            "total_leads": len(leads),
            "high_score_leads": len([l for l in leads if int(l['lead_score']) > 50]),
            "new_leads_last_hour": len([l for l in leads if self._is_recent(l['timestamp'])]),
            "top_locations": self._get_top_locations(leads),
            "top_property_types": self._get_top_property_types(leads)
        }
        
        return report
    
    def _is_recent(self, timestamp):
        from datetime import datetime, timedelta
        lead_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - lead_time) < timedelta(hours=1)
    
    def _get_top_locations(self, leads):
        from collections import Counter
        locations = [lead['location'] for lead in leads if lead['location']]
        return Counter(locations).most_common(3)
    
    def _get_top_property_types(self, leads):
        from collections import Counter
        types = [lead['property_type'] for lead in leads if lead['property_type']]
        return Counter(types).most_common(3)