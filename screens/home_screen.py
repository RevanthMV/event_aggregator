# screens/home_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.app import App
from utils.excel_db import ExcelUserDatabase


class HomeScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()

        main_layout = MDFloatLayout()
        top_section = self.create_curved_header()
        content_section = self.create_content_section()

        main_layout.add_widget(top_section)
        main_layout.add_widget(content_section)
        self.add_widget(main_layout)

    def create_curved_header(self):
        """Top header with app title and tagline"""
        return MDCard(
            MDBoxLayout(
                MDLabel(
                    text="Event Aggregator",
                    font_style="H3",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    halign="center",
                    bold=True,
                    size_hint_y=None,
                    height="80dp"
                ),
                MDLabel(
                    text="Campus Events Made Simple",
                    font_style="Subtitle1",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 0.9],
                    halign="center",
                    size_hint_y=None,
                    height="40dp"
                ),
                orientation="vertical",
                spacing="10dp",
                padding=["20dp", "60dp", "20dp", "40dp"]
            ),
            size_hint=(1, 0.35),
            pos_hint={'x': 0, 'top': 1},
            md_bg_color=[0.11, 0.35, 0.67, 1],
            radius=[0, 0, 30, 30],
            elevation=8
        )

    def create_content_section(self):
        """Scrollable content with login cards + event preview"""
        scroll = MDScrollView(
            size_hint=(0.95, 0.6),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        content = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            size_hint_y=None,
            padding="10dp"
        )
        content.bind(minimum_height=content.setter('height'))

        # Add cards for student/admin
        content.add_widget(self.create_student_card())
        content.add_widget(self.create_admin_card())

        # Add upcoming events
        events_box = self.create_events_preview()
        content.add_widget(events_box)

        scroll.add_widget(content)
        return scroll

    def create_student_card(self):
        """Student access card"""
        return MDCard(
            MDBoxLayout(
                MDBoxLayout(
                    MDCard(
                        MDLabel(
                            text="🎓",
                            font_style="H4",
                            halign="center",
                            theme_text_color="Custom",
                            text_color=[1, 1, 1, 1]
                        ),
                        size_hint=(None, None),
                        size=("55dp", "55dp"),
                        md_bg_color=[0.11, 0.35, 0.67, 1],
                        radius=[12],
                        elevation=0,
                        pos_hint={'center_y': 0.5}
                    ),
                    MDBoxLayout(
                        MDLabel(
                            text="Student Access",
                            font_style="H6",
                            theme_text_color="Primary",
                            bold=True,
                            size_hint_y=None,
                            height="30dp"
                        ),
                        MDLabel(
                            text="• Browse and register for events\n• View personalized activities\n• Track your registrations",
                            font_style="Body2",
                            theme_text_color="Secondary",
                            size_hint_y=None,
                            height="80dp"
                        ),
                        orientation="vertical",
                        spacing="5dp"
                    ),
                    orientation="horizontal",
                    spacing="15dp",
                    size_hint_x=0.65
                ),
                MDBoxLayout(
                    Button(
                        text="Register",
                        size_hint_y=None,
                        height="45dp",
                        background_color=[0.13, 0.59, 0.25, 1],
                        color=[1, 1, 1, 1],
                        font_size="15sp",
                        bold=True,
                        on_release=self.go_to_student_register
                    ),
                    Button(
                        text="Login",
                        size_hint_y=None,
                        height="45dp",
                        background_color=[0.11, 0.35, 0.67, 1],
                        color=[1, 1, 1, 1],
                        font_size="15sp",
                        bold=True,
                        on_release=self.go_to_student_login
                    ),
                    orientation="vertical",
                    spacing="10dp",
                    size_hint_x=0.35
                ),
                orientation="horizontal",
                spacing="15dp",
                padding="20dp"
            ),
            size_hint_y=None,
            height="160dp",
            elevation=4,
            radius=[15],
            md_bg_color=[1, 1, 1, 1]
        )

    def create_admin_card(self):
        """Admin access card"""
        return MDCard(
            MDBoxLayout(
                MDBoxLayout(
                    MDCard(
                        MDLabel(
                            text="🛠️",
                            font_style="H4",
                            halign="center",
                            theme_text_color="Custom",
                            text_color=[1, 1, 1, 1]
                        ),
                        size_hint=(None, None),
                        size=("55dp", "55dp"),
                        md_bg_color=[0.64, 0.16, 0.16, 1],
                        radius=[12],
                        elevation=0,
                        pos_hint={'center_y': 0.5}
                    ),
                    MDBoxLayout(
                        MDLabel(
                            text="Administrator Access",
                            font_style="H6",
                            theme_text_color="Primary",
                            bold=True,
                            size_hint_y=None,
                            height="30dp"
                        ),
                        MDLabel(
                            text="• Create and manage events\n• Upload posters\n• Monitor registrations\n• View analytics",
                            font_style="Body2",
                            theme_text_color="Secondary",
                            size_hint_y=None,
                            height="80dp"
                        ),
                        orientation="vertical",
                        spacing="5dp"
                    ),
                    orientation="horizontal",
                    spacing="15dp",
                    size_hint_x=0.65
                ),
                MDBoxLayout(
                    Button(
                        text="Admin Login",
                        size_hint_y=None,
                        height="50dp",
                        background_color=[0.64, 0.16, 0.16, 1],
                        color=[1, 1, 1, 1],
                        font_size="15sp",
                        bold=True,
                        on_release=self.go_to_admin_login
                    ),
                    MDLabel(
                        text="Restricted Access",
                        font_style="Caption",
                        theme_text_color="Secondary",
                        halign="center",
                        size_hint_y=None,
                        height="20dp"
                    ),
                    orientation="vertical",
                    spacing="8dp",
                    size_hint_x=0.35
                ),
                orientation="horizontal",
                spacing="15dp",
                padding="20dp"
            ),
            size_hint_y=None,
            height="160dp",
            elevation=4,
            radius=[15],
            md_bg_color=[1, 1, 1, 1]
        )

    def create_events_preview(self):
        """Displays a small preview of upcoming events from Excel"""
        db = ExcelUserDatabase()
        events = db.get_upcoming_events() if hasattr(db, "get_upcoming_events") else []

        box = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        title_lbl = MDLabel(text="🎉 Upcoming Events", font_style="H6", halign="left",
                            theme_text_color="Primary", size_hint_y=None, height=dp(30))
        box.add_widget(title_lbl)

        if not events:
            box.add_widget(MDLabel(text="📭 No upcoming events found.", halign="center",
                                   theme_text_color="Secondary"))
        else:
            for ev in events[:3]:
                card = MDCard(
                    MDBoxLayout(
                        MDLabel(
                            text=f"🎯 {ev.get('Title', 'Untitled')}\n📅 {ev.get('Date', '')} | 📍 {ev.get('Venue', '')}",
                            font_style="Body1",
                            theme_text_color="Primary",
                            halign="left"
                        ),
                        orientation="vertical", padding=10
                    ),
                    size_hint_y=None, height=dp(80),
                    md_bg_color=[0.96, 0.97, 1, 1], radius=[10], elevation=2
                )
                box.add_widget(card)

        return MDCard(box, size_hint_y=None, height=dp(280), radius=[15], elevation=3)

    # ---------------- NAVIGATION ----------------
    def go_to_student_register(self, *args):
        print("🔄 Navigating to student registration...")
        App.get_running_app().sm.current = 'register'

    def go_to_student_login(self, *args):
        print("🔄 Navigating to student login...")
        App.get_running_app().sm.current = 'login'

    def go_to_admin_login(self, *args):
        print("🔄 Navigating to admin login...")
        App.get_running_app().sm.current = 'admin_login'
