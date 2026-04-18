"""
JARVIS Integration with Form Database
Allows JARVIS to access and review form submissions
Add this to JARVIS V0.01.py for database functionality
"""

from database import db

def review_pending_submissions():
    """
    JARVIS reviews all pending form submissions
    Call this function from your voice commands
    """
    pending = db.get_pending_reviews()
    
    if not pending:
        return "No pending submissions to review"
    
    reviews_text = f"You have {len(pending)} submissions awaiting review.\n"
    
    for i, submission in enumerate(pending, 1):
        reviews_text += f"\nSubmission {i}:\n"
        reviews_text += f"Form Type: {submission['form_name']}\n"
        reviews_text += f"Submitted: {submission['timestamp']}\n"
        reviews_text += f"Data: {submission['data']}\n"
    
    return reviews_text


def process_submissions_voice(submit_confirmation=True):
    """
    JARVIS processes pending submissions with voice feedback
    """
    pending = db.get_pending_reviews()
    
    if not pending:
        message = "No submissions to process"
        return message
    
    message = f"Processing {len(pending)} submissions"
    
    for submission in pending:
        # Extract key information
        data = submission['data']
        form_type = submission['form_name']
        
        # Create AI response based on form type
        if form_type == "contact_form":
            response = f"Contact request from {data.get('name', 'Unknown')} received"
        elif form_type == "feedback_form":
            response = f"Feedback received: {data.get('feedback', 'No content')}"
        else:
            response = f"{form_type} submitted"
        
        # Mark as reviewed
        db.mark_reviewed(submission['id'], response)
        message += f"\n✓ {response}"
    
    return message


def get_submission_summary():
    """Get a summary of all submissions"""
    all_submissions = db.get_all_submissions(limit=10)
    
    if not all_submissions:
        return "No submissions in database"
    
    summary = f"Database contains {len(all_submissions)} recent submissions:\n"
    
    for sub in all_submissions:
        summary += f"\n- {sub['form_name']} on {sub['timestamp']}"
        summary += f" (Reviewed: {'Yes' if sub['reviewed'] else 'No'})"
    
    return summary


def add_user_setting(setting_name: str, value):
    """
    Add or update a user setting in the database
    Example: add_user_setting("preferred_voice_speed", 170)
    """
    db.add_data("user_settings", setting_name, value)
    return f"Setting '{setting_name}' set to {value}"


def get_user_setting(setting_name: str, default=None):
    """
    Get a user setting from the database
    Example: speed = get_user_setting("preferred_voice_speed", 170)
    """
    value = db.get_latest_data("user_settings", setting_name)
    return value if value is not None else default


# Example voice commands that could be added to JARVIS:
"""
VOICE COMMAND EXAMPLES:
========================

"Review submissions" -> review_pending_submissions()
"Process pending requests" -> process_submissions_voice()
"What's in the database" -> get_submission_summary()
"Set voice speed to 150" -> add_user_setting("voice_speed", 150)
"What's my voice speed" -> get_user_setting("voice_speed")

Integration with JARVIS V0.01.py:
1. Import at top: from jarvis_database import *
2. Add to voice command handler:
   
   if "review" in command and "submissions" in command:
       speak(review_pending_submissions())
   
   elif "process" in command and "pending" in command:
       speak(process_submissions_voice())
   
   elif "database" in command:
       speak(get_submission_summary())
"""
