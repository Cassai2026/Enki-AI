## Local Form Database for JARVIS AI Assistant

A complete local database system for storing form submissions, managing data, and integrating with your JARVIS AI assistant.

### Features

- **Local SQLite Database** - File-based, no server setup required
- **Form Submission Management** - Store, retrieve, and review submitted forms
- **AI Review Queue** - Automatically queue submissions for JARVIS to review
- **Key-Value Data Storage** - Store any configuration or preference data
- **REST API** - Easy HTTP endpoints for your website to submit data
- **Voice Integration** - Add voice commands to JARVIS to review submissions

### Files Created

1. **database.py** - Core database module with all database operations
2. **form_api.py** - Examples and helper functions for using the database
3. **web_server.py** - Flask REST API server for accepting form submissions
4. **jarvis_database.py** - JARVIS integration functions
5. **DATABASE_README.md** - This file

### Quick Start

#### 1. Submit a Form from Your Website

```javascript
// JavaScript example - submit form data
const formData = {
    "form_name": "contact_form",
    "data": {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Hello JARVIS!"
    }
};

fetch('http://localhost:5000/api/submit-form', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(formData)
})
.then(response => response.json())
.then(data => console.log('Submission ID:', data.submission_id));
```

#### 2. Start the Web Server

```bash
python web_server.py
```

This starts the Flask API on `http://localhost:5000`

#### 3. Check Pending Reviews

```bash
GET http://localhost:5000/api/pending-reviews
```

Returns all submissions waiting for AI review.

#### 4. Integrate with JARVIS

```python
# In JARVIS V0.01.py
from jarvis_database import *

# Add voice command handler
if "review" in command:
    message = review_pending_submissions()
    speak(message)
```

### Database Structure

#### form_submissions
- `id` - Unique submission ID
- `form_name` - Type of form (e.g., "contact_form", "feedback_form")
- `data` - JSON data submitted with the form
- `timestamp` - When it was submitted
- `reviewed` - Whether JARVIS reviewed it
- `notes` - Any notes added during review

#### data_entries
- `id` - Entry ID
- `category` - Data category (e.g., "user_settings", "system_config")
- `key` - Setting/data key
- `value` - The value (stored as JSON)
- `timestamp` - When it was added

#### review_queue
- `id` - Queue entry ID
- `submission_id` - Link to form submission
- `status` - 'pending' or 'completed'
- `ai_response` - Response from JARVIS/AI
- `created_at` - When added to queue

### API Endpoints

#### POST /api/submit-form
Submit a form to the database

```json
{
    "form_name": "contact_form",
    "data": {
        "name": "John",
        "email": "john@example.com",
        "message": "Hello"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "submission_id": 1,
    "message": "Form submitted successfully"
}
```

#### GET /api/pending-reviews
Get all submissions pending AI review

**Response:**
```json
{
    "status": "success",
    "count": 2,
    "submissions": [
        {
            "id": 1,
            "form_name": "contact_form",
            "data": {...},
            "timestamp": "2026-02-19 10:30:45"
        }
    ]
}
```

#### GET /api/submissions?limit=50
Get recent form submissions

#### POST /api/mark-reviewed/<submission_id>
Mark a submission as reviewed

```json
{
    "ai_response": "Contact request processed"
}
```

#### POST /api/data
Add key-value data

```json
{
    "category": "user_settings",
    "key": "theme",
    "value": "dark"
}
```

#### GET /api/data/<category>
Get all data in a category

#### GET /api/data/<category>/<key>
Get a specific data value

### Python Usage Examples

#### Submit a Form
```python
from database import db

submission_id = db.submit_form("contact_form", {
    "name": "Jane",
    "email": "jane@example.com"
})
print(f"Submitted with ID: {submission_id}")
```

#### Get Pending Reviews
```python
pending = db.get_pending_reviews()
for sub in pending:
    print(f"Form: {sub['form_name']}")
    print(f"Data: {sub['data']}")
```

#### Mark as Reviewed
```python
db.mark_reviewed(submission_id, "Reviewed by JARVIS")
```

#### Store Settings
```python
db.add_data("user_settings", "voice_speed", 170)
db.add_data("user_settings", "preferred_language", "en")
```

#### Retrieve Settings
```python
speed = db.get_latest_data("user_settings", "voice_speed")
language = db.get_latest_data("user_settings", "preferred_language")
```

### Integration with JARVIS Voice Commands

Add these to your JARVIS command handler:

```python
from jarvis_database import *

# ... in your voice recognition section ...

if "review" in command and "submissions" in command:
    message = review_pending_submissions()
    speak(message)

elif "process" in command and "pending" in command:
    message = process_submissions_voice()
    speak(message)

elif "what" in command and "database" in command:
    message = get_submission_summary()
    speak(message)

elif "set" in command and "speed" in command:
    # Extract speed value from command
    speed = extract_number(command)  # You'd implement this
    message = add_user_setting("voice_speed", speed)
    speak(message)
```

### Database Location

The database file is stored at:
```
AI_Assistant/data/form_submissions.db
```

It's automatically created when you first import the database module.

### Folder For Local Data

The database automatically creates this directory structure:
```
AI_Assistant/
├── data/
│   └── form_submissions.db (the local database)
├── database.py
├── form_api.py
├── web_server.py
└── jarvis_database.py
```

### Dependencies

Required packages:
```bash
pip install flask flask-cors sqlite3
```

To install:
```bash
pip install flask flask-cors
```

Note: `sqlite3` comes built-in with Python.

### Running Everything

1. **Start Web Server** (listen for form submissions from your website):
   ```bash
   python web_server.py
   ```

2. **Use with JARVIS**:
   ```bash
   python JARVIS V0.01.py
   ```
   (with database integration added)

3. **Submit Forms from Your Website**:
   ```javascript
   // From your website's JavaScript
   fetch('http://localhost:5000/api/submit-form', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({form_name: "my_form", data: {...}})
   });
   ```

### Testing

Run the examples:
```bash
python form_api.py
```

This runs all example functions and shows how the database works.

### Workflow Example

1. User fills out form on your website
2. JavaScript submits to `http://localhost:5000/api/submit-form`
3. Database stores the submission automatically queues it for review
4. You ask JARVIS: "Review submissions"
5. JARVIS reads pending submissions and processes them
6. JARVIS marks submissions as reviewed with AI response
7. Your website can check `/api/pending-reviews` to see status

---

**Created for JARVIS AI Assistant**
Local Storage Solution for Form Data & AI Review Queue
February 2026
