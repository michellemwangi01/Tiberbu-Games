import frappe


def get_context(context):
    frappe.log_error("admin.py get_context() is running", "Admin Debug")
    context.no_cache = 1
    context.show_sidebar = False
    return context
