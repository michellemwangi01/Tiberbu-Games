# Copyright (c) 2025, Fun and Games and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def get_questions_from_settings():
    """Get questions from Game Settings JSON field"""
    try:
        import json

        settings = frappe.get_single("Game Settings")
        questions_json = settings.get("questions_json", "[]")

        if questions_json:
            questions = json.loads(questions_json)
        else:
            # Fallback sample questions
            questions = [
                {
                    "name": "Q1",
                    "question_text": "Who is most likely to work late?",
                    "for_leadership_track": 1,
                    "for_backend_track": 1,
                    "for_frontend_track": 0,
                    "for_custom_sessions": 0,
                },
                {
                    "name": "Q2",
                    "question_text": "Who is most likely to debug on weekends?",
                    "for_leadership_track": 0,
                    "for_backend_track": 1,
                    "for_frontend_track": 1,
                    "for_custom_sessions": 0,
                },
            ]

        return {"questions": questions}

    except Exception as e:
        frappe.log_error(f"Error getting questions from settings: {str(e)}")
        return {"questions": []}


@frappe.whitelist(allow_guest=True)
def get_active_session():
    """Returns current active session with question and participants"""
    try:
        # Get active session
        active_session = frappe.db.get_value(
            "Game Session",
            {"status": "Active"},
            [
                "name",
                "session_name",
                "current_question",
                "question_start_time",
                "voting_deadline",
            ],
            as_dict=True,
        )

        if not active_session:
            return {"success": False, "message": "No active session found"}

        # Get current question details if exists
        question_data = None
        if active_session.current_question:
            question_data = frappe.db.get_value(
                "Game Question",
                active_session.current_question,
                ["name", "question_text"],
                as_dict=True,
            )

        # Get session participants
        participants = frappe.db.get_all(
            "Session Participant",
            filters={"session": active_session.name},
            fields=["name", "participant_name", "team"],
            order_by="display_order ASC, participant_name ASC",
        )

        # Calculate time remaining
        time_remaining = 0
        voting_open = False
        if active_session.voting_deadline:
            remaining_seconds = (
                active_session.voting_deadline - now_datetime()
            ).total_seconds()
            time_remaining = max(0, int(remaining_seconds))
            voting_open = time_remaining > 0

        return {
            "success": True,
            "session": active_session,
            "question": question_data,
            "participants": participants,
            "time_remaining": time_remaining,
            "voting_open": voting_open,
        }

    except Exception as e:
        frappe.log_error(f"Error in get_active_session: {str(e)}")
        return {
            "success": False,
            "message": "An error occurred while fetching the session",
        }


@frappe.whitelist(allow_guest=True)
def submit_vote(participant):
    """Saves vote for current active session, prevents duplicates by IP"""
    try:
        # Get active session
        active_session = frappe.db.get_value(
            "Game Session",
            {"status": "Active"},
            ["name", "current_question", "voting_deadline"],
            as_dict=True,
        )

        if not active_session:
            return {"success": False, "message": "No active session found"}

        if not active_session.current_question:
            return {"success": False, "message": "No active question in session"}

        # Check if voting is still open (with 3-second grace period)
        if active_session.voting_deadline:
            grace_period = 3  # seconds
            deadline_with_grace = active_session.voting_deadline.replace(
                second=active_session.voting_deadline.second + grace_period
            )
            if now_datetime() > deadline_with_grace:
                return {"success": False, "message": "Voting time has expired"}

        # Get client IP with user agent for better uniqueness
        voter_ip = frappe.local.request_ip or "unknown"
        user_agent = frappe.get_request_header("User-Agent") or "unknown"
        voter_identifier = f"{voter_ip}_{hash(user_agent) % 10000}"

        # Check if user already voted for this question in this session
        existing_vote = frappe.db.exists(
            "Game Vote",
            {
                "session": active_session.name,
                "question": active_session.current_question,
                "voter_ip": voter_identifier,
            },
        )

        if existing_vote:
            return {
                "success": False,
                "message": "You have already voted for this question!",
            }

        # Validate participant exists in this session
        if not frappe.db.exists(
            "Session Participant", {"name": participant, "session": active_session.name}
        ):
            return {"success": False, "message": "Invalid participant for this session"}

        # Create vote
        vote_doc = frappe.get_doc(
            {
                "doctype": "Game Vote",
                "session": active_session.name,
                "question": active_session.current_question,
                "participant": participant,
                "voter_ip": voter_identifier,
            }
        )
        vote_doc.insert(ignore_permissions=True)

        return {"success": True, "message": "Vote submitted successfully!"}

    except Exception as e:
        frappe.log_error(f"Error in submit_vote: {str(e)}")
        return {
            "success": False,
            "message": "An error occurred while submitting your vote",
        }


