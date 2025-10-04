import pandas as pd
import os
import uuid
from datetime import datetime
from utils.email_notifications import EmailNotificationSystem


class EventRegistrationManager:
    def __init__(self):
        self.registrations_file = "event_registrations.xlsx"
        self.registrations_sheet = "Event_Registrations"
        self.users_file = "users_database.xlsx"
        self.events_file = "events_database.xlsx"
        self.notifications_file = "event_notifications.xlsx"
        self.notifications_sheet = "Notifications"

        self.ensure_initialized()
        # ✅ Gmail + App Password (store securely in production)
        self.email_sys = EmailNotificationSystem(
            sender_email="revanthrajreddy@gmail.com",
            sender_password="quxdquurovojgzdx"
        )

    def ensure_initialized(self):
        """Ensure all Excel sheets exist"""
        if not os.path.exists(self.registrations_file):
            df = pd.DataFrame(columns=[
                'Registration_ID', 'Event_ID', 'Event_Title', 'User_Email',
                'User_Name', 'Student_ID', 'Department', 'Year',
                'Registration_Date', 'Notification_Sent', 'Status', 'Cancelled_Date'
            ])
            with pd.ExcelWriter(self.registrations_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.registrations_sheet, index=False)
            print(f"✅ Created {self.registrations_file}")

        if not os.path.exists(self.notifications_file):
            df = pd.DataFrame(columns=[
                "Notification_ID", "Event_ID", "User_Email", "Message", "Sent_Date", "Status"
            ])
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.notifications_sheet, index=False)
            print(f"✅ Created {self.notifications_file}")

    # ---------------- REGISTER ----------------
    def register_student_for_event(self, event_id, user_email):
        try:
            # Load Users
            users_df = pd.read_excel(self.users_file, sheet_name="Users")
            user_match = users_df[users_df['Email'].str.lower() == user_email.lower()]
            if user_match.empty:
                return False, "User not found"
            user = user_match.iloc[0]

            # Load Events
            events_df = pd.read_excel(self.events_file, sheet_name="Events")
            event_match = events_df[events_df['Event_ID'] == event_id]
            if event_match.empty:
                return False, "Event not found"
            event = event_match.iloc[0]

            # Load Registrations
            try:
                regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            except:
                regs_df = pd.DataFrame(columns=[
                    'Registration_ID', 'Event_ID', 'Event_Title', 'User_Email',
                    'User_Name', 'Student_ID', 'Department', 'Year',
                    'Registration_Date', 'Notification_Sent', 'Status', 'Cancelled_Date'
                ])

            # Already registered? (allow re-register if Cancelled)
            existing = regs_df[
                (regs_df['Event_ID'] == event_id) &
                (regs_df['User_Email'].str.lower() == user_email.lower())
            ]
            if not existing.empty:
                latest_status = str(existing.iloc[-1]['Status']).lower()
                if latest_status in ("registered", "active"):
                    return False, "Already registered for this event"
                elif latest_status == "cancelled":
                    # remove cancelled record so new registration is possible
                    regs_df = regs_df.drop(existing.index)

            # Capacity check (count only Registered/Active)
            current_registrations = len(regs_df[(regs_df['Event_ID'] == event_id) &
                                                (regs_df['Status'].str.lower().isin(['registered', 'active']))])
            if current_registrations >= int(event['Capacity']):
                return False, "Event is full"

            # New Registration
            reg_id = str(uuid.uuid4())[:8].upper()
            new_registration = {
                'Registration_ID': reg_id,
                'Event_ID': event_id,
                'Event_Title': event['Title'],
                'User_Email': user_email.lower(),
                'User_Name': user['Name'],
                'Student_ID': user['Student_ID'],
                'Department': user['Department'],
                'Year': user['Year'],
                'Registration_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Notification_Sent': False,
                'Status': 'Registered',
                'Cancelled_Date': ''
            }
            regs_df = pd.concat([regs_df, pd.DataFrame([new_registration])], ignore_index=True)
            with pd.ExcelWriter(self.registrations_file, engine='openpyxl') as writer:
                regs_df.to_excel(writer, sheet_name=self.registrations_sheet, index=False)

            # Update Event count
            events_df.loc[events_df['Event_ID'] == event_id, 'Registered_Count'] = len(
                regs_df[(regs_df['Event_ID'] == event_id) &
                        (regs_df['Status'].str.lower().isin(['registered', 'active']))]
            )
            with pd.ExcelWriter(self.events_file, engine='openpyxl') as writer:
                events_df.to_excel(writer, sheet_name='Events', index=False)

            # Log into Notifications
            notif_id = str(uuid.uuid4())[:8].upper()
            notif_row = {
                "Notification_ID": notif_id,
                "Event_ID": event_id,
                "User_Email": user_email.lower(),
                "Message": f"Confirmation: Registered for {event['Title']}",
                "Sent_Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Status": "Sent"
            }
            notifs = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
            notifs = pd.concat([notifs, pd.DataFrame([notif_row])], ignore_index=True)
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                notifs.to_excel(writer, sheet_name=self.notifications_sheet, index=False)

            # ✅ Send confirmation email immediately
            self.email_sys.send_registration_confirmation(user_email, event.to_dict())

            return True, f"Successfully registered for {event['Title']}! Confirmation email sent."
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    # ---------------- UNREGISTER ----------------
    def unregister_student_from_event(self, event_id, user_email):
        """Cancel a student's registration"""
        try:
            regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            match = (regs_df['Event_ID'] == event_id) & (regs_df['User_Email'].str.lower() == user_email.lower())

            if regs_df[match].empty:
                return False, "No registration found"

            # Mark as Cancelled + store date
            regs_df.loc[match, 'Status'] = 'Cancelled'
            regs_df.loc[match, 'Cancelled_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with pd.ExcelWriter(self.registrations_file, engine='openpyxl') as writer:
                regs_df.to_excel(writer, sheet_name=self.registrations_sheet, index=False)

            # Update Event count (only Registered/Active)
            events_df = pd.read_excel(self.events_file, sheet_name="Events")
            events_df.loc[events_df['Event_ID'] == event_id, 'Registered_Count'] = len(
                regs_df[(regs_df['Event_ID'] == event_id) &
                        (regs_df['Status'].str.lower().isin(['registered', 'active']))]
            )
            with pd.ExcelWriter(self.events_file, engine='openpyxl') as writer:
                events_df.to_excel(writer, sheet_name='Events', index=False)

            # Log cancellation in Notifications
            notif_id = str(uuid.uuid4())[:8].upper()
            notif_row = {
                "Notification_ID": notif_id,
                "Event_ID": event_id,
                "User_Email": user_email.lower(),
                "Message": f"Cancellation: Unregistered from event {event_id}",
                "Sent_Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Status": "Sent"
            }
            notifs = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
            notifs = pd.concat([notifs, pd.DataFrame([notif_row])], ignore_index=True)
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                notifs.to_excel(writer, sheet_name=self.notifications_sheet, index=False)

            # Send cancellation email
            self.email_sys.send_email(
                user_email,
                f"❌ Cancelled Registration for Event {event_id}",
                f"You have successfully cancelled your registration for event {event_id}."
            )

            return True, f"Unregistered successfully from event {event_id}."
        except Exception as e:
            return False, f"Unregister failed: {str(e)}"

    # ---------------- Helpers ----------------
    def get_event_registrations(self, event_id):
        try:
            regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            return regs_df[regs_df['Event_ID'] == event_id].to_dict('records')
        except Exception as e:
            print(f"❌ Error getting registrations: {e}")
            return []

    def get_user_registrations(self, user_email):
        try:
            regs_df = pd.read_excel(self.registrations_file, sheet_name=self.registrations_sheet)
            return regs_df[regs_df['User_Email'].str.lower() == user_email.lower()].to_dict('records')
        except Exception as e:
            print(f"❌ Error getting user registrations: {e}")
            return []

    def mark_notification_sent(self, notif_id):
        """Mark notification as Sent in event_notifications.xlsx"""
        try:
            df = pd.read_excel(self.notifications_file, sheet_name=self.notifications_sheet)
            df.loc[df['Notification_ID'] == notif_id, ['Sent_Date','Status']] = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Sent"
            ]
            with pd.ExcelWriter(self.notifications_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.notifications_sheet, index=False)
            return True
        except Exception as e:
            print(f"❌ Error updating notification: {e}")
            return False
