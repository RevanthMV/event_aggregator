import pandas as pd
import os
from datetime import datetime
import hashlib


class DatabaseInitializer:
    def __init__(self):
        self.users_file = "users_database.xlsx"
        self.events_file = "events_database.xlsx"
        self.registrations_file = "event_registrations.xlsx"
        self.notifications_file = "event_notifications.xlsx"

    def initialize_all_databases(self):
        """Initialize all databases if they do not exist (safe init + schema migration)."""
        print("🔄 Checking databases...")

        self._safe_init_or_migrate(self.users_file, self.create_users_database, self._migrate_users)
        self._safe_init_or_migrate(self.events_file, self.create_events_database, self._migrate_events)
        self._safe_init_or_migrate(self.registrations_file, self.create_registrations_database, self._migrate_registrations)
        self._safe_init_or_migrate(self.notifications_file, self.create_notifications_database, self._migrate_notifications)

        print("✅ Database check complete! (No overwrite)")

    # ---------------- USERS ----------------
    def create_users_database(self):
        print("📊 Creating users database...")
        users_data = {
            'ID': [1],
            'Name': ['System Administrator'],
            'Email': ['admin@college.edu'],
            'Student_ID': ['ADMIN001'],
            'Department': ['Administration'],
            'Year': ['Staff'],
            'Interests': ['All'],
            'Password_Hash': [self.hash_password('admin123')],
            'Is_Admin': [True],
            'Created_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        df = pd.DataFrame(users_data)
        df.to_excel(self.users_file, sheet_name='Users', index=False)
        print(f"✅ Users database created: {self.users_file}")

    def _migrate_users(self, file):
        required_cols = [
            'ID','Name','Email','Student_ID','Department','Year',
            'Interests','Password_Hash','Is_Admin','Created_Date'
        ]
        self._ensure_columns(file, 'Users', required_cols)

    # ---------------- EVENTS ----------------
    def create_events_database(self):
        print("📅 Creating events database...")
        df = pd.DataFrame(columns=[
            'Event_ID','Title','Category','Date','Time','Venue',
            'Description','Organizer','Capacity','Registered_Count',
            'Poster_Path','Created_Date','Created_By','Status'
        ])
        df.to_excel(self.events_file, sheet_name='Events', index=False)
        print(f"✅ Events database created: {self.events_file}")

    def _migrate_events(self, file):
        required_cols = [
            'Event_ID','Title','Category','Date','Time','Venue',
            'Description','Organizer','Capacity','Registered_Count',
            'Poster_Path','Created_Date','Created_By','Status'
        ]
        self._ensure_columns(file, 'Events', required_cols)

    # ---------------- REGISTRATIONS ----------------
    def create_registrations_database(self):
        print("🎟️ Creating registrations database...")
        df = pd.DataFrame(columns=[
            'Registration_ID','Event_ID','Event_Title','User_Email',
            'User_Name','Student_ID','Department','Year',
            'Registration_Date','Notification_Sent','Status'
        ])
        df.to_excel(self.registrations_file, sheet_name='Event_Registrations', index=False)
        print(f"✅ Registrations database created: {self.registrations_file}")

    def _migrate_registrations(self, file):
        required_cols = [
            'Registration_ID','Event_ID','Event_Title','User_Email',
            'User_Name','Student_ID','Department','Year',
            'Registration_Date','Notification_Sent','Status'
        ]
        self._ensure_columns(file, 'Event_Registrations', required_cols)

    # ---------------- NOTIFICATIONS ----------------
    def create_notifications_database(self):
        print("🔔 Creating notifications database...")
        df = pd.DataFrame(columns=[
            'Notification_ID','Event_ID','User_Email',
            'Message','Sent_Date','Status'
        ])
        df.to_excel(self.notifications_file, sheet_name='Notifications', index=False)
        print(f"✅ Notifications database created: {self.notifications_file}")

    def _migrate_notifications(self, file):
        required_cols = [
            'Notification_ID','Event_ID','User_Email',
            'Message','Sent_Date','Status'
        ]
        self._ensure_columns(file, 'Notifications', required_cols)

    # ---------------- HELPERS ----------------
    def _safe_init_or_migrate(self, file, create_func, migrate_func):
        """Only create DB if missing; never overwrite existing content."""
        if not os.path.exists(file):
            create_func()
        else:
            # Only migrate schema, don’t wipe data
            migrate_func(file)

    def _ensure_columns(self, file, sheet, required_cols):
        """Ensure that the Excel sheet has all required columns (migrate if missing)."""
        try:
            df = pd.read_excel(file, sheet_name=sheet)
            updated = False
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""  # add missing column
                    updated = True
                    print(f"⚡ Added missing column '{col}' to {file}")
            if updated:
                with pd.ExcelWriter(file, engine="openpyxl", mode="w") as writer:
                    df.to_excel(writer, sheet_name=sheet, index=False)
                print(f"✅ Migrated {file} to latest schema")
        except Exception as e:
            print(f"❌ Migration failed for {file}: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def reset_all_databases(self):
        """Force delete and recreate fresh databases (⚠️ wipes all data)."""
        print("🗑️ Resetting all databases...")
        for db_file in [self.users_file, self.events_file, self.registrations_file, self.notifications_file]:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"🗑️ Deleted: {db_file}")
        self.initialize_all_databases()
        print("✅ All databases reset and recreated!")