@frappe.whitelist(allow_guest=True)
def get_results():
    """Returns vote tallies for active session's current question"""
    try:
        # Get active session
        active_session = frappe.db.get_value(
            "Game Session",
            {"status": "Active"},
            ["name", "session_name", "current_question"],
            as_dict=True,
        )

        if not active_session:
            return {"success": False, "message": "No active session found"}

        if not active_session.current_question:
            return {"success": False, "message": "No active question in session"}

        # Get question details
        question_data = frappe.db.get_value(
            "Game Question",
            active_session.current_question,
            ["name", "question_text"],
            as_dict=True,
        )

        # Get vote counts for each participant in this session
        vote_counts = frappe.db.sql(
            """
			SELECT
				sp.name,
				sp.participant_name,
				sp.team,
				COUNT(gv.name) as vote_count
			FROM `tabSession Participant` sp
			LEFT JOIN `tabGame Vote` gv ON sp.name = gv.participant
				AND gv.session = %s AND gv.question = %s
			WHERE sp.session = %s
			GROUP BY sp.name, sp.participant_name, sp.team
			ORDER BY sp.display_order ASC, sp.participant_name ASC
		""",
            (active_session.name, active_session.current_question, active_session.name),
            as_dict=True,
        )

        # Calculate total votes
        total_votes = sum(row.vote_count for row in vote_counts)

        return {
            "success": True,
            "session": active_session,
            "question": question_data,
            "results": vote_counts,
            "total_votes": total_votes,
        }

    except Exception as e:
        frappe.log_error(f"Error in get_results: {str(e)}")
        return {"success": False, "message": "An error occurred while fetching results"}


@frappe.whitelist(allow_guest=True)
def activate_session_question(session_id, question_id):
    """Admin method to activate a question in a session with timer"""
    try:
        # Validate session exists and is active
        session_doc = frappe.get_doc("Game Session", session_id)
        if session_doc.status != "Active":
            return {"success": False, "message": "Session is not active"}

        # Validate question exists and is assigned to this session
        question_assigned = frappe.db.exists(
            "Session Question", {"session": session_id, "question": question_id}
        )

        if not question_assigned:
            return {
                "success": False,
                "message": "Question not assigned to this session",
            }

        # Get timer settings
        settings = frappe.get_single("Game Settings")
        timer_seconds = settings.voting_timer_seconds or 30

        # Activate question with timer
        result = session_doc.activate_question(question_id, timer_seconds)

        return {
            "success": True,
            "message": "Question activated successfully",
            "timer_seconds": timer_seconds,
            "voting_deadline": result["voting_deadline"],
            "question_id": question_id,
        }

    except Exception as e:
        frappe.log_error(f"Error in activate_session_question: {str(e)}")
        return {
            "success": False,
            "message": "An error occurred while activating the question",
        }


