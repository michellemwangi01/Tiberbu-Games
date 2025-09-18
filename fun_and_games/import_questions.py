#!/usr/bin/env python3
"""
Import Questions Script for Fun and Games App

This script imports questions from a JSON file into the Game Question doctype.

Usage:
1. Create a JSON file with questions in the correct format
2. Run: python import_questions.py questions.json
3. Or run: bench execute fun_and_games.import_questions.import_from_file --kwargs "{'file_path': 'questions.json'}"

JSON Format:
[
  {
    "question_text": "Who is most likely to work late?",
    "is_active": 1,
    "for_leadership_track": 1,
    "for_backend_track": 1,
    "for_frontend_track": 0,
    "for_custom_sessions": 0
  }
]
"""

import json
import sys
import os
import frappe


def import_from_file(file_path):
    """Import questions from a JSON file"""

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found!")
        return False

    try:
        # Read JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        if not isinstance(questions_data, list):
            print("❌ Error: JSON file must contain an array of questions!")
            return False

        print(f"📖 Found {len(questions_data)} questions to import...")

        # Import questions
        imported_count = 0
        skipped_count = 0

        for i, question_data in enumerate(questions_data, 1):
            try:
                result = import_single_question(question_data, i)
                if result:
                    imported_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                print(f"❌ Error importing question {i}: {str(e)}")
                skipped_count += 1

        # Commit changes
        frappe.db.commit()

        print(f"\n✅ Import completed!")
        print(f"   📥 Imported: {imported_count} questions")
        print(f"   ⏭️  Skipped: {skipped_count} questions")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def import_single_question(question_data, index=None):
    """Import a single question"""

    # Validate required fields
    if not question_data.get("question_text"):
        print(f"⚠️  Skipping question {index}: Missing 'question_text'")
        return False

    question_text = question_data["question_text"].strip()

    # Check if question already exists
    existing = frappe.db.exists("Game Question", {"question_text": question_text})
    if existing:
        print(
            f"⏭️  Skipping question {index}: Already exists - '{question_text[:50]}...'"
        )
        return False

    try:
        # Create Game Question document
        question_doc = frappe.get_doc(
            {
                "doctype": "Game Question",
                "question_text": question_text,
                "category": question_data.get("category", ""),
                "is_active": question_data.get("is_active", 1),
                "for_leadership_track": question_data.get("for_leadership_track", 1),
                "for_backend_track": question_data.get("for_backend_track", 1),
                "for_frontend_track": question_data.get("for_frontend_track", 1),
                "for_custom_sessions": question_data.get("for_custom_sessions", 1),
            }
        )

        # Insert the document
        question_doc.insert(ignore_permissions=True)

        print(f"✅ Imported question {index}: '{question_text[:50]}...'")
        return True

    except Exception as e:
        print(f"❌ Error creating question {index}: {str(e)}")
        return False


def import_from_json_string(json_string):
    """Import questions from a JSON string"""
    try:
        questions_data = json.loads(json_string)

        if not isinstance(questions_data, list):
            print("❌ Error: JSON must contain an array of questions!")
            return False

        print(f"📖 Found {len(questions_data)} questions to import...")

        imported_count = 0
        skipped_count = 0

        for i, question_data in enumerate(questions_data, 1):
            try:
                result = import_single_question(question_data, i)
                if result:
                    imported_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                print(f"❌ Error importing question {i}: {str(e)}")
                skipped_count += 1

        frappe.db.commit()

        print(f"\n✅ Import completed!")
        print(f"   📥 Imported: {imported_count} questions")
        print(f"   ⏭️  Skipped: {skipped_count} questions")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_questions.py <json_file_path>")
        print("Example: python import_questions.py questions.json")
        sys.exit(1)

    file_path = sys.argv[1]

    # Initialize Frappe if running standalone
    try:
        import frappe

        if not frappe.db:
            frappe.init()
            frappe.connect()
    except:
        print(
            "❌ Error: Could not connect to Frappe. Make sure you're in the correct environment."
        )
        sys.exit(1)

    success = import_from_file(file_path)
    sys.exit(0 if success else 1)
