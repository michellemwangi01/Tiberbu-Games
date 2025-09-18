import frappe


# def get_context(context):
#     # This page requires admin access
#     if frappe.session.user == "Guest":
#         frappe.throw("Access Denied", frappe.PermissionError)

#     context.no_cache = 1
#     context.show_sidebar = False

#     # Initialize all variables with safe defaults first
#     context.questions = []
#     context.existing_participants = []
#     context.settings = {"voting_timer_seconds": 30, "grace_period_seconds": 3}

#     # Get available questions with safe field access
#     try:
#         questions = frappe.db.get_all(
#             "Game Question", fields=["name", "question_text"], order_by="creation DESC"
#         )

#         # Convert to simple dict format to avoid JSON serialization issues
#         for q in questions:
#             question_dict = {
#                 "name": str(q.name),
#                 "question_text": str(q.question_text),
#                 "for_leadership_track": 0,
#                 "for_backend_track": 0,
#                 "for_frontend_track": 0,
#                 "for_custom_sessions": 0,
#             }

#             # Try to get session assignment fields if they exist
#             try:
#                 doc = frappe.get_doc("Game Question", q.name)
#                 question_dict["for_leadership_track"] = int(
#                     getattr(doc, "for_leadership_track", 0)
#                 )
#                 question_dict["for_backend_track"] = int(
#                     getattr(doc, "for_backend_track", 0)
#                 )
#                 question_dict["for_frontend_track"] = int(
#                     getattr(doc, "for_frontend_track", 0)
#                 )
#                 question_dict["for_custom_sessions"] = int(
#                     getattr(doc, "for_custom_sessions", 0)
#                 )
#             except:
#                 pass

#             context.questions.append(question_dict)
#     except Exception as e:
#         frappe.log_error(f"Error loading questions: {str(e)}")
#         # Keep the empty list we initialized above

#     # Get existing participants (from old Game Participant for migration)
#     try:
#         participants = frappe.db.get_all(
#             "Game Participant",
#             fields=["participant_name"],
#             order_by="participant_name ASC",
#         )
#         context.existing_participants = [
#             {"participant_name": str(p.participant_name)} for p in participants
#         ]
#     except Exception as e:
#         frappe.log_error(f"Error loading participants: {str(e)}")
#         # Keep the empty list we initialized above

#     frappe.log_error(f"Questions data: {context.questions}")
#     return context


# def get_context(context):
#     if frappe.session.user == "Guest":
#         frappe.throw("Access Denied", frappe.PermissionError)

#     context.no_cache = 1
#     context.show_sidebar = False

#     # Initialize with safe defaults
#     context.questions = []
#     context.existing_participants = []

#     # Get available questions safely
#     try:
#         questions = frappe.db.get_all(
#             "Game Question",
#             fields=[
#                 "name",
#                 "question_text",
#                 "for_leadership_track",
#                 "for_backend_track",
#                 "for_frontend_track",
#                 "for_custom_sessions",
#             ],
#             order_by="creation DESC",
#         )

#         # Ensure all fields have values
#         for q in questions:
#             question_dict = {
#                 "name": str(q.name) if q.name else "",
#                 "question_text": str(q.question_text) if q.question_text else "",
#                 "for_leadership_track": (
#                     int(q.for_leadership_track) if q.for_leadership_track else 0
#                 ),
#                 "for_backend_track": (
#                     int(q.for_backend_track) if q.for_backend_track else 0
#                 ),
#                 "for_frontend_track": (
#                     int(q.for_frontend_track) if q.for_frontend_track else 0
#                 ),
#                 "for_custom_sessions": (
#                     int(q.for_custom_sessions) if q.for_custom_sessions else 0
#                 ),
#             }
#             context.questions.append(question_dict)

#     except Exception as e:
#         frappe.log_error(f"Error loading questions: {str(e)}")
#         context.questions = []

#     # Get existing participants safely
#     try:
#         participants = frappe.db.get_all(
#             "Game Participant",
#             fields=["participant_name"],
#             order_by="participant_name ASC",
#         )
#         context.existing_participants = [
#             {"participant_name": str(p.participant_name) if p.participant_name else ""}
#             for p in participants
#         ]
#     except Exception as e:
#         frappe.log_error(f"Error loading participants: {str(e)}")
#         context.existing_participants = []

#     return context


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Access Denied", frappe.PermissionError)

    context.no_cache = 1
    context.show_sidebar = False
    context.questions = []
    context.existing_participants = []

    try:
        # Get questions from Game Settings JSON field
        settings = frappe.get_single("Game Settings")
        questions_json = settings.get("questions_json", "[]")

        if questions_json:
            import json

            context.questions = json.loads(questions_json)
        else:
            # Fallback: provide sample questions structure
            context.questions = [
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

    except Exception as e:
        frappe.log_error(
            f"Error loading questions from JSON: {str(e)}", "Question Loading Error"
        )
        context.questions = []

    # Get existing participants for migration
    try:
        participants = frappe.db.get_all(
            "Game Participant",
            fields=["participant_name"],
            order_by="participant_name ASC",
        )
        context.existing_participants = [
            {"participant_name": str(p.participant_name)} for p in participants
        ]
    except Exception as e:
        frappe.log_error(f"Error loading participants: {str(e)}")
        context.existing_participants = []

    return context
