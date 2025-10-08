# screens/admin_dashboard.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime
from plyer import filechooser
import calendar
import os
import pandas as pd


class AdminDashboard(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

        # Editing state
        self.editing_event_id = None

        # Poster and date selection variables
        self.selected_poster_path = None
        self.selected_day = None
        self.selected_month = None
        self.selected_year = None

        # Dropdown menus
        self.day_menu = None
        self.month_menu = None
        self.year_menu = None
        self.category_menu = None

        # Form fields
        self.title_field = None
        self.category_field = None
        self.time_field = None
        self.venue_field = None
        self.description_field = None
        self.capacity_field = None
        self.organizer_field = None
        self.day_field = None
        self.month_field = None
        self.year_field = None
        self.date_display = None
        self.poster_status = None

    # ---------------- Entry ----------------
    def on_enter(self):
        self.load_dashboard()

    # ---------------- DASHBOARD (Events Overview) ----------------
    def load_dashboard(self):
        self.clear_widgets()
        app = App.get_running_app()

        main_layout = MDBoxLayout(orientation="vertical")

        # Modern gradient-style toolbar
        toolbar = MDTopAppBar(
            title=f"👨‍💼 Admin Dashboard - {getattr(app.current_user, 'name', 'Admin')}",
            left_action_items=[["home", lambda x: self.go_home()]],
            right_action_items=[["logout", lambda x: self.logout()]],
            md_bg_color=[0.16, 0.50, 0.73, 1],  # Professional blue
            elevation=6
        )

        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing=dp(20),
                              size_hint_y=None, padding=dp(20))
        content.bind(minimum_height=content.setter("height"))

        # Header with gradient background card
        header_card = MDCard(
            MDLabel(text="📊 Events Overview", font_style="H5", bold=True,
                   halign="center", size_hint_y=None, height=dp(60)),
            size_hint_y=None, height=dp(80), 
            md_bg_color=[0.95, 0.96, 0.98, 1],  # Light gray-blue
            elevation=3, radius=[15], padding=dp(10)
        )
        content.add_widget(header_card)

        try:
            from utils.excel_db import ExcelUserDatabase
            db = ExcelUserDatabase()
            events = db.get_all_events()
        except Exception as e:
            events = []
            error_card = MDCard(
                MDLabel(text=f"⚠️ Error loading events: {e}", halign="center", 
                       theme_text_color="Error"),
                size_hint_y=None, height=dp(60), md_bg_color=[1, 0.95, 0.95, 1],
                elevation=2, radius=[12], padding=dp(10)
            )
            content.add_widget(error_card)

        if not events:
            empty_card = MDCard(
                MDLabel(text="📭 No events created yet\nCreate your first event below!", 
                       halign="center", font_style="Subtitle1"),
                size_hint_y=None, height=dp(100), md_bg_color=[0.98, 0.98, 1, 1],
                elevation=2, radius=[12], padding=dp(20)
            )
            content.add_widget(empty_card)
        else:
            for ev in events:
                # Color-coded cards based on capacity
                reg_count = ev.get('Registered_Count', 0)
                capacity = int(ev.get('Capacity', 100))
                fill_ratio = reg_count / capacity if capacity > 0 else 0
                
                if fill_ratio >= 0.9:
                    card_color = [1, 0.95, 0.95, 1]  # Light red - almost full
                elif fill_ratio >= 0.7:
                    card_color = [1, 0.98, 0.94, 1]  # Light orange - getting full
                else:
                    card_color = [0.95, 1, 0.95, 1]  # Light green - available
                
                card = MDCard(
                    MDBoxLayout(
                        MDBoxLayout(
                            MDLabel(text=f"🎉 {ev.get('Title','Untitled')}", 
                                   font_style="Subtitle1", bold=True,
                                   theme_text_color="Primary"),
                            MDLabel(
                                text=f"📅 {ev.get('Date','')} {ev.get('Time','')} | 📍 {ev.get('Venue','')}\n"
                                     f"👥 {ev.get('Registered_Count',0)}/{ev.get('Capacity','')} | 🏷️ {ev.get('Category','')}",
                                font_style="Caption", theme_text_color="Secondary"
                            ),
                            orientation="vertical", spacing=dp(8), size_hint_x=0.45
                        ),
                        MDBoxLayout(
                            MDRaisedButton(
                                text="ℹ️ Details", 
                                md_bg_color=[0.26, 0.63, 0.79, 1],  # Teal
                                text_color=[1, 1, 1, 1],
                                on_release=lambda x, e=ev: self.show_event_details(e)
                            ),
                            MDRaisedButton(
                                text="👥 Regs", 
                                md_bg_color=[0.40, 0.73, 0.42, 1],  # Green
                                text_color=[1, 1, 1, 1],
                                on_release=lambda x, e=ev: self.show_registrations(e)
                            ),
                            MDRaisedButton(
                                text="💬 Feedback",
                                md_bg_color=[0.2, 0.5, 0.8, 1],
                                text_color=[1, 1, 1, 1],
                                on_release=lambda x, e=ev: self.show_feedbacks(e)
                            ),
                            MDRaisedButton(
                                text="✏️ Edit",
                                md_bg_color=[1, 0.76, 0.03, 1],  # Amber
                                text_color=[0.2, 0.2, 0.2, 1],
                                on_release=lambda x, e=ev: self.load_event_form(e)
                            ),
                            MDRaisedButton(
                                text="🗑️ Del",
                                md_bg_color=[0.96, 0.26, 0.21, 1],  # Red
                                text_color=[1, 1, 1, 1],
                                on_release=lambda x, e=ev: self.confirm_delete_event(e)
                            ),
                            orientation="horizontal", spacing=dp(8), size_hint_x=0.55
                        ),
                        orientation="horizontal", spacing=dp(12), padding=dp(14)
                    ),
                    size_hint_y=None, height=dp(130), md_bg_color=card_color,
                    elevation=4, radius=[15]
                )
                content.add_widget(card)

        # Create button with gradient effect
        create_btn_card = MDCard(
            MDRaisedButton(
                text="➕ Create New Event",
                md_bg_color=[0.30, 0.69, 0.31, 1],  # Success green
                text_color=[1, 1, 1, 1],
                size_hint=(1, 1),
                font_style="Button",
                on_release=lambda x: self.load_event_form()
            ),
            size_hint_y=None, height=dp(60), elevation=6, radius=[15], padding=dp(5)
        )
        content.add_widget(create_btn_card)

        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    # ---------------- CREATE / EDIT FORM ----------------
    def load_event_form(self, event=None):
        self.clear_widgets()
        self.editing_event_id = event.get("Event_ID") if event else None

        if not event:
            self.selected_day = self.selected_month = self.selected_year = None
            self.selected_poster_path = None

        main_layout = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="✏️ Edit Event" if event else "📝 Create Event",
            left_action_items=[["arrow-left", lambda x: self.load_dashboard()]],
            md_bg_color=[0.30, 0.69, 0.31, 1] if not event else [1, 0.76, 0.03, 1],
            elevation=6
        )

        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing=dp(16),
                              size_hint_y=None, padding=dp(16))
        content.bind(minimum_height=content.setter("height"))

        form_card = self._build_event_form()

        if event:
            try:
                self.title_field.text = str(event.get("Title", ""))
                self.category_field.text = str(event.get("Category", ""))
                self.time_field.text = str(event.get("Time", ""))
                self.venue_field.text = str(event.get("Venue", ""))
                self.description_field.text = str(event.get("Description", ""))
                self.capacity_field.text = str(event.get("Capacity", ""))
                self.organizer_field.text = str(event.get("Organizer", ""))
                poster_path = event.get("Poster_Path")
                if poster_path:
                    self.selected_poster_path = poster_path
                    self.poster_status.text = f"✅ {os.path.basename(poster_path)}"
                    self.poster_status.theme_text_color = "Custom"
                    self.poster_status.text_color = [0.30, 0.69, 0.31, 1]
                date_val = str(event.get("Date", ""))
                if date_val and "-" in date_val:
                    parts = date_val.split("-")
                    if len(parts) == 3:
                        self.selected_year = int(parts[0])
                        self.selected_month = int(parts[1])
                        self.selected_day = int(parts[2])
                        self.year_field.text = str(self.selected_year)
                        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        self.month_field.text = months[self.selected_month - 1]
                        self.day_field.text = f"{self.selected_day:02d}"
                        self._update_date_display()
            except Exception:
                pass

        content.add_widget(form_card)
        scroll.add_widget(content)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    # ---------------- VIEW REGISTRATIONS ----------------
    def show_registrations(self, event):
        """Show all registered users for a specific event."""
        try:
            import pandas as pd
            from utils.excel_db import ExcelUserDatabase

            db = ExcelUserDatabase()
            regs_df = pd.read_excel(db.registrations_file, sheet_name=db.registrations_sheet)

            event_regs = regs_df[regs_df["Event_ID"] == event["Event_ID"]]

            if event_regs.empty:
                text = "📭 No registrations yet for this event."
            else:
                lines = []
                for _, r in event_regs.iterrows():
                    name = r.get("User_Name", "Unknown")
                    email = r.get("User_Email", "Unknown")
                    dept = r.get("Department", "")
                    year = r.get("Year", "")
                    lines.append(f"👤 {name} ({email}) — {dept} {year}")
                text = "\n".join(lines)

            self.dialog = MDDialog(
                title=f"👥 Registrations - {event.get('Title','')}",
                text=text,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        theme_text_color="Custom",
                        text_color=[0.26, 0.63, 0.79, 1],
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

        except Exception as e:
            self.dialog = MDDialog(
                title="⚠️ Error",
                text=f"Failed to load registrations: {e}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=[0.96, 0.26, 0.21, 1],
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

    # ---------------- VIEW FEEDBACKS ----------------
    def show_feedbacks(self, event):
        """Display all feedback for a specific event."""
        try:
            import pandas as pd
            from utils.excel_db import ExcelUserDatabase

            db = ExcelUserDatabase()
            feedback_file = os.path.join(db.project_root, "event_feedbacks.xlsx")
            feedback_sheet = "Feedbacks"

            if not os.path.exists(feedback_file):
                text = "📭 No feedback yet."
            else:
                df = pd.read_excel(feedback_file, sheet_name=feedback_sheet)
                event_feedback = df[df["Event_ID"] == event["Event_ID"]]

                if event_feedback.empty:
                    text = "📭 No feedback yet."
                else:
                    lines = []
                    for _, r in event_feedback.iterrows():
                        lines.append(f"👤 {r['User_Name']} ⭐ {r['Rating']}/5\n{r['Feedback']}\n")
                    text = "\n".join(lines)

            self.dialog = MDDialog(
                title=f"💬 Feedback - {event.get('Title','')}",
                text=text,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        theme_text_color="Custom",
                        text_color=[0.26, 0.63, 0.79, 1],
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

        except Exception as e:
            self.show_error(f"Failed to load feedback: {e}")

    # ---------------- EVENT DETAILS POPUP ----------------
    def show_event_details(self, event):
        """Display detailed information about the selected event in a popup."""
        try:
            title = event.get("Title", "Untitled Event")
            category = event.get("Category", "N/A")
            date = event.get("Date", "N/A")
            time = event.get("Time", "N/A")
            venue = event.get("Venue", "N/A")
            organizer = event.get("Organizer", "N/A")
            contact = str(event.get("Organizer_Contact", "Not Provided"))
            desc = event.get("Description", "No description available.")
            capacity = event.get("Capacity", "N/A")
            registered = event.get("Registered_Count", 0)

            text = (
                f"📌 {title}\n"
                f"🏷️ Category: {category}\n"
                f"📅 Date: {date} | 🕒 Time: {time}\n"
                f"📍 Venue: {venue}\n"
                f"👨‍🏫 Organizer: {organizer}\n"
                f"📞 Contact: {contact}\n"
                f"👥 Registered: {registered}/{capacity}\n\n"
                f"📝 Description:\n{desc}"
            )

            self.dialog = MDDialog(
                title="ℹ️ Event Details",
                text=text,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        theme_text_color="Custom",
                        text_color=[0.26, 0.63, 0.79, 1],
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

        except Exception as e:
            self.dialog = MDDialog(
                title="⚠️ Error",
                text=f"Failed to load event details:\n{e}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=[0.96, 0.26, 0.21, 1],
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

    # ---------------- DELETE EVENT ----------------
    def confirm_delete_event(self, event):
        """Ask for confirmation before deleting an event."""
        self.dialog = MDDialog(
            title="🗑️ Delete Event",
            text=f"Are you sure you want to delete:\n\n{event.get('Title', 'Untitled')}?",
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=[0.96, 0.26, 0.21, 1],  # Red
                    text_color=[1, 1, 1, 1],
                    on_release=lambda x, e=event: self._delete_event(e)
                )
            ]
        )
        self.dialog.open()

    def _delete_event(self, event):
        """Delete event from Excel database (Events + Registrations)."""
        try:
            import pandas as pd
            from utils.excel_db import ExcelUserDatabase

            db = ExcelUserDatabase()

            # Remove from Events sheet
            events_df = pd.read_excel(db.events_file, sheet_name=db.events_sheet)
            events_df = events_df[events_df["Event_ID"] != event["Event_ID"]]
            with pd.ExcelWriter(db.events_file, engine="openpyxl") as writer:
                events_df.to_excel(writer, sheet_name=db.events_sheet, index=False)

            # Remove related registrations
            regs_df = pd.read_excel(db.registrations_file, sheet_name=db.registrations_sheet)
            regs_df = regs_df[regs_df["Event_ID"] != event["Event_ID"]]
            with pd.ExcelWriter(db.registrations_file, engine="openpyxl") as writer:
                regs_df.to_excel(writer, sheet_name=db.registrations_sheet, index=False)

            self.dialog.dismiss()
            self.show_success(f"Event '{event.get('Title', '')}' deleted ✅")

            # Reload dashboard
            self.load_dashboard()

        except Exception as e:
            self.show_error(f"❌ Delete failed: {e}")

    # ---------------- Build Event Form ----------------
    def _build_event_form(self):
        form_layout = MDBoxLayout(orientation="vertical", spacing=dp(16),
                                  size_hint_y=None, adaptive_height=True)

        # Title
        self.title_field = MDTextField(
            hint_text="Event Title", 
            mode="rectangle",
            size_hint_y=None, height=dp(56),
            line_color_focus=[0.16, 0.50, 0.73, 1],
            hint_text_color_focus=[0.16, 0.50, 0.73, 1]
        )
        form_layout.add_widget(self.title_field)

        # Category Section
        cat_box = MDBoxLayout(orientation="vertical", spacing=dp(6),
                              size_hint_y=None, height=dp(95))
        cat_label = MDLabel(
            text="🏷️ Category", font_style="Subtitle2", bold=True,
            size_hint_y=None, height=dp(30), halign="left",
            theme_text_color="Custom", text_color=[0.26, 0.63, 0.79, 1]
        )
        cat_box.add_widget(cat_label)
        self.category_field = MDTextField(
            hint_text="Enter or Select Category", mode="rectangle",
            size_hint_y=None, height=dp(56),
            line_color_focus=[0.26, 0.63, 0.79, 1]
        )
        categories = ["Technical", "Cultural", "Sports", "Workshop", "Seminar",
                      "Placement", "Social", "Clubs", "Competitions", "Academic"]
        category_items = [{"viewclass": "OneLineListItem", "text": c,
                           "on_release": lambda x=c: self.select_category(x)}
                          for c in categories]
        self.category_menu = MDDropdownMenu(
            caller=self.category_field, items=category_items, width_mult=4
        )
        self.category_field.bind(
            on_focus=lambda i, f: self.category_menu.open() if f else None
        )
        cat_box.add_widget(self.category_field)
        form_layout.add_widget(cat_box)

        # Date Section
        date_box = MDBoxLayout(orientation="vertical", spacing=dp(6),
                               size_hint_y=None, height=dp(105))
        date_label = MDLabel(
            text="📅 Select Event Date", font_style="Subtitle2", bold=True,
            size_hint_y=None, height=dp(30), halign="left",
            theme_text_color="Custom", text_color=[0.40, 0.73, 0.42, 1]
        )
        date_box.add_widget(date_label)
        date_box.add_widget(self._create_date_picker_box())
        form_layout.add_widget(date_box)

        # Time
        self.time_field = MDTextField(
            hint_text="Event Time (HH:MM)", mode="rectangle",
            size_hint_y=None, height=dp(56),
            line_color_focus=[0.40, 0.73, 0.42, 1]
        )
        form_layout.add_widget(self.time_field)

        # Venue
        self.venue_field = MDTextField(
            hint_text="Venue", mode="rectangle",
            size_hint_y=None, height=dp(56),
            line_color_focus=[1, 0.76, 0.03, 1]
        )
        form_layout.add_widget(self.venue_field)

        # Description
        self.description_field = MDTextField(
            hint_text="Event Description", mode="rectangle", multiline=True,
            size_hint_y=None, height=dp(100),
            line_color_focus=[0.16, 0.50, 0.73, 1]
        )
        form_layout.add_widget(self.description_field)

        # Capacity, Organizer, and Contact row
        row = MDBoxLayout(spacing=dp(12), size_hint_y=None, height=dp(56))

        self.capacity_field = MDTextField(
            hint_text="Capacity",
            mode="rectangle",
            line_color_focus=[0.96, 0.26, 0.21, 1]
        )
        self.organizer_field = MDTextField(
            hint_text="Organizer Name",
            mode="rectangle",
            line_color_focus=[0.26, 0.63, 0.79, 1]
        )
        self.contact_field = MDTextField(
            hint_text="Organizer Contact (Phone/Email)",
            mode="rectangle",
            line_color_focus=[0.40, 0.73, 0.42, 1]
        )

        row.add_widget(self.capacity_field)
        row.add_widget(self.organizer_field)
        row.add_widget(self.contact_field)
        form_layout.add_widget(row)

        # Poster
        form_layout.add_widget(self._create_poster_upload_section())

        # Save Button
        save_btn = MDRaisedButton(
            text="✅ Save Event",
            md_bg_color=[0.30, 0.69, 0.31, 1],
            text_color=[1, 1, 1, 1],
            size_hint_y=None, height=dp(56),
            font_style="Button", elevation=4,
            on_release=self.create_event
        )
        form_layout.add_widget(save_btn)

        return MDCard(
            form_layout, padding=dp(16),
            md_bg_color=[0.98, 0.99, 1, 1],
            radius=[15], size_hint_y=None, adaptive_height=True,
            elevation=4
        )

    def select_category(self, cat):
        self.category_field.text = cat
        if self.category_menu:
            self.category_menu.dismiss()

    # ---------------- Date picker ----------------
    def _create_date_picker_box(self):
        row = MDBoxLayout(spacing=dp(10), size_hint_y=None, height=dp(60))

        self.day_field = MDTextField(
            hint_text="Day", mode="rectangle", readonly=True,
            size_hint=(None, None), size=(dp(80), dp(56)),
            line_color_focus=[0.40, 0.73, 0.42, 1]
        )
        day_layout = MDRelativeLayout(size_hint=(None, None), size=(dp(80), dp(56)))
        day_layout.add_widget(self.day_field)
        day_btn = MDIconButton(
            icon="menu-down", pos_hint={"center_y": 0.5, "right": 1},
            theme_text_color="Custom", text_color=[0.40, 0.73, 0.42, 1],
            on_release=lambda x: self._open_day_menu()
        )
        day_layout.add_widget(day_btn)

        self.month_field = MDTextField(
            hint_text="Month", mode="rectangle", readonly=True,
            size_hint=(None, None), size=(dp(110), dp(56)),
            line_color_focus=[0.40, 0.73, 0.42, 1]
        )
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_items = [{"viewclass": "OneLineListItem", "text": m,
                        "on_release": lambda x=i+1: self.select_month(x)}
                       for i, m in enumerate(months)]
        self.month_menu = MDDropdownMenu(
            caller=self.month_field, items=month_items, width_mult=4
        )
        month_layout = MDRelativeLayout(size_hint=(None, None), size=(dp(110), dp(56)))
        month_layout.add_widget(self.month_field)
        month_btn = MDIconButton(
            icon="menu-down", pos_hint={"center_y": 0.5, "right": 1},
            theme_text_color="Custom", text_color=[0.40, 0.73, 0.42, 1],
            on_release=lambda x: self.month_menu.open()
        )
        month_layout.add_widget(month_btn)

        self.year_field = MDTextField(
            hint_text="Year", mode="rectangle", readonly=True,
            size_hint=(None, None), size=(dp(90), dp(56)),
            line_color_focus=[0.40, 0.73, 0.42, 1]
        )
        this_year = datetime.now().year
        year_items = [{"viewclass": "OneLineListItem", "text": str(y),
                       "on_release": lambda x=y: self.select_year(x)}
                      for y in range(this_year, this_year + 6)]
        self.year_menu = MDDropdownMenu(
            caller=self.year_field, items=year_items, width_mult=3
        )
        year_layout = MDRelativeLayout(size_hint=(None, None), size=(dp(90), dp(56)))
        year_layout.add_widget(self.year_field)
        year_btn = MDIconButton(
            icon="menu-down", pos_hint={"center_y": 0.5, "right": 1},
            theme_text_color="Custom", text_color=[0.40, 0.73, 0.42, 1],
            on_release=lambda x: self.year_menu.open()
        )
        year_layout.add_widget(year_btn)

        row.add_widget(day_layout)
        row.add_widget(month_layout)
        row.add_widget(year_layout)

        self.date_display = MDLabel(
            text="No date selected", font_style="Caption", halign="center",
            theme_text_color="Secondary", size_hint_y=None, height=dp(28)
        )

        box = MDBoxLayout(orientation="vertical", spacing=dp(8))
        box.add_widget(row)
        box.add_widget(self.date_display)
        return box

    def _open_day_menu(self):
        today = datetime.now()
        year = self.selected_year or today.year
        month = self.selected_month or today.month
        days_in_month = calendar.monthrange(year, month)[1]
        start_day = today.day if (year == today.year and month == today.month) else 1
        day_items = [{"viewclass": "OneLineListItem", "text": f"{d:02d}",
                      "on_release": lambda x=d: self.select_day(x)}
                     for d in range(start_day, days_in_month + 1)]
        self.day_menu = MDDropdownMenu(caller=self.day_field, items=day_items, width_mult=3)
        self.day_menu.open()

    def select_day(self, d):
        self.selected_day = d
        self.day_field.text = f"{d:02d}"
        if self.day_menu:
            self.day_menu.dismiss()
        self._update_date_display()

    def select_month(self, m):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.selected_month = m
        self.month_field.text = months[m - 1]
        if self.month_menu:
            self.month_menu.dismiss()
        if self.selected_day and self.selected_year:
            maxd = calendar.monthrange(self.selected_year, self.selected_month)[1]
            if self.selected_day > maxd:
                self.selected_day = None
                self.day_field.text = ""
        self._update_date_display()

    def select_year(self, y):
        self.selected_year = y
        self.year_field.text = str(y)
        if self.year_menu:
            self.year_menu.dismiss()
        if self.selected_day and self.selected_month:
            maxd = calendar.monthrange(self.selected_year, self.selected_month)[1]
            if self.selected_day > maxd:
                self.selected_day = None
                self.day_field.text = ""
        self._update_date_display()

    def _update_date_display(self):
        if all([self.selected_day, self.selected_month, self.selected_year]):
            self.date_display.text = f"✅ {self.selected_day:02d}-{self.selected_month:02d}-{self.selected_year}"
            self.date_display.theme_text_color = "Custom"
            self.date_display.text_color = [0.30, 0.69, 0.31, 1]
            self.date_display.bold = True
        else:
            self.date_display.text = "Select Day, Month, Year"
            self.date_display.theme_text_color = "Secondary"
            self.date_display.bold = False

    def _get_formatted_date(self):
        if all([self.selected_day, self.selected_month, self.selected_year]):
            return f"{self.selected_year}-{self.selected_month:02d}-{self.selected_day:02d}"
        return None

    # ---------------- Poster Upload ----------------
    def _create_poster_upload_section(self):
        row = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(56))
        upload_btn = MDRaisedButton(
            text="📁 Choose Poster", 
            md_bg_color=[0.40, 0.73, 0.42, 1],
            text_color=[1, 1, 1, 1], 
            elevation=3,
            on_release=self._choose_poster
        )
        self.poster_status = MDLabel(
            text="No poster selected", 
            font_style="Caption", 
            size_hint_x=0.6,
            theme_text_color="Secondary"
        )
        row.add_widget(upload_btn)
        row.add_widget(self.poster_status)
        return row

    def _choose_poster(self, *args):
        try:
            filechooser.open_file(
                title="Choose Event Poster",
                filters=[("Image files", "*.jpg"), ("Image files", "*.png"), ("Image files", "*.jpeg")],
                on_selection=self._poster_selected
            )
        except Exception as e:
            self.show_error(f"File chooser not available: {e}")

    def _poster_selected(self, selection):
        if selection and len(selection) > 0:
            self.selected_poster_path = selection[0]
            self.poster_status.text = f"✅ {os.path.basename(selection[0])}"
            self.poster_status.theme_text_color = "Custom"
            self.poster_status.text_color = [0.30, 0.69, 0.31, 1]

    # ---------------- Create / Update ----------------
    def create_event(self, *args):
        if not self._validate_form_fields():
            return

        from utils.excel_db import ExcelUserDatabase
        db = ExcelUserDatabase()

        poster_path = None
        if self.selected_poster_path:
            try:
                success, poster_path = db.save_poster_image(self.selected_poster_path, "posters")
                if not success:
                    poster_path = None
            except Exception:
                poster_path = None

        if self.editing_event_id:
            try:
                events_df = pd.read_excel(db.events_file, sheet_name=db.events_sheet)
                idx = events_df[events_df["Event_ID"] == self.editing_event_id].index
                if not idx.empty:
                    row_idx = idx[0]
                    events_df.at[row_idx, "Title"] = self.title_field.text.strip()
                    events_df.at[row_idx, "Category"] = self.category_field.text.strip()
                    events_df.at[row_idx, "Date"] = self._get_formatted_date()
                    events_df.at[row_idx, "Time"] = self.time_field.text.strip()
                    events_df.at[row_idx, "Venue"] = self.venue_field.text.strip()
                    events_df.at[row_idx, "Description"] = self.description_field.text.strip()
                    events_df.at[row_idx, "Organizer"] = self.organizer_field.text.strip()
                    events_df.at[row_idx, "Capacity"] = self.capacity_field.text.strip()
                    if poster_path:
                        events_df.at[row_idx, "Poster_Path"] = poster_path
                    events_df.to_excel(db.events_file, sheet_name=db.events_sheet, index=False)
                    self.show_success("Event updated ✅")
                else:
                    self.show_error("Could not find event to update.")
            except Exception as e:
                self.show_error(f"Update failed: {e}")
                return
        else:
            try:
                success, event_id = db.create_event(
                    title=self.title_field.text.strip(),
                    category=self.category_field.text.strip(),
                    date=self._get_formatted_date(),
                    time=self.time_field.text.strip(),
                    venue=self.venue_field.text.strip(),
                    description=self.description_field.text.strip(),
                    organizer=self.organizer_field.text.strip(),
                    organizer_contact=self.contact_field.text.strip(),
                    capacity=self.capacity_field.text.strip(),
                    poster_path=poster_path
                )

                if success:
                    self.show_success(f"Event created ✅\nEvent ID: {event_id}")
                else:
                    self.show_error(f"Create failed: {event_id}")
                    return
            except Exception as e:
                self.show_error(f"Create error: {e}")
                return

        self.editing_event_id = None
        self.load_dashboard()

    # ---------------- Validation & Helpers ----------------
    def _validate_form_fields(self):
        if not self.title_field.text.strip():
            self.show_error("Enter event title")
            return False
        if not self.category_field.text.strip():
            self.show_error("Enter category")
            return False
        if not all([self.selected_day, self.selected_month, self.selected_year]):
            self.show_error("Select event date")
            return False
        if not self.time_field.text.strip():
            self.show_error("Enter time")
            return False
        if not self.venue_field.text.strip():
            self.show_error("Enter venue")
            return False
        if not self.capacity_field.text.strip():
            self.show_error("Enter capacity")
            return False
        try:
            datetime.strptime(self.time_field.text.strip(), "%H:%M")
        except Exception:
            self.show_error("Invalid time format. Use HH:MM (24-hour)")
            return False
        return True

    # ---------------- Dialog Feedback ----------------
    def show_success(self, msg):
        self.dialog = MDDialog(
            title="✅ Success",
            text=msg,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=[0.30, 0.69, 0.31, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def show_error(self, msg):
        self.dialog = MDDialog(
            title="❌ Error",
            text=msg,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=[0.96, 0.26, 0.21, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    # ---------------- Navigation ----------------
    def go_home(self, *args):
        App.get_running_app().sm.current = "home"

    def logout(self, *args):
        app = App.get_running_app()
        app.current_user = None
        app.sm.current = "home"