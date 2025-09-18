# Copyright (c) 2025, Fun and Games and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GameVote(Document):
	def validate(self):
		# Check for duplicate votes from same IP for same question
		existing_vote = frappe.db.exists("Game Vote", {
			"question": self.question,
			"voter_ip": self.voter_ip
		})
		
		if existing_vote and existing_vote != self.name:
			frappe.throw("You have already voted for this question!")