@frappe.whitelist(allow_guest=True)
def reset_session_votes(session_id, question_id=None):
    """Reset votes for a session - either specific question or all questions"""
    try:
        # Validate session exists
        if not frappe.db.exists("Game Session", session_id):
            return {"success": False, "message": "Session not found"}

        if question_id:
            # Reset votes for specific question in session
            frappe.db.delete(
                "Game Vote", {"session": session_id, "question": question_id}
            )
            message = f"Votes reset for question in session"
        else:
            # Reset all votes for session
            frappe.db.delete("Game Vote", {"session": session_id})
            message = "All votes have been reset for this session"

        frappe.db.commit()
        return {"success": True, "message": message}

    except Exception as e:
        frappe.log_error(f"Error in reset_session_votes: {str(e)}")
        return {"success": False, "message": "An error occurred while resetting votes"}


@frappe.whitelist()
def get_session_list():
    """Get list of all sessions for admin"""
    try:
        sessions = frappe.db.get_all(
            "Game Session",
            fields=["name", "session_name", "team_group", "status", "session_date"],
            order_by="creation DESC",
        )
        return {"success": True, "sessions": sessions}
    except Exception as e:
        frappe.log_error(f"Error in get_session_list: {str(e)}")
        return {"success": False, "message": "Error fetching sessions"}


@frappe.whitelist(allow_guest=True)
def start_session(session_id):
    """Start a session (set as active)"""
    try:
        # Deactivate all other sessions
        frappe.db.sql(
            "UPDATE `tabGame Session` SET status = 'Completed' WHERE status = 'Active'"
        )

        # Activate this session
        frappe.db.set_value("Game Session", session_id, "status", "Active")
        frappe.db.commit()

        return {"success": True, "message": "Session started successfully"}
    except Exception as e:
        frappe.log_error(f"Error in start_session: {str(e)}")
        return {"success": False, "message": "Error starting session"}


@frappe.whitelist(allow_guest=True)
def reactivate_session(session_id):
    """Reactivate a completed session by resetting votes and setting it as active"""
    try:
        # Deactivate all other sessions
        frappe.db.sql(
            "UPDATE `tabGame Session` SET status = 'Completed' WHERE status = 'Active'"
        )

        # Reset all votes for this session
        frappe.db.sql("DELETE FROM `tabGame Vote` WHERE session = %s", [session_id])

        # Reset question completion status for this session
        frappe.db.sql(
            "UPDATE `tabSession Question` SET is_completed = 0 WHERE session = %s",
            [session_id],
        )

        # Activate this session
        frappe.db.set_value("Game Session", session_id, "status", "Active")
        frappe.db.commit()

        return {"success": True, "message": "Session reactivated successfully"}
    except Exception as e:
        frappe.log_error(f"Error in reactivate_session: {str(e)}")
        return {"success": False, "message": "Error reactivating session"}


@frappe.whitelist(allow_guest=True)
def get_cumulative_results(session_id=None):
    """Returns cumulative vote tallies for a session or active session"""
    try:
        # If no session specified, get active session
        if not session_id:
            session_id = frappe.db.get_value(
                "Game Session", {"status": "Active"}, "name"
            )
            if not session_id:
                return {"success": False, "message": "No active session found"}

        # Get session details
        session_data = frappe.db.get_value(
            "Game Session",
            session_id,
            ["name", "session_name", "team_group"],
            as_dict=True,
        )

        # Get cumulative vote counts for each participant in this session
        cumulative_counts = frappe.db.sql(
            """
			SELECT
				sp.name,
				sp.participant_name,
				sp.team,
				COUNT(gv.name) as total_votes
			FROM `tabSession Participant` sp
			LEFT JOIN `tabGame Vote` gv ON sp.name = gv.participant AND gv.session = %s
			WHERE sp.session = %s
			GROUP BY sp.name, sp.participant_name, sp.team
			ORDER BY total_votes DESC, sp.participant_name ASC
		""",
            (session_id, session_id),
            as_dict=True,
        )

        # Get total votes for this session
        total_votes = sum(row.total_votes for row in cumulative_counts)

        # Get total number of questions that have been voted on in this session
        questions_with_votes = frappe.db.sql(
            """
			SELECT COUNT(DISTINCT question) as question_count
			FROM `tabGame Vote`
			WHERE session = %s
		""",
            (session_id,),
            as_dict=True,
        )

        questions_count = (
            questions_with_votes[0].question_count if questions_with_votes else 0
        )

        return {
            "success": True,
            "session": session_data,
            "results": cumulative_counts,
            "total_votes": total_votes,
            "questions_count": questions_count,
        }

    except Exception as e:
        frappe.log_error(f"Error in get_cumulative_results: {str(e)}")
        return {
            "success": False,
            "message": "An error occurred while fetching cumulative results",
        }


