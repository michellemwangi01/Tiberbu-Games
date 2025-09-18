# Copyright (c) 2025, Fun and Games and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GameQuestion(Document):
	def validate(self):
		# Ensure only one question is active at a time
		if self.is_active:
			# Deactivate all other questions
			frappe.db.sql("""
				UPDATE `tabGame Question` 
				SET is_active = 0 
				WHERE name != %s AND is_active = 1
			""", (self.name,))
			frappe.db.commit()
