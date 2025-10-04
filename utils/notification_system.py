import pandas as pd
import os
from datetime import datetime, timedelta
import schedule
import time
import threading


class NotificationSystem:
    def __init__(self):
        self.events_file = "events_database.xlsx"
        self.events_sheet = "Events"
        self.notifications_file = "event_notifications.xlsx"
        self.notifications_sheet = "Notifications"
        self.registrations_file = "event_registrations.xlsx"
        self.registrations_sheet = "Event_Registrations"
        self.ensure_databases_exist()

    # -------------------- INITIALIZE DB --------------------
    def ensure_databases_exist(self):
        """Ensure all required Excel files exist"""
        if not os.path.exists(self.events_file):
            df = pd.DataFrame(columns=[
                'Event_ID', 'Title', 'Category', 'Date', 'Time', 'Venue',
                'Description', 'Organizer', 'Capacity', 'Registered_Count',
                'Poster_Path', 'Created_Date', 'Created_By', 'Status'
            ])
            df.to_excel(self.events_file, sheet_name=self.events_sheet, index=False)

        if not os.path.exists(self.notifications_file):
            df = pd.DataFrame(columns=[
                'Notification_ID', 'Event_ID', 'User_Email', 'Message', 'Sent_Date', 'Status'
            ])
            df.to_excel(self.notifications_file, sheet_name=self.notifications_sheet, index=False)

        if not os.path.exists(self.registrations_file):
            df = pd.DataFrame(columns=[
                'Registration_ID', 'Event_ID', 'Event_Title', 'User_Email', 'User_Name',
                'Student_ID', 'Department', 'Year', 'Registration_Date', 'Notification_Sent', 'Status'
            ])
            df.to_excel(self.registrations_file, sheet_name=self.registrations_sheet, index=False)

    # -------------------- CORE REMINDER LOGIC --------------------
    def send_reminders(self, hours_before):
        """
        Send reminders to all registered users for events that start in <hours_before> hours.
        Adds entries to event_notifications.xlsx.
        """
        try:
            events_df = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            notifs_df = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)

            now = datetime.now()
            upcoming_time = now + timedelta(hours=hours_before)

            for _, event in events_df.iterrows():
                event_date = pd.to_datetime(event['Date'], errors='coerce')
                if pd.isna(event_date):
                    continue

                # Only send if event is within the reminder window
                if 0 <= (event_date - upcoming_time).total_seconds() <= 86400:  # 1-day buffer
                    event_id = event['Event_ID']
                    event_regs = regs_df[regs_df['Event_ID'] == event_id]

                    for _, reg in event_regs.iterrows():
                        user_email = reg['User_Email']

                        # Avoid duplicate notifications
                        existing = notifs_df[
                            (notifs_df['Event_ID'] == event_id)
                            & (notifs_df['User_Email'].str.lower() == user_email.lower())
                            & (notifs_df['Status'] == f"{hours_before}h Reminder")
                        ]
                        if not existing.empty:
                            continue

                        notification_id = str(len(notifs_df) + 1)
                        message = (
                            f"Reminder: '{event['Title']}' starts in {hours_before} hours "
                            f"on {event['Date']} at {event['Time']} at {event['Venue']}."
                        )

                        new_notif = {
                            'Notification_ID': notification_id,
                            'Event_ID': event_id,
                            'User_Email': user_email,
                            'Message': message,
                            'Sent_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'Status': f"{hours_before}h Reminder"
                        }

                        notifs_df = pd.concat([notifs_df, pd.DataFrame([new_notif])], ignore_index=True)

            # Save all updated notifications
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                notifs_df.to_excel(writer, sheet_name=self.notifications_sheet, index=False)

            print(f"✅ {hours_before}-hour reminders logged successfully.")
        except Exception as e:
            print(f"⚠️ Reminder system error ({hours_before}h): {e}")

    # -------------------- 48HR + 24HR REMINDERS --------------------
    def send_48_hour_reminders(self):
        print("⏰ Checking for 48-hour reminders...")
        self.send_reminders(48)

    def send_24_hour_reminders(self):
        print("⏰ Checking for 24-hour reminders...")
        self.send_reminders(24)

    # -------------------- SCHEDULER --------------------
    def start_scheduler(self):
        """Run hourly checks for 24-hour and 48-hour reminders"""
        schedule.every(1).hours.do(self.send_48_hour_reminders)
        schedule.every(1).hours.do(self.send_24_hour_reminders)

        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(3600)

        t = threading.Thread(target=run_scheduler, daemon=True)
        t.start()
        print("✅ Notification scheduler started (24hr + 48hr checks hourly)")
