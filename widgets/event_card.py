# widgets/event_card.py
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivy.uix.button import Button
from kivy.app import App
import os


class EventCard(MDCard):
    def __init__(self, event_data, **kwargs):
        super().__init__(**kwargs)
        self.event_data = event_data
        
        # Card styling
        self.size_hint_y = None
        self.height = "200dp"
        self.elevation = 4
        self.radius = [15]
        self.md_bg_color = [1, 1, 1, 1]
        self.padding = "10dp"

        # Category color palette
        self.category_colors = {
            'Technical': [0.2, 0.4, 0.9, 1],
            'Cultural': [0.9, 0.2, 0.6, 1],
            'Sports': [0.2, 0.8, 0.2, 1],
            'Placement': [0.8, 0.4, 0.1, 1],
            'Social': [0.6, 0.2, 0.8, 1],
            'Clubs': [0.9, 0.5, 0.1, 1],
        }

        self.create_card_content()

    def create_card_content(self):
        """Creates a nicely structured event card layout"""
        main_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="15dp",
            padding=("10dp", "10dp", "10dp", "10dp")
        )

        # 🖼️ Left: Poster (if exists)
        poster_path = self.event_data.get('Poster_Path', '')
        if isinstance(poster_path, str) and os.path.exists(poster_path):
            poster = FitImage(
                source=poster_path,
                size_hint_x=0.3,
                radius=[12, 0, 0, 12]
            )
            main_layout.add_widget(poster)
            info_width = 0.7
        else:
            info_width = 1.0

        # 🧾 Middle: Event Info
        info_layout = MDBoxLayout(
            orientation="vertical",
            spacing="5dp",
            size_hint_x=info_width
        )

        title = self.event_data.get('Title', 'Untitled Event')
        category = self.event_data.get('Category', 'General')
        date = self.event_data.get('Date', 'TBD')
        time = self.event_data.get('Time', 'TBD')
        venue = self.event_data.get('Venue', 'TBD')
        organizer = self.event_data.get('Organizer', 'Unknown')
        capacity = self.event_data.get('Capacity', 0)

        # Title Label
        title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )

        # Event details with emojis
        details = (
            f"🏷️ {category}\n"
            f"📅 {date}  ⏰ {time}\n"
            f"📍 {venue}"
        )
        details_label = MDLabel(
            text=details,
            font_style="Body2",
            theme_text_color="Secondary"
        )

        # Organizer and capacity
        extra_label = MDLabel(
            text=f"👨‍🏫 {organizer} • 👥 Max: {capacity}",
            font_style="Caption",
            theme_text_color="Hint"
        )

        info_layout.add_widget(title_label)
        info_layout.add_widget(details_label)
        info_layout.add_widget(extra_label)

        # 🎨 Right: Actions
        action_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.3,
            spacing="8dp"
        )

        color = self.category_colors.get(category, [0.4, 0.4, 0.4, 1])

        category_badge = MDCard(
            MDLabel(
                text=category[:3].upper(),
                halign="center",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
                bold=True,
                font_style="Caption"
            ),
            size_hint=(None, None),
            size=("55dp", "25dp"),
            radius=[12],
            md_bg_color=color,
            elevation=2
        )

        view_btn = Button(
            text="View Details",
            size_hint_y=None,
            height="35dp",
            background_color=color,
            color=[1, 1, 1, 1],
            on_release=self.view_event_details
        )

        register_btn = Button(
            text="Quick Register →",
            size_hint_y=None,
            height="30dp",
            background_color=[0, 0, 0, 0],
            color=color,
            on_release=self.quick_register
        )

        action_layout.add_widget(category_badge)
        action_layout.add_widget(view_btn)
        action_layout.add_widget(register_btn)

        main_layout.add_widget(info_layout)
        main_layout.add_widget(action_layout)

        self.add_widget(main_layout)

    def view_event_details(self, *args):
        """Navigate to event details screen"""
        app = App.get_running_app()
        app.selected_event = self.event_data
        app.sm.current = 'event_details'

    def quick_register(self, *args):
        """Handles quick registration logic"""
        app = App.get_running_app()
        user = app.current_user
        if not user:
            app.sm.current = 'login'
            return

        try:
            from utils.excel_db import ExcelUserDatabase
            db = ExcelUserDatabase()
            success, message = db.register_user_for_event(
                event_id=self.event_data.get('Event_ID'),
                user_email=user.email,
                user_name=user.name,
                student_id=user.student_id
            )
            if success:
                print(f"✅ Quick registered for {self.event_data.get('Title')}")
                app.selected_event = self.event_data
                app.sm.current = 'event_details'
            else:
                from kivymd.uix.dialog import MDDialog
                dialog = MDDialog(title="Registration Failed", text=str(message))
                dialog.open()
        except Exception as e:
            print("⚠️ Quick register error:", e)
            app.selected_event = self.event_data
            app.sm.current = 'event_details'
