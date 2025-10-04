# screens/my_events.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivy.app import App
from datetime import datetime, date
from utils.event_registration_manager import EventRegistrationManager
from utils.excel_db import ExcelUserDatabase
import math


def _to_date_safe(val):
    """Convert value to date.date or return None.
       Handles datetime, date, pandas.Timestamp, strings (YYYY-MM-DD or with time),
       and NaN floats.
    """
    if val is None:
        return None
    # NaN floats from pandas
    try:
        if isinstance(val, float) and math.isnan(val):
            return None
    except Exception:
        pass

    from datetime import datetime, date
    # if already datetime/date
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val

    # string-ish values
    try:
        s = str(val).strip()
        if not s:
            return None
        # try common formats
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                pass
        # last resort: let dateutil parse if available
        try:
            from dateutil.parser import parse as _parse
            return _parse(s).date()
        except Exception:
            return None
    except Exception:
        return None


class MyEventsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.current_view = "registered"  # registered, past, stats

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.96, 0.97, 1, 1]

        app = App.get_running_app()
        user = app.current_user
        if not user:
            app.sm.current = 'login'
            return

        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        toolbar = MDTopAppBar(
            title="👥 My Events",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["refresh", lambda x: self.refresh_events()]],
            md_bg_color=[0.6, 0.2, 0.8, 1],
            elevation=4
        )

        # Navigation buttons
        nav_layout = MDBoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="60dp")

        self.registered_btn = MDRaisedButton(
            text="✅ Registered Events",
            size_hint_x=0.33,
            md_bg_color=[0.6, 0.2, 0.8, 1] if self.current_view == "registered" else [0.8, 0.8, 0.8, 1],
            on_release=lambda x: self.switch_view("registered")
        )

        self.past_btn = MDRaisedButton(
            text="📚 Past Events",
            size_hint_x=0.33,
            md_bg_color=[0.6, 0.2, 0.8, 1] if self.current_view == "past" else [0.8, 0.8, 0.8, 1],
            on_release=lambda x: self.switch_view("past")
        )

        self.stats_btn = MDRaisedButton(
            text="📊 Statistics",
            size_hint_x=0.33,
            md_bg_color=[0.6, 0.2, 0.8, 1] if self.current_view == "stats" else [0.8, 0.8, 0.8, 1],
            on_release=lambda x: self.switch_view("stats")
        )

        nav_layout.add_widget(self.registered_btn)
        nav_layout.add_widget(self.past_btn)
        nav_layout.add_widget(self.stats_btn)

        # Content area
        self.content_area = MDBoxLayout(orientation="vertical")
        self.load_current_view()

        main_layout.add_widget(toolbar)
        main_layout.add_widget(nav_layout)
        main_layout.add_widget(self.content_area)
        self.add_widget(main_layout)

    def switch_view(self, view_name):
        self.current_view = view_name
        self.registered_btn.md_bg_color = [0.6, 0.2, 0.8, 1] if view_name == "registered" else [0.8, 0.8, 0.8, 1]
        self.past_btn.md_bg_color = [0.6, 0.2, 0.8, 1] if view_name == "past" else [0.8, 0.8, 0.8, 1]
        self.stats_btn.md_bg_color = [0.6, 0.2, 0.8, 1] if view_name == "stats" else [0.8, 0.8, 0.8, 1]
        self.content_area.clear_widgets()
        self.load_current_view()

    def load_current_view(self):
        if self.current_view == "registered":
            content = self.create_registered_events_section()
        elif self.current_view == "past":
            content = self.create_past_events_section()
        else:
            content = self.create_statistics_section()
        self.content_area.add_widget(content)

    # ---------------- REGISTERED EVENTS ----------------
    def create_registered_events_section(self):
        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing="15dp", size_hint_y=None, padding="20dp")
        content.bind(minimum_height=content.setter('height'))

        header = MDCard(MDLabel(text="🎪 Your Upcoming Events", halign="center", font_style="H6"),
                        size_hint_y=None, height=80)
        content.add_widget(header)

        registered_events = self.get_registered_events()
        if not registered_events:
            content.add_widget(MDLabel(text="📅 No Registered Events", halign="center"))
        else:
            for event in registered_events:
                content.add_widget(self.create_registered_event_card(event))

        scroll.add_widget(content)
        return scroll

    def create_registered_event_card(self, event):
        left = MDBoxLayout(orientation="vertical", spacing=5, size_hint_x=0.7)
        title = MDLabel(text=f"🎉 {event.get('Event_Title', 'Event')}", font_style="Subtitle1", bold=True)
        reg_date = MDLabel(text=f"📅 Registered: {event.get('Registration_Date', 'Unknown')}", font_style="Caption")
        left.add_widget(title)
        left.add_widget(reg_date)

        right = MDBoxLayout(orientation="vertical", spacing=5, size_hint_x=0.3)
        right.add_widget(MDRaisedButton(text="View Details", on_release=lambda x, e=event: self.view_event_details(e)))
        right.add_widget(MDFlatButton(text="Unregister", theme_text_color="Custom",
                                      text_color=[0.9, 0.3, 0.3, 1], on_release=lambda x, e=event: self.unregister_from_event(e)))

        return MDCard(MDBoxLayout(left, right, orientation="horizontal", spacing=15, padding=20),
                      size_hint_y=None, height=120, elevation=3, radius=[10])

    # ---------------- PAST EVENTS ----------------
    def create_past_events_section(self):
        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing="15dp", size_hint_y=None, padding="20dp")
        content.bind(minimum_height=content.setter('height'))

        header = MDCard(MDLabel(text="📚 Past Events", halign="center", font_style="H6"),
                        size_hint_y=None, height=80)
        content.add_widget(header)

        past_events = self.get_past_events()
        if not past_events:
            content.add_widget(MDLabel(text="📚 No Past Events", halign="center"))
        else:
            for event in past_events:
                content.add_widget(self.create_past_event_card(event))

        scroll.add_widget(content)
        return scroll

    def create_past_event_card(self, event):
        status = event.get("Status", "Past")
        cancel_date = event.get("Cancelled_Date", None)
        label_text = f"📅 Status: {status}"
        if cancel_date:
            label_text += f"\n❌ Cancelled on {cancel_date}"

        left = MDLabel(text="❌" if status.lower() == "cancelled" else "✅", font_style="H4", size_hint_x=None, width=40)
        middle = MDBoxLayout(orientation="vertical", spacing=5)
        middle.add_widget(MDLabel(text=event.get("Event_Title", "Event"), font_style="Subtitle1", bold=True))
        middle.add_widget(MDLabel(text=label_text, font_style="Caption"))

        return MDCard(MDBoxLayout(left, middle, orientation="horizontal", spacing=15, padding=20),
                      size_hint_y=None, height=100, elevation=2, radius=[10])

    # ---------------- STATS ----------------
    def create_statistics_section(self):
        return MDLabel(text="📊 Stats Coming Soon", halign="center")

    # ---------------- EVENT OPERATIONS ----------------
    def get_registered_events(self):
        try:
            app = App.get_running_app()
            user = app.current_user
            manager = EventRegistrationManager()
            regs = manager.get_user_registrations(user.email)
            today = datetime.now().date()

            result = []
            for r in regs:
                status = str(r.get("Status", "")).lower()
                # Keep active/registered future events as "registered"
                if status in ("registered", "active"):
                    ev_date_raw = r.get("Event_Date")
                    ev_date = _to_date_safe(ev_date_raw)
                    # If event date absent -> keep it (we don't filter)
                    if ev_date is None or ev_date >= today:
                        result.append(r)
            return result
        except Exception as e:
            print("Error fetching registered events:", e)
            return []

    def get_past_events(self):
        try:
            app = App.get_running_app()
            user = app.current_user
            manager = EventRegistrationManager()
            regs = manager.get_user_registrations(user.email)
            today = datetime.now().date()

            past = []
            for r in regs:
                status = str(r.get("Status", "")).lower()
                if status == "cancelled":
                    past.append(r)
                elif status in ("registered", "active"):
                    ev_date_raw = r.get("Event_Date")
                    ev_date = _to_date_safe(ev_date_raw)
                    if ev_date and ev_date < today:
                        past.append(r)
            return past
        except Exception as e:
            print("Error fetching past events:", e)
            return []

    def unregister_from_event(self, event):
        self.dialog = MDDialog(
            title="🚪 Unregister from Event",
            text=f"Are you sure you want to unregister from {event.get('Event_Title', 'this event')}?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Unregister", md_bg_color=[0.9, 0.3, 0.3, 1],
                               on_release=lambda x, e=event: self.confirm_unregister(e))
            ],
        )
        self.dialog.open()

    def confirm_unregister(self, event):
        if self.dialog:
            self.dialog.dismiss()
        try:
            app = App.get_running_app()
            user = app.current_user
            if not user:
                self.show_info("❌ Error", "No user logged in")
                return

            manager = EventRegistrationManager()
            success, msg = manager.unregister_student_from_event(event["Event_ID"], user.email)

            if success:
                self.show_info("✅ Unregistered", msg)
                self.refresh_events()
                # try refresh event details too
                try:
                    if 'event_details' in app.sm.screen_names:
                        app.sm.get_screen('event_details').on_enter()
                except Exception:
                    pass
            else:
                self.show_info("⚠️ Failed", msg)
        except Exception as e:
            self.show_info("❌ Error", str(e))

    def view_event_details(self, event):
        app = App.get_running_app()
        try:
            excel_db = ExcelUserDatabase()
            full_event = excel_db.get_event_by_id(event.get("Event_ID"))
            if full_event is None:
                full_event = {
                    "Event_ID": event.get("Event_ID"),
                    "Title": event.get("Event_Title"),
                    "Date": event.get("Event_Date", ""),
                    "Time": event.get("Event_Time", ""),
                    "Venue": event.get("Venue", ""),
                    "Organizer": event.get("Organizer", ""),
                    "Description": event.get("Description", ""),
                    "Capacity": event.get("Capacity", 0),
                    "Category": event.get("Category", "General")
                }
        except Exception as e:
            print("Error loading full event details:", e)
            full_event = {
                "Event_ID": event.get("Event_ID"),
                "Title": event.get("Event_Title")
            }

        app.selected_event = full_event
        app.sm.current = "event_details"

    def show_info(self, title, message):
        self.dialog = MDDialog(title=title, text=message, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def refresh_events(self, *args):
        self.on_enter()

    def go_back(self, *args):
        App.get_running_app().sm.current = "dashboard"