@frappe.whitelist(allow_guest=True)
def check_vote_status():
    """Check if current IP has already voted for active session's current question"""
    try:
        # Get active session
        active_session = frappe.db.get_value(
            "Game Session",
            {"status": "Active"},
            ["name", "current_question"],
            as_dict=True,
        )

        if not active_session or not active_session.current_question:
            return {"success": True, "has_voted": False}

        voter_ip = frappe.local.request_ip or "unknown"
        user_agent = frappe.get_request_header("User-Agent") or "unknown"
        voter_identifier = f"{voter_ip}_{hash(user_agent) % 10000}"

        existing_vote = frappe.db.get_value(
            "Game Vote",
            {
                "session": active_session.name,
                "question": active_session.current_question,
                "voter_ip": voter_identifier,
            },
            ["participant"],
        )

        if existing_vote:
            return {
                "success": True,
                "has_voted": True,
                "voted_participant": existing_vote,
            }
        else:
            return {"success": True, "has_voted": False}

    except Exception as e:
        frappe.log_error(f"Error in check_vote_status: {str(e)}")
        return {
            "success": False,
            "message": "An error occurred while checking vote status",
        }


@frappe.whitelist(allow_guest=True)
def get_session_questions(session_id):
    """Get questions assigned to a session"""
    try:
        questions = frappe.db.sql(
            """
            SELECT sq.name, sq.question_order, sq.is_completed,
                   gq.name as question_id, gq.question_text
            FROM `tabSession Question` sq
            JOIN `tabGame Question` gq ON sq.question = gq.name
            WHERE sq.session = %s
            ORDER BY sq.question_order ASC
        """,
            (session_id,),
            as_dict=True,
        )

        return {"success": True, "questions": questions}
    except Exception as e:
        frappe.log_error(f"Error in get_session_questions: {str(e)}")
        return {"success": False, "message": "Error fetching session questions"}


@frappe.whitelist()
def get_session_participants(session_id):
    """Get participants in a session"""
    try:
        participants = frappe.db.get_all(
            "Session Participant",
            filters={"session": session_id},
            fields=["name", "participant_name", "team", "display_order"],
            order_by="display_order ASC, participant_name ASC",
        )

        return {"success": True, "participants": participants}
    except Exception as e:
        frappe.log_error(f"Error in get_session_participants: {str(e)}")
        return {"success": False, "message": "Error fetching session participants"}


