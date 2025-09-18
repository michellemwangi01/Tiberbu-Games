#!/usr/bin/env python3
"""
Create Team-Specific Sessions for Fun and Games

This script creates predefined sessions for different teams with their relevant questions.
"""

import frappe
import json


def create_team_sessions():
    """Create team-specific sessions with relevant questions"""
    
    # Define the sessions to create
    sessions_config = [
        {
            "session_name": "Backend & Security & DevOps Team Session",
            "team_group": "Backend Track", 
            "description": "Team building session for Backend, Security, and DevOps teams",
            "question_filters": {
                "for_backend_track": 1
            }
        },
        {
            "session_name": "Frontend & UI/UX Team Session", 
            "team_group": "Frontend Track",
            "description": "Team building session for Frontend and UI/UX teams",
            "question_filters": {
                "for_frontend_track": 1
            }
        },
        {
            "session_name": "Management & Scrum Team Session",
            "team_group": "Leadership Track", 
            "description": "Team building session for Management and Scrum teams",
            "question_filters": {
                "for_leadership_track": 1
            }
        }
    ]
    
    # Sample participants for each session
    participants_config = {
        "Backend Track": [
            {"participant_name": "Alex Backend", "team": "Backend", "display_order": 1},
            {"participant_name": "Sarah Security", "team": "Security", "display_order": 2}, 
            {"participant_name": "Mike DevOps", "team": "DevOps", "display_order": 3},
            {"participant_name": "Lisa Database", "team": "Backend", "display_order": 4}
        ],
        "Frontend Track": [
            {"participant_name": "Emma Frontend", "team": "Frontend", "display_order": 1},
            {"participant_name": "David UI/UX", "team": "UI/UX", "display_order": 2},
            {"participant_name": "Sophie Designer", "team": "UI/UX", "display_order": 3},
            {"participant_name": "Ryan React", "team": "Frontend", "display_order": 4}
        ],
        "Leadership Track": [
            {"participant_name": "Jennifer Manager", "team": "Management", "display_order": 1},
            {"participant_name": "Tom Scrum Master", "team": "Scrum", "display_order": 2},
            {"participant_name": "Maria Product Owner", "team": "Management", "display_order": 3},
            {"participant_name": "Chris Team Lead", "team": "Management", "display_order": 4}
        ]
    }
    
    created_sessions = []
    
    for session_config in sessions_config:
        try:
            print(f"\n🚀 Creating session: {session_config['session_name']}")
            
            # Get questions for this session based on filters
            questions = get_questions_for_session(session_config['question_filters'])
            print(f"   📝 Found {len(questions)} relevant questions")
            
            if not questions:
                print(f"   ⚠️  No questions found for {session_config['session_name']}")
                continue
            
            # Get participants for this team group
            participants = participants_config.get(session_config['team_group'], [])
            
            # Create the session using the existing API
            result = create_session_with_api(
                session_config['session_name'],
                session_config['team_group'], 
                session_config['description'],
                questions[:10],  # Limit to first 10 questions
                participants
            )
            
            if result.get('success'):
                created_sessions.append({
                    'name': session_config['session_name'],
                    'id': result.get('session_id'),
                    'questions_count': len(questions[:10])
                })
                print(f"   ✅ Created session: {result.get('session_id')}")
            else:
                print(f"   ❌ Failed to create session: {result.get('message')}")
                
        except Exception as e:
            print(f"   ❌ Error creating session {session_config['session_name']}: {str(e)}")
    
    print(f"\n🎉 Session creation completed!")
    print(f"   📊 Created {len(created_sessions)} sessions:")
    for session in created_sessions:
        print(f"      • {session['name']} ({session['questions_count']} questions)")
    
    return created_sessions


def get_questions_for_session(filters):
    """Get questions that match the session filters"""
    
    # Build the WHERE clause
    where_conditions = []
    for field, value in filters.items():
        where_conditions.append(f"{field} = {value}")
    
    where_clause = " AND ".join(where_conditions)
    
    # Get questions from database
    questions = frappe.db.sql(f"""
        SELECT name, question_text, category
        FROM `tabGame Question` 
        WHERE {where_clause} AND is_active = 1
        ORDER BY category, question_text
    """, as_dict=True)
    
    return questions


def create_session_with_api(session_name, team_group, description, questions, participants):
    """Create session using the existing API"""
    
    # Format questions for API
    question_ids = [q['name'] for q in questions]
    
    # Use the existing create_session API
    from fun_and_games.fun_and_games.api import create_session
    
    return create_session(
        session_name=session_name,
        team_group=team_group, 
        description=description,
        questions=question_ids,
        participants=participants
    )


if __name__ == "__main__":
    # Initialize Frappe
    try:
        if not frappe.db:
            frappe.init()
            frappe.connect()
    except:
        print("❌ Error: Could not connect to Frappe")
        exit(1)
    
    create_team_sessions()
