# screens/event_details.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp
from utils.event_registration_manager import EventRegistrationManager
from datetime import datetime
import re, webbrowser, os


def _wrap_label(text, font_style="Body1", padding_x=40):
    lbl = MDLabel(
        text=text or "",
        font_style=font_style,
        size_hint_y=None,
        halign="left",
        valign="top",
        theme_text_color="Secondary",
    )
    lbl.text_size = (max(Window.width - dp(padding_x), dp(200)), None)
    lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
    return lbl


class EventDetailsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.event_data = None

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.96, 0.97, 1, 1]

        app = App.get_running_app()
        self.event_data = app.selected_event

        if not self.event_data:
            app.sm.current = 'dashboard'
            return

        main_layout = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title="📅 Event Details",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["share", lambda x: self.share_event()]],
            md_bg_color=[0.1, 0.4, 0.9, 1],
            elevation=4
        )

        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", spacing=20, size_hint_y=None, padding=20)
        content.bind(minimum_height=content.setter("height"))

        # ---------------- POSTER SECTION (Improved) ----------------
        poster_path = self.event_data.get("Poster_Path", "")

        if isinstance(poster_path, str) and poster_path.strip():
            if "," in poster_path:
                carousel = Carousel(direction="right", size_hint_y=None, height=dp(260))
                for p in [pp.strip() for pp in poster_path.split(",") if os.path.exists(pp.strip())]:
                    img = Image(
                        source=p,
                        allow_stretch=True,
                        keep_ratio=True,
                        size_hint=(1, None),
                        height=dp(250)
                    )
                    carousel.add_widget(
                        MDCard(
                            img,
                            size_hint_y=None,
                            height=dp(250),
                            radius=[20],
                            elevation=6,
                            md_bg_color=[1, 1, 1, 1],
                            padding=10
                        )
                    )
                if len(carousel.slides) > 0:
                    content.add_widget(carousel)
            elif os.path.exists(poster_path.strip()):
                img = Image(
                    source=poster_path.strip(),
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(1, None),
                    height=dp(250)
                )
                content.add_widget(
                    MDCard(
                        img,
                        size_hint_y=None,
                        height=dp(260),
                        radius=[20],
                        elevation=6,
                        md_bg_color=[1, 1, 1, 1],
                        padding=10
                    )
                )

        # ---------------- MAIN EVENT DETAILS ----------------
        content.add_widget(self.create_event_header())
        content.add_widget(self.create_details_layout())
        content.add_widget(self.create_event_stats_card())
        content.add_widget(self.create_registration_section())

    
        # Contact Info (Optional)
        if "Organizer_Contact" in self.event_data:
            contact_value = self.event_data.get("Organizer_Contact", "Not Available")

            # Ensure it’s a clean string (avoid NaN, None, or numeric values)
            if contact_value is None or str(contact_value).strip().lower() in ("nan", ""):
                contact_value = "Not Available"

            contact_box = MDBoxLayout(orientation="vertical", padding=15, spacing=10, size_hint_y=None)
            contact_box.add_widget(MDLabel(text="📞 Contact Info", font_style="H6", theme_text_color="Primary"))
            contact_box.add_widget(MDLabel(
                text=str(contact_value),  # 👈 convert to string safely
                font_style="Body1",
                theme_text_color="Secondary"
            ))
            content.add_widget(MDCard(contact_box, size_hint_y=None, height=dp(120), radius=[12], elevation=3))


        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    # ---------------- HEADER ----------------
    def create_event_header(self):
        category_colors = {
            'Technical': [0.2, 0.4, 0.9, 1], 'Cultural': [0.9, 0.2, 0.6, 1],
            'Sports': [0.2, 0.8, 0.2, 1], 'Placement': [0.8, 0.4, 0.1, 1],
            'Social': [0.6, 0.2, 0.8, 1], 'Clubs': [0.9, 0.5, 0.1, 1]
        }

        category = self.event_data.get('Category', 'General')
        bg_color = category_colors.get(category, [0.5, 0.5, 0.5, 1])

        title = MDLabel(
            text=self.event_data.get('Title', 'Event Title'),
            font_style="H4",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            bold=True,
            size_hint_y=None,
            halign="left"
        )
        title.text_size = (max(Window.width - dp(80), dp(200)), None)
        title.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))

        meta = MDLabel(
            text=f"📅 {self.event_data.get('Date', 'TBD')} at {self.event_data.get('Time', 'TBD')}\n"
                 f"📍 {self.event_data.get('Venue', 'TBD')}\n"
                 f"👨‍🏫 {self.event_data.get('Organizer', 'TBD')}",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.9],
            size_hint_y=None,
            halign="left"
        )
        meta.text_size = (max(Window.width - dp(80), dp(200)), None)
        meta.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))

        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=30, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        cat_lbl = MDLabel(
            text=f"🏷️ {category}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            halign="center",
            size_hint_y=None
        )
        cat_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))

        layout.add_widget(cat_lbl)
        layout.add_widget(title)
        layout.add_widget(meta)

        return MDCard(layout, size_hint_y=None, height=layout.minimum_height,
                      elevation=6, md_bg_color=bg_color, radius=[20])

    # ---------------- DETAILS ----------------
    def create_details_layout(self):
        details_container = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        details_container.bind(minimum_height=details_container.setter('height'))

        description = self.event_data.get("Description", "")
        if not description.strip():
            box = MDBoxLayout(padding=12, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            box.add_widget(_wrap_label("No description available for this event."))
            details_container.add_widget(MDCard(box, elevation=3, radius=[12]))
            return details_container

        pattern = re.compile(r'\n([A-Z][A-Z\s()]+)\n')
        parts = pattern.split(description.strip())

        overview_text = parts[0].strip()
        if overview_text:
            box = MDBoxLayout(orientation="vertical", spacing=8, padding=12, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            heading = MDLabel(text="📖 Overview", font_style="H6", theme_text_color="Primary",
                              size_hint_y=None, height=dp(30))
            box.add_widget(heading)
            box.add_widget(_wrap_label(overview_text))
            details_container.add_widget(MDCard(box, size_hint_y=None, elevation=3,
                                                radius=[12], md_bg_color=[1, 1, 1, 1]))

        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            content = parts[i + 1].strip()
            if not header or not content:
                continue
            panel_content_layout = MDBoxLayout(padding=(dp(15), dp(15), dp(15), dp(25)), size_hint_y=None)
            panel_content_layout.bind(minimum_height=panel_content_layout.setter('height'))
            panel_content_layout.add_widget(_wrap_label(content, padding_x=50))

            panel = MDExpansionPanel(
                content=panel_content_layout,
                panel_cls=MDExpansionPanelOneLine(text=header, font_style="Subtitle1")
            )
            details_container.add_widget(panel)

        return details_container

    # ---------------- STATS ----------------
    def create_event_stats_card(self):
        capacity = int(self.event_data.get('Capacity', 100))
        registered = self.get_registered_count()
        available = capacity - registered

        grid = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None, height=dp(120))
        stats_data = [
            ("👥 Capacity", str(capacity)),
            ("✅ Registered", str(registered)),
            ("📊 Available", f"{available} spots left"),
            ("🎯 Category", self.event_data.get('Category', 'General'))
        ]
        for label, value in stats_data:
            stat_card = MDCard(
                MDBoxLayout(
                    MDLabel(text=label, font_style="Caption", theme_text_color="Secondary", halign="center"),
                    MDLabel(text=value, font_style="Subtitle2", theme_text_color="Primary", halign="center", bold=True),
                    orientation="vertical", spacing=5, padding=10
                ),
                elevation=2, radius=[10], md_bg_color=[0.95, 0.98, 1, 1]
            )
            grid.add_widget(stat_card)

        container = MDBoxLayout(orientation="vertical", padding=10, size_hint_y=None, height=dp(140))
        container.add_widget(grid)
        return MDCard(container, size_hint_y=None, height=dp(150),
                      elevation=3, radius=[12], md_bg_color=[1, 1, 1, 1])

    def get_registered_count(self):
        try:
            manager = EventRegistrationManager()
            regs = manager.get_event_registrations(self.event_data['Event_ID'])
            return len([r for r in regs if str(r.get("Status", "")).lower() in ("registered", "active")])
        except Exception:
            return 0

    # ---------------- REGISTER / UNREGISTER ----------------
    def create_registration_section(self):
        app = App.get_running_app()
        user = app.current_user
        if not user:
            return MDCard(MDLabel(text="🔒 Please login to register", halign="center"))

        is_registered = self.check_registration_status(user.email)
        capacity = int(self.event_data.get('Capacity', 100))
        registered = self.get_registered_count()

        if is_registered:
            box = MDBoxLayout(orientation="vertical", padding=20, spacing=12, size_hint_y=None)
            lbl = MDLabel(text="✅ You're Registered!", font_style="H6", halign="center",
                          theme_text_color="Custom", text_color=[0.2, 0.7, 0.2, 1])
            box.add_widget(lbl)
            box.add_widget(MDFlatButton(text="Unregister", text_color=[1, 1, 1, 1],
                                        md_bg_color=[0.9, 0.3, 0.3, 1],
                                        pos_hint={'center_x': 0.5},
                                        on_release=lambda x: self.unregister_from_event()))
            return MDCard(box, size_hint_y=None, height=dp(150), radius=[15], elevation=4)
        elif registered >= capacity:
            return MDCard(MDLabel(text="😔 Event Full", halign="center"), size_hint_y=None, height=dp(150))
        else:
            box = MDBoxLayout(orientation="vertical", padding=20, spacing=12, size_hint_y=None)
            box.add_widget(MDLabel(text="🎟️ Register for this Event", font_style="H6", halign="center"))
            box.add_widget(MDRaisedButton(text="🎉 REGISTER NOW", size_hint_y=None, height=dp(55),
                                          md_bg_color=[0.2, 0.8, 0.2, 1],
                                          pos_hint={'center_x': 0.5},
                                          on_release=self.register_for_event))
            return MDCard(box, size_hint_y=None, height=dp(150), radius=[15], elevation=4)

    def check_registration_status(self, user_email):
        try:
            manager = EventRegistrationManager()
            regs = manager.get_user_registrations(user_email)
            for r in regs:
                if r.get('Event_ID') == self.event_data['Event_ID'] and str(r.get('Status', '')).lower() in ("registered", "active"):
                    return True
            return False
        except Exception:
            return False

    def register_for_event(self, *args):
        app = App.get_running_app()
        user = app.current_user
        manager = EventRegistrationManager()
        success, msg = manager.register_student_for_event(self.event_data['Event_ID'], user.email)
        if success:
            self.show_success("🎉 Registered", msg)
            if 'my_events' in app.sm.screen_names:
                app.sm.get_screen('my_events').refresh_events()
            self.on_enter()
        else:
            self.show_error("Registration Failed", msg)

    def unregister_from_event(self, *args):
        self.dialog = MDDialog(
            title="🚪 Unregister from Event",
            text=f"Are you sure you want to unregister from {self.event_data.get('Title')}?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Unregister", md_bg_color=[0.9, 0.3, 0.3, 1],
                               on_release=lambda x: self.confirm_unregister())
            ],
        )
        self.dialog.open()

    def confirm_unregister(self, *args):
        if self.dialog: self.dialog.dismiss()
        app = App.get_running_app()
        user = app.current_user
        manager = EventRegistrationManager()
        success, msg = manager.unregister_student_from_event(self.event_data['Event_ID'], user.email)
        if success:
            self.show_success("✅ Unregistered", msg)
            if 'my_events' in app.sm.screen_names:
                app.sm.get_screen('my_events').refresh_events()
            self.on_enter()
        else:
            self.show_error("Unregister Failed", msg)

    # ---------------- SIMILAR & SHARE ----------------
    def create_similar_events(self):
        category = self.event_data.get('Category', 'General')
        box = MDBoxLayout(orientation="vertical", spacing=12, padding=20, size_hint_y=None)
        box.add_widget(MDLabel(text=f"🔍 More {category} Events", font_style="H6", theme_text_color="Primary"))
        box.add_widget(MDRaisedButton(text=f"Browse All {category} Events →", md_bg_color=[0.98, 0.99, 1, 1],
                                     on_release=self.browse_similar_events, pos_hint={'center_x': 0.5}))
        return MDCard(box, size_hint_y=None, height=dp(120), radius=[15], elevation=2, md_bg_color=[0.98, 0.99, 1, 1])

    def browse_similar_events(self, *args):
        App.get_running_app().sm.current = 'dashboard'

    def share_event(self, *args):
        """Share event details with icons"""
        event = self.event_data
        share_text = (
            f"🎉 Check out this event: {event.get('Title', 'Event')}\n\n"
            f"📅 Date: {event.get('Date', 'TBD')}\n"
            f"🕒 Time: {event.get('Time', 'TBD')}\n"
            f"📍 Venue: {event.get('Venue', 'TBD')}\n"
            f"👨‍🏫 Organizer: {event.get('Organizer', 'TBD')}\n\n"
            "Don’t miss it! 🚀"
        )

        grid = MDGridLayout(cols=4, spacing=20, padding=20, adaptive_height=True)

        platforms = [
            ("content-copy", "Copy", lambda: Clipboard.copy(share_text)),
            ("whatsapp", "WhatsApp", lambda: webbrowser.open(f"https://wa.me/?text={share_text.replace(' ', '%20')}")),
            ("gmail", "Gmail", lambda: webbrowser.open(f"mailto:?subject=Event: {event.get('Title')}&body={share_text}")),
            ("twitter", "Twitter", lambda: webbrowser.open(f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20')}")),
            ("linkedin", "LinkedIn", lambda: webbrowser.open(f"https://www.linkedin.com/shareArticle?mini=true&title={event.get('Title')}&summary={share_text.replace(' ', '%20')}")),
            ("telegram", "Telegram", lambda: webbrowser.open(f"https://t.me/share/url?url={share_text.replace(' ', '%20')}")),
            ("facebook", "Facebook", lambda: webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={share_text.replace(' ', '%20')}")),
            ("instagram", "Instagram", lambda: webbrowser.open("https://www.instagram.com/"))
        ]

        for icon, label, action in platforms:
            box = MDBoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=dp(80))
            btn = MDIconButton(
                icon=icon,
                icon_size=dp(32),
                pos_hint={"center_x": 0.5},
                on_release=lambda x, act=action: (self.dialog.dismiss(), act())
            )
            lbl = MDLabel(text=label, font_style="Caption", halign="center", size_hint_y=None, height=dp(20))
            box.add_widget(btn)
            box.add_widget(lbl)
            grid.add_widget(box)

        grid.add_widget(MDIconButton(icon="close-circle", icon_size=dp(32),
                                     pos_hint={"center_x": 0.5}, on_release=lambda x: self.dialog.dismiss()))

        self.dialog = MDDialog(title="📤 Share Event", type="custom", content_cls=grid)
        self.dialog.open()

    # ---------------- HELPERS ----------------
    def show_success(self, title, msg):
        self.dialog = MDDialog(title=title, text=msg,
                               buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def show_error(self, title, msg):
        self.dialog = MDDialog(title=title, text=msg,
                               buttons=[MDFlatButton(text="Close", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def go_back(self, *args):
        App.get_running_app().sm.current = 'dashboard'
         # ---------------- HELPERS ----------------
    def go_back(self, *args):
        App.get_running_app().sm.current = 'dashboard'

