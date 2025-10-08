import pandas as pd
import os
from datetime import datetime
import hashlib
import uuid
import shutil
from utils.database_initializer import DatabaseInitializer
from utils.email_notifications import EmailNotificationSystem


class ExcelUserDatabase:
    def __init__(self):
        # ✅ Always use project root (same folder as main.py)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

        self.users_file = os.path.join(self.project_root, "users_database.xlsx")
        self.events_file = os.path.join(self.project_root, "events_database.xlsx")
        self.registrations_file = os.path.join(self.project_root, "event_registrations.xlsx")
        self.notifications_file = os.path.join(self.project_root, "event_notifications.xlsx")

        self.users_sheet = "Users"
        self.events_sheet = "Events"
        self.registrations_sheet = "Event_Registrations"
        self.notifications_sheet = "Notifications"

        self.ensure_database_exists()
        self.email_sys = EmailNotificationSystem()

    # ---------------- Ensure DB Exists ----------------
    def ensure_database_exists(self):
        dbi = DatabaseInitializer()
        dbi.initialize_all_databases()

    # ---------------- Utility ----------------
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # ---------------- Admin Auth ----------------
    def authenticate_admin_user(self, email, password, security_code=None):
        try:
            print(f"🔍 Loading admin users from: {self.users_file}")
            df = pd.read_excel(self.users_file, sheet_name=self.users_sheet)

            admin_row = df[(df['Email'].str.lower() == email.lower()) & (df['Is_Admin'] == True)]
            if admin_row.empty:
                return False, "Admin user not found"

            admin = admin_row.iloc[0]
            if str(admin['Password_Hash']) == self.hash_password(password):
                return True, {
                    'id': int(admin['ID']),
                    'name': str(admin['Name']),
                    'email': str(admin['Email']),
                    'student_id': str(admin['Student_ID']),
                    'department': str(admin['Department']),
                    'year': str(admin['Year']),
                    'interests': [] if pd.isna(admin.get('Interests', None)) else str(admin['Interests']).split(','),
                    'is_admin': True
                }
            return False, "Invalid admin password"
        except Exception as e:
            return False, f"Admin authentication error: {str(e)}"

    # ---------------- Student Auth ----------------
    def authenticate_user(self, email, password):
        try:
            print(f"🔍 Loading users from: {self.users_file}")
            df = pd.read_excel(self.users_file, sheet_name=self.users_sheet)

            user_row = df[df['Email'].str.lower() == email.lower()]
            if user_row.empty:
                return False, "User not found"

            user = user_row.iloc[0]
            if str(user['Password_Hash']) == self.hash_password(password):
                return True, {
                    'id': int(user['ID']),
                    'name': str(user['Name']),
                    'email': str(user['Email']),
                    'student_id': str(user['Student_ID']),
                    'department': str(user['Department']),
                    'year': str(user['Year']),
                    'interests': [] if pd.isna(user.get('Interests', None)) else str(user['Interests']).split(','),
                    'is_admin': str(user['Is_Admin']).strip().lower() == "true"
                }
            return False, "Invalid password"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    # ---------------- Register User ----------------
    def register_user(self, name, student_id, email, department, year, password, interests):
        try:
            print(f"📝 Registering new user to: {self.users_file}")
            df = pd.read_excel(self.users_file, sheet_name=self.users_sheet)
            if len(df[df['Email'].str.lower() == email.lower()]) > 0:
                return False, "User with this email already exists"
            if len(df[df['Student_ID'] == student_id]) > 0:
                return False, "Student ID already registered"

            new_user_data = {
                'ID': [len(df) + 1],
                'Name': [name],
                'Email': [email.lower()],
                'Student_ID': [student_id],
                'Department': [department],
                'Year': [year],
                'Interests': [','.join(interests)],
                'Password_Hash': [self.hash_password(password)],
                'Is_Admin': [False],
                'Created_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            }
            df = pd.concat([df, pd.DataFrame(new_user_data)], ignore_index=True)

            with pd.ExcelWriter(self.users_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.users_sheet, index=False)

            print(f"✅ User registered successfully: {email}")
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    # ---------------- Events ----------------
    def create_event(self, title, category, date, time, venue, description, organizer, organizer_contact, capacity, poster_path=None):
        try:
            print(f"📂 Saving event to: {self.events_file}")

            try:
                df = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            except:
                df = pd.DataFrame(columns=[
                    'Event_ID', 'Title', 'Category', 'Date', 'Time', 'Venue',
                    'Description', 'Organizer', 'Organizer_Contact', 'Capacity', 
                    'Registered_Count', 'Poster_Path', 'Created_Date', 'Created_By', 'Status'
                ])

            event_id = str(uuid.uuid4())[:8].upper()
            new_event = {
                'Event_ID': [event_id],
                'Title': [title],
                'Category': [category],
                'Date': [date],
                'Time': [time],
                'Venue': [venue],
                'Description': [description],
                'Organizer': [organizer],
                'Organizer_Contact': [organizer_contact],
                'Capacity': [int(capacity)],
                'Registered_Count': [0],
                'Poster_Path': [poster_path or ''],
                'Created_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Created_By': [organizer],
                'Status': ['Active']
            }

            df = pd.concat([df, pd.DataFrame(new_event)], ignore_index=True)
            with pd.ExcelWriter(self.events_file, engine='openpyxl', mode="w") as writer:
                df.to_excel(writer, sheet_name=self.events_sheet, index=False)

            print(f"✅ Event created: {title} ({event_id})")
            return True, event_id

        except Exception as e:
            return False, str(e)


    # ✅ Admin Dashboard
    def get_all_events(self):
        """Return all events as list of dictionaries from Events sheet."""
        try:
            if not os.path.exists(self.events_file):
                return []

            df = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            if df.empty:
                return []

            events = df.to_dict(orient="records")

            # Calculate registration count
            if os.path.exists(self.registrations_file):
                regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
                for event in events:
                    event_id = event.get("Event_ID")
                    count = len(regs_df[regs_df["Event_ID"] == event_id]) if "Event_ID" in regs_df.columns else 0
                    event["Registered_Count"] = count

            return events
        except Exception as e:
            print(f"❌ Error reading events: {e}")
            return []

    # ✅ Student Dashboard
    def get_upcoming_events(self):
        """Return only active and upcoming events for student dashboard."""
        try:
            if not os.path.exists(self.events_file):
                return []

            df = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            if df.empty:
                return []

            today = datetime.now().date()
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df[df['Date'] >= pd.Timestamp(today)]
            df = df[df['Status'].str.lower() == "active"]

            events = df.to_dict(orient="records")

            if os.path.exists(self.registrations_file):
                regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
                for event in events:
                    event_id = event.get("Event_ID")
                    count = len(regs_df[regs_df["Event_ID"] == event_id]) if "Event_ID" in regs_df.columns else 0
                    event["Registered_Count"] = count

            return events
        except Exception as e:
            print(f"❌ Error fetching student events: {e}")
            return []

    # ---------------- Registrations ----------------
    def register_user_for_event(self, event_id, user_email, user_name=None, student_id=None):
        """Register user for an event and send confirmation immediately"""
        try:
            # Load or create registration sheet
            regs = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet) \
                if os.path.exists(self.registrations_file) else pd.DataFrame(columns=[
                    'Registration_ID', 'Event_ID', 'Event_Title', 'User_Email', 'User_Name',
                    'Student_ID', 'Department', 'Year', 'Registration_Date', 'Notification_Sent', 'Status'
                ])

            # Load user details
            users = pd.read_excel(self.users_file, sheet_name=self.users_sheet)
            user_row = users[users['Email'].str.lower() == user_email.lower()]
            if user_row.empty:
                if not user_name or not student_id:
                    return False, "User not found and no extra details provided"
                user = {'Name': user_name, 'Student_ID': student_id, 'Department': "Unknown", 'Year': "Unknown"}
            else:
                user = user_row.iloc[0]

            # Load event details
            events = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            event_row = events[events['Event_ID'] == event_id]
            if event_row.empty:
                return False, "Event not found"
            event = event_row.iloc[0]

            # Prevent duplicate registration
            if not regs[(regs['Event_ID'] == event_id) & (regs['User_Email'].str.lower() == user_email.lower())].empty:
                return False, "Already registered for this event"

            # Capacity check
            if len(regs[regs['Event_ID'] == event_id]) >= int(event['Capacity']):
                return False, "Event is full"

            # Create registration entry
            registration_id = str(uuid.uuid4())[:8].upper()
            new_row = {
                'Registration_ID': registration_id,
                'Event_ID': event_id,
                'Event_Title': event['Title'],
                'User_Email': user_email.lower(),
                'User_Name': user['Name'] if 'Name' in user else user_name,
                'Student_ID': user['Student_ID'] if 'Student_ID' in user else student_id,
                'Department': user['Department'] if 'Department' in user else "Unknown",
                'Year': user['Year'] if 'Year' in user else "Unknown",
                'Registration_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Notification_Sent': True,  # will send immediately
                'Status': 'Active'
            }

            # Save to Excel
            regs = pd.concat([regs, pd.DataFrame([new_row])], ignore_index=True)
            with pd.ExcelWriter(self.registrations_file, engine='openpyxl') as writer:
                regs.to_excel(writer, sheet_name=self.registrations_sheet, index=False)

            # 📨 Send immediate confirmation email
            print(f"📧 Sending immediate confirmation email to {user_email}")
            event_dict = event.to_dict()
            event_dict['User_Name'] = user['Name']
            self.email_sys.send_registration_confirmation(user_email, event_dict)

            # 📝 Log notification for record-keeping
            self.log_notification(event_id, user_email, f"Immediate confirmation for {event['Title']}")

            print(f"✅ Registered {user_email} for {event['Title']} (confirmation sent)")
            return True, event.to_dict()

        except Exception as e:
            return False, f"Registration failed: {str(e)}"


    # ---------------- Log Notification ----------------
    def log_notification(self, event_id, user_email, message):
        try:
            df = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet) \
                if os.path.exists(self.notifications_file) else pd.DataFrame(columns=[
                    "Notification_ID", "Event_ID", "User_Email", "Message", "Sent_Date", "Status"
                ])

            notif_id = str(uuid.uuid4())[:8].upper()
            new_notif = {
                "Notification_ID": notif_id,
                "Event_ID": event_id,
                "User_Email": user_email,
                "Message": message,
                "Sent_Date": "",
                "Status": "Pending"
            }

            df = pd.concat([df, pd.DataFrame([new_notif])], ignore_index=True)
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.notifications_sheet, index=False)

            print(f"📝 Notification logged for {user_email}")
        except Exception as e:
            print(f"⚠️ Failed to log notification: {e}")

    # ---------------- Send Pending Notifications ----------------
    def send_pending_notifications(self):
        """Send all pending notifications"""
        try:
            if not os.path.exists(self.notifications_file):
                print("ℹ️ No notifications yet.")
                return

            notifs = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
            events = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            pending = notifs[notifs["Status"].str.lower() == "pending"]

            if pending.empty:
                print("✅ No pending notifications.")
                return

            for _, row in pending.iterrows():
                event = events[events["Event_ID"] == row["Event_ID"]]
                if event.empty:
                    continue

                event_data = event.iloc[0].to_dict()
                success = self.email_sys.send_registration_confirmation(row["User_Email"], event_data)

                if success:
                    notifs.loc[notifs["Notification_ID"] == row["Notification_ID"], ["Sent_Date", "Status"]] = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Sent"
                    ]

            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                notifs.to_excel(writer, sheet_name=self.notifications_sheet, index=False)

            print("✅ Pending notifications processed.")
        except Exception as e:
            print(f"❌ Error in send_pending_notifications: {e}")

    # ---------------- 24 Hour Reminders ----------------
    def schedule_24hr_reminders(self):
        """Send reminder emails 24 hours before event start time"""
        try:
            if not os.path.exists(self.events_file) or not os.path.exists(self.registrations_file):
                print("⚠️ No events or registrations found.")
                return

            events = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            regs = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            now = datetime.now()

            reminder_count = 0

            for _, event in events.iterrows():
                event_date = pd.to_datetime(event['Date'], errors='coerce')
                if pd.isna(event_date):
                    continue

                hours_left = (event_date - now).total_seconds() / 3600
                if 23 <= hours_left <= 25:  # Within 24 hours
                    event_regs = regs[regs['Event_ID'] == event['Event_ID']]
                    for _, reg in event_regs.iterrows():
                        email = reg['User_Email']
                        user_name = reg.get('User_Name', 'Participant')
                        message = f"⏰ Reminder: '{event['Title']}' starts in 24 hours at {event['Time']}!"
                        print(f"📧 Sending 24-hour reminder to {email} for {event['Title']}")
                        self.email_sys.send_event_reminder(email, event.to_dict(), message)
                        self.log_notification(event['Event_ID'], email, message)
                        reminder_count += 1

            print(f"✅ {reminder_count} 24-hour reminder(s) sent successfully.")
        except Exception as e:
            print(f"⚠️ Error in schedule_24hr_reminders: {e}")
    # ---------------- FEEDBACK SYSTEM ----------------
    def submit_feedback(self, event_id, user_email, user_name, feedback_text, rating):
        """Save student feedback for an event."""
        import pandas as pd
        import uuid
        from datetime import datetime

        try:
            feedback_file = os.path.join(self.project_root, "event_feedbacks.xlsx")
            feedback_sheet = "Feedbacks"

            # Load or create feedback sheet
            if os.path.exists(feedback_file):
                df = pd.read_excel(feedback_file, sheet_name=feedback_sheet)
            else:
                df = pd.DataFrame(columns=[
                    "Feedback_ID", "Event_ID", "Event_Title",
                    "User_Email", "User_Name", "Feedback", "Rating", "Date"
                ])

            # Get event title
            events_df = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            event_row = events_df[events_df["Event_ID"] == event_id]
            event_title = event_row.iloc[0]["Title"] if not event_row.empty else "Unknown"

            # Create new feedback
            new_row = {
                "Feedback_ID": str(uuid.uuid4())[:8].upper(),
                "Event_ID": event_id,
                "Event_Title": event_title,
                "User_Email": user_email,
                "User_Name": user_name,
                "Feedback": feedback_text,
                "Rating": rating,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            with pd.ExcelWriter(feedback_file, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=feedback_sheet, index=False)

            print(f"✅ Feedback saved for {event_title} by {user_name}")
            return True, "Feedback submitted successfully"
        except Exception as e:
            return False, f"❌ Feedback submission failed: {e}"



    # ---------------- Poster ----------------
    def save_poster_image(self, source_path, event_id):
        try:
            posters_dir = os.path.join(self.project_root, "event_posters")
            if not os.path.exists(posters_dir):
                os.makedirs(posters_dir)

            ext = os.path.splitext(source_path)[1]
            unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
            poster_filename = f"poster_{event_id}_{unique_suffix}{ext}"
            poster_path = os.path.join(posters_dir, poster_filename)
            shutil.copy2(source_path, poster_path)
            print(f"🖼️ Poster saved: {poster_path}")
            return True, poster_path
        except Exception as e:
            return False, str(e)
