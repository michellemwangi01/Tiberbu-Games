# Copyright (c) 2025, Fun and Games and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class GameSession(Document):
	def validate(self):
		# Ensure only one session is active at a time
		if self.status == "Active":
			# Deactivate all other sessions
			frappe.db.sql("""
				UPDATE `tabGame Session` 
				SET status = 'Completed' 
				WHERE name != %s AND status = 'Active'
			""", (self.name,))
			frappe.db.commit()
	
	def activate_question(self, question_id, timer_seconds=30):
		"""Activate a question for this session with timer"""
		from frappe.utils import now_datetime, add_to_date
		
		# Set current question and timing
		self.current_question = question_id
		self.question_start_time = now_datetime()
		self.voting_deadline = add_to_date(self.question_start_time, seconds=timer_seconds)
		self.save()
		
		return {
			"success": True,
			"question_start_time": self.question_start_time,
			"voting_deadline": self.voting_deadline
		}
	
	def is_voting_open(self):
		"""Check if voting is still open for current question"""
		if not self.current_question or not self.voting_deadline:
			return False
		
		from frappe.utils import now_datetime
		return now_datetime() <= self.voting_deadline
	
	def get_time_remaining(self):
		"""Get remaining time in seconds"""
		if not self.voting_deadline:
			return 0
		
		from frappe.utils import now_datetime
		remaining = self.voting_deadline - now_datetime()
		return max(0, int(remaining.total_seconds()))