@frappe.whitelist(allow_guest=True)
def create_session(session_name, team_group, description, questions, participants):
    """Create a new game session with questions and participants"""
    try:
        # Create the session
        session_doc = frappe.get_doc(
            {
                "doctype": "Game Session",
                "session_name": session_name,
                "team_group": team_group,
                "description": description,
                "status": "Draft",
            }
        )
        session_doc.insert(ignore_permissions=True)

        # Add questions to session
        # First, get questions from JSON settings to create actual Game Question records if needed
        import json

        settings = frappe.get_single("Game Settings")
        questions_json = settings.get("questions_json", "[]")
        available_questions = json.loads(questions_json) if questions_json else []

        for i, question_id in enumerate(questions):
            # Find the question in JSON
            question_data = next(
                (q for q in available_questions if q["name"] == question_id), None
            )

            if question_data:
                # Create or get Game Question record
                if not frappe.db.exists("Game Question", question_id):
                    game_question = frappe.get_doc(
                        {
                            "doctype": "Game Question",
                            "name": question_id,
                            "question_text": question_data["question_text"],
                            "is_active": 1,
                            "for_leadership_track": question_data.get(
                                "for_leadership_track", 0
                            ),
                            "for_backend_track": question_data.get(
                                "for_backend_track", 0
                            ),
                            "for_frontend_track": question_data.get(
                                "for_frontend_track", 0
                            ),
                            "for_custom_sessions": question_data.get(
                                "for_custom_sessions", 0
                            ),
                        }
                    )
                    game_question.insert(ignore_permissions=True)

                # Create Session Question
                session_question = frappe.get_doc(
                    {
                        "doctype": "Session Question",
                        "session": session_doc.name,
                        "question": question_id,
                        "question_order": i + 1,
                    }
                )
                session_question.insert(ignore_permissions=True)

        # Add participants to session
        for i, participant in enumerate(participants):
            session_participant = frappe.get_doc(
                {
                    "doctype": "Session Participant",
                    "session": session_doc.name,
                    "participant_name": participant["name"],
                    "team": participant["team"],
                    "display_order": i + 1,
                }
            )
            session_participant.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "success": True,
            "message": "Session created successfully",
            "session_id": session_doc.name,
        }

    except Exception as e:
        frappe.log_error(f"Error in create_session: {str(e)}")
        return {"success": False, "message": f"Error creating session: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def import_questions_from_json(questions_json):
    """Import questions from JSON string"""
    try:
        from fun_and_games.import_questions import import_from_json_string

        # Parse and import questions
        success = import_from_json_string(questions_json)

        if success:
            return {"success": True, "message": "Questions imported successfully!"}
        else:
            return {
                "success": False,
                "message": "Failed to import questions. Check the format.",
            }

    except Exception as e:
        frappe.log_error(f"Error importing questions: {str(e)}")
        return {"success": False, "message": f"Error importing questions: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def clear_expired_question(session_id):
    """Clear expired question from session"""
    try:
        session_doc = frappe.get_doc("Game Session", session_id)

        # Check if voting has expired
        if session_doc.voting_deadline and now_datetime() > session_doc.voting_deadline:
            session_doc.current_question = None
            session_doc.question_start_time = None
            session_doc.voting_deadline = None
            session_doc.save()

            return {"success": True, "message": "Expired question cleared"}

        return {"success": False, "message": "Question has not expired yet"}

    except Exception as e:
        frappe.log_error(f"Error in clear_expired_question: {str(e)}")
        return {"success": False, "message": "Failed to clear expired question"}


@frappe.whitelist(allow_guest=True)
def reset_entire_session(session_id):
    """Reset entire session - clear all votes and current question"""
    try:
        # Delete all votes for this session
        frappe.db.sql("DELETE FROM `tabGame Vote` WHERE session = %s", (session_id,))

        # Reset session state
        session_doc = frappe.get_doc("Game Session", session_id)
        session_doc.current_question = None
        session_doc.question_start_time = None
        session_doc.voting_deadline = None
        session_doc.save()

        frappe.db.commit()

        return {"success": True, "message": "Session reset successfully"}

    except Exception as e:
        frappe.log_error(f"Error in reset_entire_session: {str(e)}")
        return {"success": False, "message": "Failed to reset session"}


@frappe.whitelist(allow_guest=True)
def update_session_participants(session_id, participants):
    """Update participants for a session"""
    try:
        # Delete existing participants
        frappe.db.sql(
            "DELETE FROM `tabSession Participant` WHERE session = %s", (session_id,)
        )

        # Add new participants
        for i, participant in enumerate(participants):
            session_participant = frappe.get_doc(
                {
                    "doctype": "Session Participant",
                    "session": session_id,
                    "participant_name": participant["name"],
                    "team": participant["team"],
                    "display_order": i + 1,
                }
            )
            session_participant.insert(ignore_permissions=True)

        frappe.db.commit()

        return {"success": True, "message": "Participants updated successfully"}

    except Exception as e:
        frappe.log_error(f"Error in update_session_participants: {str(e)}")
        return {"success": False, "message": "Failed to update participants"}
