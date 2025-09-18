#!/usr/bin/env python3
"""
Create Simple Team Sessions
"""

import frappe


def create_simple_sessions():
    """Create team sessions with questions"""

    # Get questions for each track using SQL
    backend_questions = frappe.db.sql(
        """
        SELECT name, question_text
        FROM `tabGame Question`
        WHERE for_backend_track = 1 AND is_active = 1
        LIMIT 15
    """,
        as_dict=True,
    )

    frontend_questions = frappe.db.sql(
        """
        SELECT name, question_text
        FROM `tabGame Question`
        WHERE for_frontend_track = 1 AND is_active = 1
        LIMIT 15
    """,
        as_dict=True,
    )

    leadership_questions = frappe.db.sql(
        """
        SELECT name, question_text
        FROM `tabGame Question`
        WHERE for_leadership_track = 1 AND is_active = 1
        LIMIT 15
    """,
        as_dict=True,
    )

    print(f"📊 Found questions:")
    print(f"   Backend: {len(backend_questions)}")
    print(f"   Frontend: {len(frontend_questions)}")
    print(f"   Leadership: {len(leadership_questions)}")

    # Create sessions
    sessions = [
        {
            "session_name": "Backend Security DevOps Session",
            "team_group": "Backend Track",
            "description": "Session for Backend, Security, and DevOps teams",
            "questions": backend_questions,
            "participants": [
                {"participant_name": "Alex Backend", "team": "Backend"},
                {"participant_name": "Sarah Security", "team": "Security"},
                {"participant_name": "Mike DevOps", "team": "DevOps"},
            ],
        },
        {
            "session_name": "Frontend UI UX Session",
            "team_group": "Frontend Track",
            "description": "Session for Frontend and UI/UX teams",
            "questions": frontend_questions,
            "participants": [
                {"participant_name": "Emma Frontend", "team": "Frontend"},
                {"participant_name": "David UI/UX", "team": "UI/UX"},
                {"participant_name": "Sophie Designer", "team": "UI/UX"},
            ],
        },
        {
            "session_name": "Management Scrum Session",
            "team_group": "Leadership Track",
            "description": "Session for Management and Scrum teams",
            "questions": leadership_questions,
            "participants": [
                {"participant_name": "Jennifer Manager", "team": "Management"},
                {"participant_name": "Tom Scrum Master", "team": "Scrum"},
                {"participant_name": "Maria Product Owner", "team": "Management"},
            ],
        },
    ]

    created_count = 0

    for session_config in sessions:
        if not session_config["questions"]:
            print(f"⚠️  Skipping {session_config['session_name']} - no questions")
            continue

        try:
            # Create session document
            session_doc = frappe.get_doc(
                {
                    "doctype": "Game Session",
                    "session_name": session_config["session_name"],
                    "team_group": session_config["team_group"],
                    "description": session_config["description"],
                    "status": "Draft",
                }
            )
            session_doc.insert(ignore_permissions=True)

            # Add questions to session
            for i, question in enumerate(session_config["questions"]):
                session_question = frappe.get_doc(
                    {
                        "doctype": "Session Question",
                        "session": session_doc.name,
                        "question": question["name"],
                        "question_order": i + 1,
                    }
                )
                session_question.insert(ignore_permissions=True)

            # Add participants to session
            for i, participant in enumerate(session_config["participants"]):
                session_participant = frappe.get_doc(
                    {
                        "doctype": "Session Participant",
                        "session": session_doc.name,
                        "participant_name": participant["participant_name"],
                        "team": participant["team"],
                        "display_order": i + 1,
                    }
                )
                session_participant.insert(ignore_permissions=True)

            print(
                f"✅ Created: {session_config['session_name']} ({len(session_config['questions'])} questions)"
            )
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating {session_config['session_name']}: {str(e)}")

    frappe.db.commit()
    print(f"\n🎉 Created {created_count} sessions successfully!")


if __name__ == "__main__":
    try:
        if not frappe.db:
            frappe.init()
            frappe.connect()
    except:
        print("❌ Error: Could not connect to Frappe")
        exit(1)

    create_simple_sessions()
