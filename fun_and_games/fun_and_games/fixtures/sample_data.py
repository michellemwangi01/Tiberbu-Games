# Copyright (c) 2025, Fun and Games and contributors
# For license information, please see license.txt

import frappe


def create_sample_data():
	"""Create sample questions and participants for testing"""
	
	# Sample participants (typical office roles)
	participants = [
		{"participant_name": "Sarah Chen", "display_order": 1},
		{"participant_name": "Mike Rodriguez", "display_order": 2},
		{"participant_name": "Emily Johnson", "display_order": 3},
		{"participant_name": "David Kim", "display_order": 4},
		{"participant_name": "Lisa Thompson", "display_order": 5},
		{"participant_name": "Alex Patel", "display_order": 6},
	]
	
	# Create participants
	for participant_data in participants:
		if not frappe.db.exists("Game Participant", {"participant_name": participant_data["participant_name"]}):
			participant = frappe.get_doc({
				"doctype": "Game Participant",
				"participant_name": participant_data["participant_name"],
				"display_order": participant_data["display_order"]
			})
			participant.insert(ignore_permissions=True)
			print(f"Created participant: {participant_data['participant_name']}")
	
	# Sample questions
	questions = [
		"Who's most likely to stay calm when everything goes wrong?",
		"Who's the one you'd want in the room when a big negotiation is happening?",
		"Who's most likely to have the boldest idea in a strategy meeting?",
		"Who pushes the team hardest to hit deadlines?",
		"Who's most likely to notice small details everyone else misses?",
		"Who's the best at diffusing tension in a heated meeting?",
		"Who's most likely to volunteer to fix something no one else wants to touch?",
		"Who's most likely to remember everyone's birthday?",
		"Who's the first person you'd ask for help with a technical problem?",
		"Who's most likely to work late to help a teammate?",
		"Who's the best at explaining complex concepts simply?",
		"Who's most likely to suggest the team grab coffee together?",
		"Who's most likely to have the most organized workspace?",
		"Who's the best at keeping meetings on track?",
		"Who's most likely to come up with a creative solution to a problem?"
	]
	
	# Create questions
	for i, question_text in enumerate(questions):
		if not frappe.db.exists("Game Question", {"question_text": question_text}):
			question = frappe.get_doc({
				"doctype": "Game Question",
				"question_text": question_text,
				"is_active": 1 if i == 0 else 0  # Make first question active
			})
			question.insert(ignore_permissions=True)
			print(f"Created question: {question_text[:50]}...")
	
	frappe.db.commit()
	print("Sample data created successfully!")


if __name__ == "__main__":
	create_sample_data()
