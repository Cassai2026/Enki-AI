"""
Example usage and API for the form database
Shows how to collect form data, submit it, and retrieve it for AI review
"""

from database import db
import json

def example_form_submission():
    """Example: Submitting a form to the database"""
    form_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234",
        "message": "Need help with project",
        "priority": "high"
    }
    
    submission_id = db.submit_form("contact_form", form_data)
    print(f"Form submitted. ID: {submission_id}")
    return submission_id


def example_get_pending_reviews():
    """Example: Get all submissions waiting for AI review"""
    pending = db.get_pending_reviews()
    
    print(f"\nPending Reviews ({len(pending)} items):")
    print("-" * 50)
    for item in pending:
        print(f"ID: {item['id']}")
        print(f"Form: {item['form_name']}")
        print(f"Data: {item['data']}")
        print(f"Submitted: {item['timestamp']}")
        print("-" * 50)
    
    return pending


def example_ai_review_workflow():
    """Example: Workflow for JARVIS to review pending submissions"""
    pending = db.get_pending_reviews()
    
    if not pending:
        print("No pending reviews")
        return
    
    print(f"\nJARVIS reviewing {len(pending)} submissions...")
    
    for submission in pending:
        print(f"\nReviewing submission ID {submission['id']}...")
        
        # Here you would process with AI/make decisions
        # For demo, we'll create a simple response
        ai_response = f"Processed {submission['form_name']}: {submission['data']['name']} - Priority: {submission['data'].get('priority', 'normal')}"
        
        # Mark as reviewed with AI response
        db.mark_reviewed(submission['id'], ai_response)
        print(f"✓ Marked as reviewed with response: {ai_response}")


def example_add_data():
    """Example: Add key-value data entries"""
    # Add user preferences
    db.add_data("user_preferences", "theme", "dark")
    db.add_data("user_preferences", "language", "en")
    db.add_data("user_preferences", "notifications", "enabled")
    
    # Add system configuration
    db.add_data("system_config", "api_key", "sample_key_123")
    db.add_data("system_config", "debug_mode", True)
    
    print("Data added to database")


def example_retrieve_data():
    """Example: Retrieve stored data"""
    # Get latest theme preference
    theme = db.get_latest_data("user_preferences", "theme")
    print(f"Current theme: {theme}")
    
    # Get all preferences
    prefs = db.get_data_by_category("user_preferences")
    print(f"\nAll preferences:")
    for pref in prefs:
        print(f"  {pref['key']}: {pref['value']}")


def simple_form_api(form_name: str, form_data: dict) -> dict:
    """
    Simple API endpoint for external services to submit forms
    
    Usage from website:
        response = simple_form_api("contact_form", {
            "name": "Jane",
            "email": "jane@example.com",
            "message": "Hello JARVIS"
        })
    """
    try:
        submission_id = db.submit_form(form_name, form_data)
        return {
            "status": "success",
            "submission_id": submission_id,
            "message": "Form submitted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    print("=== Form Database Examples ===\n")
    
    # Example 1: Submit a form
    print("1. Submitting form...")
    example_form_submission()
    
    # Example 2: Add some data
    print("\n2. Adding data entries...")
    example_add_data()
    
    # Example 3: Retrieve data
    print("\n3. Retrieving data...")
    example_retrieve_data()
    
    # Example 4: Get pending reviews
    print("\n4. Getting pending reviews...")
    example_get_pending_reviews()
    
    # Example 5: AI review workflow
    print("\n5. Simulating AI review...")
    example_ai_review_workflow()
    
    # Example 6: View all submissions
    print("\n6. All submissions in database...")
    all_subs = db.get_all_submissions(limit=10)
    print(f"Total submissions shown: {len(all_subs)}")
