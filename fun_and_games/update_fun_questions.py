#!/usr/bin/env python3
"""
Script to update all Fun category questions to have value 1 for all tracks
"""

import json
import os

def update_fun_questions():
    """Update all Fun questions to have 1 for all track flags"""
    
    # Path to questions file
    questions_file = "fun_and_games/questions.json"
    
    print("🔄 Loading questions from", questions_file)
    
    # Load questions
    with open(questions_file, 'r') as f:
        questions = json.load(f)
    
    print(f"📊 Total questions: {len(questions)}")
    
    # Count and update Fun questions
    fun_count = 0
    updated_count = 0
    
    for question in questions:
        if question.get("category") == "Fun":
            fun_count += 1
            
            # Check if any track flag needs updating
            needs_update = (
                question.get("for_leadership_track") != 1 or
                question.get("for_backend_track") != 1 or
                question.get("for_frontend_track") != 1 or
                question.get("for_custom_sessions") != 1
            )
            
            if needs_update:
                # Update all track flags to 1
                question["for_leadership_track"] = 1
                question["for_backend_track"] = 1
                question["for_frontend_track"] = 1
                question["for_custom_sessions"] = 1
                updated_count += 1
                print(f"✅ Updated: {question['question_text'][:50]}...")
    
    print(f"\n📊 Summary:")
    print(f"   - Fun questions found: {fun_count}")
    print(f"   - Questions updated: {updated_count}")
    print(f"   - Questions already correct: {fun_count - updated_count}")
    
    if updated_count > 0:
        # Save updated questions
        print(f"\n💾 Saving updated questions to {questions_file}")
        with open(questions_file, 'w') as f:
            json.dump(questions, f, indent=2)
        
        print("✅ All Fun questions now have value 1 for all tracks!")
    else:
        print("✅ All Fun questions already have correct values!")
    
    return {
        "fun_questions": fun_count,
        "updated": updated_count,
        "already_correct": fun_count - updated_count
    }

if __name__ == "__main__":
    result = update_fun_questions()
    print(f"\n🎉 Done! Updated {result['updated']} out of {result['fun_questions']} Fun questions")
