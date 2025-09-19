#!/usr/bin/env python3
"""
Production Session Creation Script

Creates 3 pre-configured team sessions with participants and questions.
Run via: bench --site [site-name] execute fun_and_games.create_production_sessions.create_team_sessions
"""

import frappe


def create_team_sessions():
    """Create 3 team sessions with participants and questions - FLEXIBLE based on question flags"""

    print("🚀 Creating team sessions...")

    # Get questions for each track dynamically
    backend_questions = frappe.db.get_all(
        "Game Question",
        filters={"for_backend_track": 1, "is_active": 1},
        fields=["name"],
        order_by="creation",
    )

    frontend_questions = frappe.db.get_all(
        "Game Question",
        filters={"for_frontend_track": 1, "is_active": 1},
        fields=["name"],
        order_by="creation",
    )

    leadership_questions = frappe.db.get_all(
        "Game Question",
        filters={"for_leadership_track": 1, "is_active": 1},
        fields=["name"],
        order_by="creation",
    )

    print(
        f"📊 Found {len(backend_questions)} backend, {len(frontend_questions)} frontend, {len(leadership_questions)} leadership questions"
    )
    print("💡 Sessions will include ALL questions with matching flags (no limit)")

    # Session configurations
    sessions_config = [
        {
            "session_name": "Backend Security DevOps Session",
            "team_group": "Backend Track",
            "description": "Session for Backend, Security, and DevOps teams",
            "questions": [q["name"] for q in backend_questions],
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
            "questions": [q["name"] for q in frontend_questions],
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
            "questions": [q["name"] for q in leadership_questions],
            "participants": [
                {"participant_name": "Jennifer Manager", "team": "Management"},
                {"participant_name": "Tom Scrum Master", "team": "Scrum"},
                {"participant_name": "Maria Product Owner", "team": "Management"},
            ],
        },
    ]

    created_sessions = []

    for session_config in sessions_config:
        try:
            print(f"📝 Creating session: {session_config['session_name']}")

            # Create session
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
            for i, question_id in enumerate(session_config["questions"]):
                session_question = frappe.get_doc(
                    {
                        "doctype": "Session Question",
                        "session": session_doc.name,
                        "question": question_id,
                        "display_order": i + 1,
                        "is_completed": 0,
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

            created_sessions.append(session_doc.name)
            print(
                f"✅ Created session: {session_config['session_name']} ({session_doc.name})"
            )

        except Exception as e:
            print(
                f"❌ Error creating session {session_config['session_name']}: {str(e)}"
            )
            continue

    frappe.db.commit()

    print(f"\n🎉 Successfully created {len(created_sessions)} sessions!")
    print("Sessions created:")
    for session_id in created_sessions:
        session = frappe.get_doc("Game Session", session_id)
        print(f"  - {session.session_name} ({session_id})")

    return {"success": True, "sessions_created": len(created_sessions)}


def create_custom_session(session_name, description, participant_list):
    """
    Create a custom session with any questions (all questions have for_custom_sessions=1)

    Usage:
    participants = [
        {"participant_name": "John Doe", "team": "Backend"},
        {"participant_name": "Jane Smith", "team": "Frontend"}
    ]
    create_custom_session("My Custom Session", "Custom team session", participants)
    """

    print(f"🎨 Creating custom session: {session_name}")

    # Get ALL questions that are available for custom sessions
    custom_questions = frappe.db.get_all(
        "Game Question",
        filters={"for_custom_sessions": 1, "is_active": 1},
        fields=["name"],
        order_by="creation",
    )

    print(f"📊 Found {len(custom_questions)} questions available for custom sessions")

    try:
        # Create session
        session_doc = frappe.get_doc(
            {
                "doctype": "Game Session",
                "session_name": session_name,
                "team_group": "Custom",
                "description": description,
                "status": "Draft",
            }
        )
        session_doc.insert(ignore_permissions=True)

        # Add ALL available questions to session
        for i, question in enumerate(custom_questions):
            session_question = frappe.get_doc(
                {
                    "doctype": "Session Question",
                    "session": session_doc.name,
                    "question": question["name"],
                    "display_order": i + 1,
                    "is_completed": 0,
                }
            )
            session_question.insert(ignore_permissions=True)

        # Add participants to session
        for i, participant in enumerate(participant_list):
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

        frappe.db.commit()

        print(f"✅ Created custom session: {session_name} ({session_doc.name})")
        print(f"   - {len(custom_questions)} questions added")
        print(f"   - {len(participant_list)} participants added")

        return {"success": True, "session_id": session_doc.name}

    except Exception as e:
        print(f"❌ Error creating custom session: {str(e)}")
        return {"success": False, "error": str(e)}


def verify_setup():
    """Verify the complete setup"""

    print("\n🔍 Verifying setup...")

    # Check questions by track
    total_questions = frappe.db.count("Game Question")
    backend_count = frappe.db.count(
        "Game Question", {"for_backend_track": 1, "is_active": 1}
    )
    frontend_count = frappe.db.count(
        "Game Question", {"for_frontend_track": 1, "is_active": 1}
    )
    leadership_count = frappe.db.count(
        "Game Question", {"for_leadership_track": 1, "is_active": 1}
    )
    custom_count = frappe.db.count(
        "Game Question", {"for_custom_sessions": 1, "is_active": 1}
    )

    print(f"📊 Questions: {total_questions} total")
    print(f"   - Backend track: {backend_count}")
    print(f"   - Frontend track: {frontend_count}")
    print(f"   - Leadership track: {leadership_count}")
    print(f"   - Custom sessions: {custom_count}")

    # Check sessions with question counts
    sessions = frappe.db.get_all(
        "Game Session", fields=["name", "session_name", "status"]
    )
    print(f"\n🎮 Sessions: {len(sessions)}")
    for session in sessions:
        question_count = frappe.db.count("Session Question", {"session": session.name})
        participant_count = frappe.db.count(
            "Session Participant", {"session": session.name}
        )
        print(f"  - {session.session_name} ({session.status})")
        print(f"    └── {question_count} questions, {participant_count} participants")

    # Check participants by team
    participants = frappe.db.get_all(
        "Session Participant", fields=["participant_name", "team"]
    )
    print(f"\n👥 Participants: {len(participants)}")
    teams = {}
    for participant in participants:
        if participant.team not in teams:
            teams[participant.team] = []
        teams[participant.team].append(participant.participant_name)

    for team, members in teams.items():
        print(f"  - {team}: {', '.join(members)}")

    print(f"\n✅ Setup verification complete!")
    print(
        f"💡 All questions have for_custom_sessions=1, so they can be used in any custom session"
    )


if __name__ == "__main__":
    create_team_sessions()
    verify_setup()
