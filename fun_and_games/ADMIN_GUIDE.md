# 🎮 Admin Page Guide - Participant Management & Session Reset

## How to Include Participants in a Session

### Method 1: When Creating a New Session
1. Go to `/admin` page
2. Click **"➕ Create New Session"**
3. Fill in session details
4. The system will automatically create default participants:
   - Player 1, Player 2, Player 3 (with appropriate team based on session type)

### Method 2: Manage Existing Session Participants
1. **Activate a session** first (make it the active session)
2. In the **Question Control** section, click **"👥 Manage Participants"**
3. **Edit existing participants**:
   - Change names and teams
   - Remove participants with "Remove" button
4. **Add new participants**:
   - Click **"+ Add Participant"**
   - Enter name and select team
5. Click **"Save Changes"**

### Available Teams:
- Management
- Backend  
- Frontend
- UI/UX
- Scrum
- DevOps
- Security
- QA

## How to Reset a Session

### Option 1: Reset Session Votes Only
- **Purpose**: Clear all votes but keep current question active
- **Button**: 🔄 Reset Session Votes
- **What it does**:
  - Deletes all votes for the session
  - Keeps current question and timer
  - Players can vote again on the same question

### Option 2: Reset Entire Session  
- **Purpose**: Complete session reset for replay
- **Button**: 🔄 Reset Entire Session  
- **What it does**:
  - Deletes all votes for the session
  - Clears current active question
  - Resets timer
  - Session returns to "no active question" state
  - Ready to start fresh with any question

## Typical Workflow

### Setting Up a Game Session:
1. **Create Session** with basic info
2. **Manage Participants** - add real names and teams
3. **Activate Session** (make it the active one)
4. **Start Questions** - click on questions to activate them
5. **Players Vote** on `/vote` page
6. **View Results** on `/results` page

### Replaying a Session:
1. **Reset Entire Session** to clear everything
2. **Start Questions** again from the beginning
3. Players can vote again on all questions

### Between Questions:
1. **View Results** for current question
2. **Activate Next Question** 
3. Players vote on new question
4. Repeat until all questions done

## API Endpoints (for developers)

```javascript
// Get session participants
POST /api/method/fun_and_games.fun_and_games.api.get_session_participants
Body: {"session_id": "GS-2025-00001"}

// Update session participants  
POST /api/method/fun_and_games.fun_and_games.api.update_session_participants
Body: {
  "session_id": "GS-2025-00001",
  "participants": [
    {"name": "John Doe", "team": "Backend"},
    {"name": "Jane Smith", "team": "Frontend"}
  ]
}

// Reset session votes only
POST /api/method/fun_and_games.fun_and_games.api.reset_session_votes  
Body: {"session_id": "GS-2025-00001"}

// Reset entire session
POST /api/method/fun_and_games.fun_and_games.api.reset_entire_session
Body: {"session_id": "GS-2025-00001"}
```

## Tips

- **Always manage participants** after creating a session to use real names
- **Use "Reset Entire Session"** when you want to replay the whole game
- **Use "Reset Session Votes"** if you just want to re-vote on current question
- **Participants must be added** before players can vote (they vote FOR participants)
- **Session must be active** to manage participants or reset
