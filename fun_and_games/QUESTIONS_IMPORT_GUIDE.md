# 🎮 Questions Import Guide for Fun and Games

This guide explains how to import questions into the Fun and Games app using AI-generated content.

## 📋 **AI Prompt Format**

Use this prompt with your AI to generate questions in the correct format:

```
Generate 20 "Who is most likely to..." questions for a team building game in JSON format. 

Each question should be appropriate for a workplace environment and follow this exact JSON structure:

[
  {
    "question_text": "Who is most likely to work late to finish a project?",
    "is_active": 1,
    "for_leadership_track": 1,
    "for_backend_track": 1,
    "for_frontend_track": 1,
    "for_custom_sessions": 1
  }
]

Field explanations:
- question_text: The actual question (always start with "Who is most likely to...")
- is_active: 1 = active question, 0 = inactive
- for_leadership_track: 1 = include in Leadership sessions, 0 = exclude
- for_backend_track: 1 = include in Backend sessions, 0 = exclude  
- for_frontend_track: 1 = include in Frontend sessions, 0 = exclude
- for_custom_sessions: 1 = include in Custom sessions, 0 = exclude

Make questions that are:
- Fun and engaging
- Appropriate for workplace
- Mix of technical and personality-based
- Some specific to leadership roles
- Some specific to backend developers
- Some specific to frontend developers
- Some general for all teams

Return only the JSON array, no additional text.
```

## 🔧 **Import Methods**

### **Method 1: Command Line Import**

1. Save your AI-generated JSON to a file (e.g., `my_questions.json`)
2. Run the import script:

```bash
# From the frappe-bench directory
cd apps/fun_and_games
python import_questions.py my_questions.json
```

Or using bench execute:

```bash
# From frappe-bench root
bench execute fun_and_games.import_questions.import_from_file --kwargs "{'file_path': 'apps/fun_and_games/my_questions.json'}"
```

### **Method 2: API Import**

You can also import via API call:

```javascript
// Example API call
fetch('/api/method/fun_and_games.fun_and_games.api.import_questions_from_json', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        questions_json: JSON.stringify([
            {
                "question_text": "Who is most likely to work late?",
                "is_active": 1,
                "for_leadership_track": 1,
                "for_backend_track": 1,
                "for_frontend_track": 1,
                "for_custom_sessions": 1
            }
        ])
    })
});
```

## 📝 **Question Field Details**

### **Required Fields:**
- `question_text` (string): The question text

### **Optional Fields (with defaults):**
- `is_active` (0 or 1): Whether question is active (default: 1)
- `for_leadership_track` (0 or 1): Include in Leadership sessions (default: 1)
- `for_backend_track` (0 or 1): Include in Backend sessions (default: 1)
- `for_frontend_track` (0 or 1): Include in Frontend sessions (default: 1)
- `for_custom_sessions` (0 or 1): Include in Custom sessions (default: 1)

## 🎯 **Question Categories**

### **Leadership Track Questions:**
```json
{
  "question_text": "Who is most likely to lead a difficult client meeting?",
  "for_leadership_track": 1,
  "for_backend_track": 0,
  "for_frontend_track": 0,
  "for_custom_sessions": 1
}
```

### **Backend Track Questions:**
```json
{
  "question_text": "Who is most likely to optimize database queries?",
  "for_leadership_track": 0,
  "for_backend_track": 1,
  "for_frontend_track": 0,
  "for_custom_sessions": 1
}
```

### **Frontend Track Questions:**
```json
{
  "question_text": "Who is most likely to create the most user-friendly interface?",
  "for_leadership_track": 0,
  "for_backend_track": 0,
  "for_frontend_track": 1,
  "for_custom_sessions": 1
}
```

### **Universal Questions:**
```json
{
  "question_text": "Who is most likely to remember everyone's birthday?",
  "for_leadership_track": 1,
  "for_backend_track": 1,
  "for_frontend_track": 1,
  "for_custom_sessions": 1
}
```

## ✅ **Import Features**

- **Duplicate Detection**: Won't import questions that already exist
- **Validation**: Checks for required fields
- **Error Handling**: Shows detailed error messages
- **Progress Tracking**: Shows import progress and results
- **Rollback Safe**: Uses database transactions

## 📁 **Sample Files**

- `sample_questions.json`: Example questions in correct format
- `import_questions.py`: Import script
- See the sample file for format examples

## 🚀 **Quick Start**

1. Use the AI prompt above to generate questions
2. Save the JSON response to a file
3. Run: `python import_questions.py your_file.json`
4. Questions will be available in the Game Question doctype
5. Use them in your game sessions!

## 🔍 **Troubleshooting**

- **"File not found"**: Check file path is correct
- **"Invalid JSON"**: Validate JSON format online
- **"Missing question_text"**: Ensure all questions have question_text field
- **"Already exists"**: Question with same text already imported (this is normal)

Happy gaming! 🎮
