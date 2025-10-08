# screens/student_dashboard.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.button import Button
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivy.app import App
from widgets.event_card import EventCard
from kivy.metrics import dp
import pandas as pd
import os


class Dashboard(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.events = []
        self.events_container = None

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.96, 0.97, 1, 1]

        app = App.get_running_app()
        user = app.current_user

        if not user:
            app.sm.current = 'login'
            return

        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Toolbar
        toolbar = MDTopAppBar(
            title=f"👋 Welcome, {user.name.split()[0]}!",
            right_action_items=[
                ["account-circle", lambda x: self.show_profile()],
                ["logout", lambda x: self.logout()]
            ],
            md_bg_color=[0.1, 0.4, 0.9, 1],
            elevation=4
        )

        # Scrollable area
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            size_hint_y=None,
            padding=dp(20)
        )
        content.bind(minimum_height=content.setter('height'))

        # Add cards
        content.add_widget(self.create_welcome_card(user))
        content.add_widget(self.create_quick_actions_card())
        content.add_widget(self.create_events_section())

        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

        # Load events
        self.load_events()

    # ------------------- UI COMPONENTS -------------------

    def create_welcome_card(self, user):
        """Welcome banner card"""
        return MDCard(
            MDBoxLayout(
                MDBoxLayout(
                    MDLabel(
                        text=f"🎉 Welcome back, {user.name}!",
                        font_style="H5",
                        theme_text_color="Custom",
                        text_color=[1, 1, 1, 1],
                        bold=True
                    ),
                    MDLabel(
                        text=f"📚 {user.department} • {user.year}\n🎯 Interests: {', '.join(user.interests)}",
                        theme_text_color="Custom",
                        text_color=[1, 1, 1, 0.85]
                    ),
                    orientation="vertical",
                    spacing=dp(8),
                    size_hint_x=0.7
                ),
                MDBoxLayout(
                    MDLabel(text="🏆", font_style="H2", halign="center"),
                    MDLabel(text="Active\nStudent", font_style="Caption", halign="center",
                            theme_text_color="Custom", text_color=[1, 1, 1, 1]),
                    orientation="vertical",
                    size_hint_x=0.3
                ),
                orientation="horizontal",
                padding=dp(25),
                spacing=dp(15)
            ),
            size_hint_y=None,
            height=dp(120),
            elevation=6,
            md_bg_color=[0.1, 0.4, 0.9, 1],
            radius=[20]
        )

    def create_quick_actions_card(self):
        """Card with Browse, My Events, Settings"""
        actions_grid = MDGridLayout(cols=3, spacing=dp(15), size_hint_y=None, height=dp(100))

        actions = [
            ("📅", "Browse\nEvents", lambda x: self.load_events()),
            ("👥", "My Events", lambda x: self.go_to_my_events()),
            ("⚙️", "Settings", lambda x: self.show_settings())
        ]

        for emoji, text, action in actions:
            action_card = MDCard(
                MDBoxLayout(
                    MDLabel(text=emoji, font_style="H4", halign="center"),
                    MDLabel(text=text, font_style="Caption", halign="center", theme_text_color="Primary"),
                    orientation="vertical",
                    spacing=dp(5)
                ),
                elevation=3,
                radius=[15],
                md_bg_color=[1, 1, 1, 1],
                on_release=action
            )
            actions_grid.add_widget(action_card)

        return MDCard(
            MDBoxLayout(
                MDLabel(text="⚡ Quick Actions", font_style="H6", theme_text_color="Primary", bold=True),
                actions_grid,
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20)
            ),
            size_hint_y=None,
            height=dp(180),
            elevation=4,
            radius=[15],
            md_bg_color=[0.98, 0.99, 1, 1]
        )

    def create_events_section(self):
        """Container for all events"""
        layout = MDBoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        header = MDBoxLayout(
            MDLabel(
                text="🎪 All Events",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_x=0.7
            ),
            Button(
                text="⟳ Refresh",
                background_color=[0, 0, 0, 0],
                color=[0.1, 0.4, 0.9, 1],
                size_hint_x=0.3,
                size_hint_y=None,
                height=dp(40),
                on_release=self.load_events
            ),
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40)
        )

        # Event container
        self.events_container = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.events_container.bind(minimum_height=self.events_container.setter('height'))

        layout.add_widget(header)
        layout.add_widget(self.events_container)
        return layout

    # ------------------- LOAD EVENTS -------------------

    def load_events(self, *args):
        """Load all events from Excel"""
        self.events_container.clear_widgets()
        excel_file = "events_database.xlsx"

        if not os.path.exists(excel_file):
            self.events_container.add_widget(
                MDLabel(text="📭 No events file found. Ask admin to create events.", halign="center", theme_text_color="Secondary")
            )
            return

        try:
            events_df = pd.read_excel(excel_file, sheet_name="Events")

            if events_df.empty:
                self.events_container.add_widget(
                    MDLabel(text="📭 No events available.", halign="center", theme_text_color="Secondary")
                )
                return

            displayed = 0
            for _, event in events_df.iterrows():
                # Accept events with or without "Status" column
                if "Status" not in events_df.columns or str(event.get("Status", "Active")).lower() == "active":
                    event_data = event.to_dict()
                    event_card = EventCard(event_data=event_data)
                    self.events_container.add_widget(event_card)
                    displayed += 1

            if displayed == 0:
                self.events_container.add_widget(
                    MDLabel(text="📭 No active events right now.", halign="center", theme_text_color="Secondary")
                )

        except Exception as e:
            self.events_container.add_widget(
                MDLabel(text=f"⚠️ Error loading events: {e}", halign="center", theme_text_color="Error")
            )

    # ------------------- USER ACTIONS -------------------

    def go_to_my_events(self, *args):
        App.get_running_app().sm.current = 'my_events'

    def show_profile(self, *args):
        app = App.get_running_app()
        user = app.current_user
        self.dialog = MDDialog(
            title="👤 Your Profile",
            text=f"""📧 Email: {user.email}
🆔 Student ID: {user.student_id}
🏫 Department: {user.department}
📚 Academic Year: {user.year}
🎯 Interests: {', '.join(user.interests)}""",
            buttons=[Button(text="Close", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

    def show_settings(self, *args):
        self.dialog = MDDialog(
            title="⚙️ Settings",
            text="Notifications, preferences, and settings managed by admin.",
            buttons=[Button(text="Close", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

    def logout(self, *args):
        app = App.get_running_app()
        app.current_user = None
        app.sm.current = 'home'
