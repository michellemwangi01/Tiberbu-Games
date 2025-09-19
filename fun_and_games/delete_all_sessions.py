#!/usr/bin/env python3
"""
Delete All Sessions Script

Cleans up all existing sessions, participants, votes, and session questions
so you can test the new flexible session creation scripts with a clean slate.

Run via: bench --site [site-name] execute fun_and_games.delete_all_sessions.delete_all_sessions
"""

import frappe


def delete_all_sessions():
    """Delete all sessions and related data"""
    
    print("🗑️  Deleting all existing sessions...")
    
    try:
        # Get current session count
        session_count = frappe.db.count("Game Session")
        participant_count = frappe.db.count("Session Participant")
        vote_count = frappe.db.count("Game Vote")
        session_question_count = frappe.db.count("Session Question")
        
        print(f"📊 Current data:")
        print(f"   - Sessions: {session_count}")
        print(f"   - Participants: {participant_count}")
        print(f"   - Votes: {vote_count}")
        print(f"   - Session Questions: {session_question_count}")
        
        if session_count == 0:
            print("✅ No sessions to delete!")
            return {"success": True, "message": "No sessions found"}
        
        # Delete in correct order (child tables first)
        print("\n🗑️  Deleting votes...")
        frappe.db.sql("DELETE FROM `tabGame Vote`")
        
        print("🗑️  Deleting session participants...")
        frappe.db.sql("DELETE FROM `tabSession Participant`")
        
        print("🗑️  Deleting session questions...")
        frappe.db.sql("DELETE FROM `tabSession Question`")
        
        print("🗑️  Deleting sessions...")
        frappe.db.sql("DELETE FROM `tabGame Session`")
        
        # Commit changes
        frappe.db.commit()
        
        print("\n✅ All sessions deleted successfully!")
        print("🎯 Ready for fresh session creation with new flexible scripts")
        
        return {"success": True, "message": "All sessions deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting sessions: {str(e)}")
        frappe.db.rollback()
        return {"success": False, "error": str(e)}


def verify_cleanup():
    """Verify all session data has been deleted"""
    
    print("\n🔍 Verifying cleanup...")
    
    session_count = frappe.db.count("Game Session")
    participant_count = frappe.db.count("Session Participant")
    vote_count = frappe.db.count("Game Vote")
    session_question_count = frappe.db.count("Session Question")
    
    print(f"📊 After cleanup:")
    print(f"   - Sessions: {session_count}")
    print(f"   - Participants: {participant_count}")
    print(f"   - Votes: {vote_count}")
    print(f"   - Session Questions: {session_question_count}")
    
    if session_count == 0 and participant_count == 0 and vote_count == 0 and session_question_count == 0:
        print("✅ Cleanup successful - all session data removed!")
        print("🚀 Ready to test new session creation scripts")
        return True
    else:
        print("⚠️  Some data may still exist")
        return False


def delete_and_verify():
    """Delete all sessions and verify cleanup"""
    result = delete_all_sessions()
    verify_cleanup()
    return result


if __name__ == "__main__":
    delete_and_verify()
