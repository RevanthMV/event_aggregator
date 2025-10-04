from datetime import datetime

class User:
    def __init__(self, id, name, email, student_id, department, year, interests, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.student_id = student_id
        self.department = department
        self.year = year
        self.interests = interests if isinstance(interests, list) else []
        self.is_admin = is_admin
        self.registered_events = []
    
    def add_event_registration(self, event_id):
        """Add event to user's registered events"""
        if event_id not in self.registered_events:
            self.registered_events.append(event_id)
    
    def remove_event_registration(self, event_id):
        """Remove event from user's registered events"""
        if event_id in self.registered_events:
            self.registered_events.remove(event_id)

class Event:
    def __init__(self, id, title, category, date, time, venue, description, organizer, capacity, poster_image=None):
        self.id = id
        self.title = title
        self.category = category
        self.date = date
        self.time = time
        self.venue = venue
        self.description = description
        self.organizer = organizer
        self.capacity = capacity
        self.poster_image = poster_image
        self.registered_users = []
    
    def get_registration_count(self):
        """Get number of registered users"""
        return len(self.registered_users)
    
    def is_full(self):
        """Check if event is at capacity"""
        return len(self.registered_users) >= self.capacity
    
    def add_registration(self, user_id):
        """Add user to event registrations"""
        if user_id not in self.registered_users and not self.is_full():
            self.registered_users.append(user_id)
            return True
        return False
    
    def remove_registration(self, user_id):
        """Remove user from event registrations"""
        if user_id in self.registered_users:
            self.registered_users.remove(user_id)
            return True
        return False
