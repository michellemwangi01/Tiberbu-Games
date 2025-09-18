#!/usr/bin/env python3
"""
Example: How to create a session with participants using the API
"""

import requests
import json

# Example API call to create session with participants
def create_session_with_participants():
    url = "http://your-site/api/method/fun_and_games.fun_and_games.api.create_session"
    
    # Session data with participants
    session_data = {
        "session_name": "My Team Session",
        "team_group": "Custom",
        "description": "Fun team building session",
        "questions": ["GQ-2025-00001", "GQ-2025-00002"],  # Question IDs
        "participants": [
            {
                "name": "John Doe",
                "team": "Backend"
            },
            {
                "name": "Jane Smith", 
                "team": "Frontend"
            },
            {
                "name": "Bob Wilson",
                "team": "UI/UX"
            },
            {
                "name": "Alice Johnson",
                "team": "Management"
            }
        ]
    }
    
    response = requests.post(url, json=session_data)
    return response.json()

# Example using Frappe framework directly
def create_session_frappe():
    import frappe
    
    # Create session document
    session_doc = frappe.get_doc({
        "doctype": "Game Session",
        "session_name": "Backend Team Session",
        "team_group": "Backend Track",
        "description": "Backend team building",
        "status": "Draft"
    })
    session_doc.insert()
    
    # Add participants
    participants = [
        {"name": "Alex Backend", "team": "Backend"},
        {"name": "Sarah Security", "team": "Security"},
        {"name": "Mike DevOps", "team": "DevOps"}
    ]
    
    for i, participant in enumerate(participants):
        session_participant = frappe.get_doc({
            "doctype": "Session Participant",
            "session": session_doc.name,
            "participant_name": participant["name"],
            "team": participant["team"],
            "display_order": i + 1
        })
        session_participant.insert()
    
    frappe.db.commit()
    return session_doc.name

if __name__ == "__main__":
    print("Example session creation with participants")
    print("See the functions above for implementation details")
