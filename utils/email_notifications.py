import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import uuid
import pandas as pd
import threading
import time
import os

class EmailNotificationSystem:
    def __init__(self, sender_email="revanthrajreddy@gmail.com", sender_password="quxdquurovojgzdx"):
        # SMTP settings
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = sender_email
        self.sender_password = sender_password

        # Files / sheets (must match excel_db / initializer)
        self.events_file = "events_database.xlsx"
        self.events_sheet = "Events"
        self.registrations_file = "event_registrations.xlsx"
        self.registrations_sheet = "Event_Registrations"
        self.notifications_file = "event_notifications.xlsx"
        self.notifications_sheet = "Notifications"

    # ---------------- EMAIL SENDING ----------------
    def send_email(self, recipient_email, subject, body):
        """Generic email sender; returns True on success, False on error."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=20)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            print(f"✅ Email sent to {recipient_email}: {subject}")
            return True
        except Exception as e:
            print(f"❌ Email sending failed to {recipient_email}: {e}")
            return False

    # ---------------- CONFIRMATION ----------------
    def send_registration_confirmation(self, user_email, event):
        """Send instant confirmation email on registration."""
        subject = f"🎉 Registered for {event['Title']}"
        body = f"""Hello {event.get('Organizer','Participant')},

You are successfully registered for:

Event: {event['Title']}
Date: {event['Date']}
Time: {event['Time']}
Venue: {event['Venue']}
Organizer: {event.get('Organizer','')}

We’ll remind you again a day before the event.

Best regards,
Event Aggregator
"""
        success = self.send_email(user_email, subject, body)
        # Log confirmation (optional) - we write to notifications file as Sent/Confirmation
        if success:
            self._log_notification(event.get("Event_ID", ""), user_email, f"Confirmation for {event['Title']}", "Sent")
        else:
            self._log_notification(event.get("Event_ID", ""), user_email, f"Confirmation failed for {event['Title']}", "Failed")
        return success

    # ---------------- REMINDERS ----------------
    def send_event_reminder(self, recipient_email, event):
        """Send reminder email (1 day before event)."""
        subject = f"⏰ Reminder: {event['Title']} Tomorrow!"
        body = f"""Dear Student,

This is a reminder for:

Event: {event['Title']}
Date: {event['Date']}
Time: {event['Time']}
Venue: {event['Venue']}
Organizer: {event.get('Organizer','')}

See you there!
Event Aggregator
"""
        return self.send_email(recipient_email, subject, body)

    def check_and_send_reminders(self):
        """Check events happening tomorrow and send reminders to registrations with Notification_Sent == False."""
        try:
            if not os.path.exists(self.events_file) or not os.path.exists(self.registrations_file):
                print("⚠️ Events or registrations file missing; skipping reminder check.")
                return

            events = pd.read_excel(self.events_file, sheet_name=self.events_sheet)
            regs = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)

            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            tomorrow_events = events[events["Date"] == tomorrow]

            if tomorrow_events.empty:
                print("ℹ️ No events tomorrow.")
            for _, event in tomorrow_events.iterrows():
                event_id = event["Event_ID"]
                to_notify = regs[(regs["Event_ID"] == event_id) & (regs["Notification_Sent"] == False)]

                for idx, reg in to_notify.iterrows():
                    user_email = reg["User_Email"]
                    success = self.send_event_reminder(user_email, event.to_dict())
                    if success:
                        # mark registration as notified
                        regs.loc[idx, "Notification_Sent"] = True
                        # log and mark notification record as Sent
                        self._log_notification(event_id, user_email, f"Reminder for {event['Title']}", "Sent")
                        # update any matching pending notification rows in notifications file
                        self._mark_notification_sent_for(event_id, user_email)
                    else:
                        # log failed attempt
                        self._log_notification(event_id, user_email, f"Reminder FAILED for {event['Title']}", "Failed")

            # save back registrations
            with pd.ExcelWriter(self.registrations_file, engine="openpyxl") as writer:
                regs.to_excel(writer, sheet_name=self.registrations_sheet, index=False)

            print("🔔 Reminder check complete.")
        except Exception as e:
            print(f"❌ Notification check error: {e}")

    # ---------------- NOTIFICATIONS LOGGING ----------------
    def _log_notification(self, event_id, email, message, status):
        """Append a notification record to event_notifications.xlsx (always creates file if missing)."""
        try:
            if os.path.exists(self.notifications_file):
                try:
                    notifs = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
                except Exception:
                    # file exists but sheet missing or unreadable: create fresh frame
                    notifs = pd.DataFrame(columns=["Notification_ID", "Event_ID", "User_Email", "Message", "Sent_Date", "Status"])
            else:
                notifs = pd.DataFrame(columns=["Notification_ID", "Event_ID", "User_Email", "Message", "Sent_Date", "Status"])

            notif_id = str(uuid.uuid4())[:8].upper()
            new_notif = {
                "Notification_ID": notif_id,
                "Event_ID": event_id,
                "User_Email": email,
                "Message": message,
                "Sent_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Sent" else "",
                "Status": status
            }
            notifs = pd.concat([notifs, pd.DataFrame([new_notif])], ignore_index=True)
            with pd.ExcelWriter(self.notifications_file, engine="openpyxl") as writer:
                notifs.to_excel(writer, sheet_name=self.notifications_sheet, index=False)
            return True
        except Exception as e:
            print(f"❌ Failed to log notification: {e}")
            return False

    def _mark_notification_sent_for(self, event_id, user_email):
        """
        Marks existing pending notifications rows (matching event_id & user_email) as Sent.
        This updates event_notifications.xlsx (Sent_Date + Status).
        """
        try:
            if not os.path.exists(self.notifications_file):
                return False

            try:
                df = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
            except Exception:
                return False

            mask = (df["Event_ID"] == event_id) & (df["User_Email"].str.lower() == str(user_email).lower()) & (df["Status"].str.lower() != "sent")
            if mask.any():
                df.loc[mask, "Sent_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[mask, "Status"] = "Sent"
                with pd.ExcelWriter(self.notifications_file, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=self.notifications_sheet, index=False)
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to mark notification sent: {e}")
            return False

    # ---------------- Scheduler ----------------
    def start_notification_scheduler(self):
        """Start a background thread that runs check_and_send_reminders daily at configured time."""
        def scheduler():
            while True:
                try:
                    current_time = datetime.now().strftime("%H:%M")
                    # Run check once per day at 11:30 (adjust as needed)
                    if current_time == "11:30":
                        print("🔔 Running daily email notification check...")
                        self.check_and_send_reminders()
                        # sleep a bit to avoid double-run within same minute
                        time.sleep(70)
                except Exception as e:
                    print(f"❌ Scheduler error: {e}")
                time.sleep(60)

        t = threading.Thread(target=scheduler, daemon=True)
        t.start()
        print("✅ Email notification scheduler started")
