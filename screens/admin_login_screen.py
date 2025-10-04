from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.button import Button
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.app import App
from kivy.clock import Clock
from models.event_model import User


class AdminLoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.95, 0.95, 0.95, 1]

        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Top App Bar
        toolbar = MDTopAppBar(
            title="👨‍💼 Administrator Login",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=2,
            md_bg_color=[0.8, 0.3, 0.3, 1]
        )

        # Content
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="25dp",
            size_hint_y=None,
            padding="30dp"
        )
        content.bind(minimum_height=content.setter('height'))

        # Admin warning card
        warning_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="⚠️ RESTRICTED ACCESS",
                    font_style="H4",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    bold=True
                ),
                MDLabel(
                    text="This area is for system administrators only.\nUnauthorized access is prohibited.",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 0.9]
                ),
                orientation="vertical",
                spacing="10dp",
                padding="25dp"
            ),
            size_hint_y=None,
            height="120dp",
            md_bg_color=[0.8, 0.3, 0.3, 1],
            radius=[20],
            elevation=6
        )

        # Admin login form
        form_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🔐 Administrator Credentials",
                    font_style="H6",
                    theme_text_color="Primary",
                    bold=True,
                    halign="center"
                ),

                # Admin email field
                self.create_admin_email_field(),

                # Admin password field
                self.create_admin_password_field(),

                # Security code field
                self.create_security_code_field(),

                # Admin login button
                Button(
                    text="🚀 ADMIN LOGIN",
                    size_hint_y=None,
                    height="60dp",
                    background_color=[0.8, 0.3, 0.3, 1],
                    color=[1, 1, 1, 1],
                    font_size="18sp",
                    bold=True,
                    on_release=self.admin_login
                ),

                # Warning text
                MDLabel(
                    text="⚠️ Only authorized personnel with admin credentials can access this system",
                    font_style="Caption",
                    theme_text_color="Secondary",
                    halign="center"
                ),

                orientation="vertical",
                spacing="20dp",
                padding="30dp"
            ),
            size_hint_y=None,
            height="420dp",
            radius=[20],
            elevation=4,
            md_bg_color=[1, 1, 1, 1]
        )

        # Admin credentials info
        info_card = self.create_admin_info_card()

        content.add_widget(warning_card)
        content.add_widget(form_card)
        content.add_widget(info_card)

        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def create_admin_email_field(self):
        self.admin_email_field = MDTextField(
            hint_text="Administrator Email",
            helper_text="Enter admin@college.edu",
            helper_text_mode="persistent",
            mode="rectangle",
            line_color_focus=[0.8, 0.3, 0.3, 1],
            size_hint_y=None,
            height="70dp"
        )
        return self.admin_email_field

    def create_admin_password_field(self):
        self.admin_password_field = MDTextField(
            hint_text="Administrator Password",
            helper_text="Enter admin123",
            helper_text_mode="persistent",
            mode="rectangle",
            password=True,
            line_color_focus=[0.8, 0.3, 0.3, 1],
            size_hint_y=None,
            height="70dp"
        )
        return self.admin_password_field

    def create_security_code_field(self):
        self.security_code_field = MDTextField(
            hint_text="Security Code (Optional)",
            helper_text="Additional security verification",
            helper_text_mode="persistent",
            mode="rectangle",
            password=True,
            line_color_focus=[0.8, 0.3, 0.3, 1],
            size_hint_y=None,
            height="70dp"
        )
        return self.security_code_field

    def create_admin_info_card(self):
        return MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🔑 Default Admin Credentials",
                    font_style="H6",
                    theme_text_color="Primary",
                    bold=True
                ),
                MDLabel(
                    text="""📧 Email: admin@college.edu
🔒 Password: admin123

👨‍💼 Admin Capabilities:
• Create and manage all events
• Upload event posters
• View all student registrations  
• Export data to Excel files
• System analytics and reports
• Complete platform administration

🔒 Security Features:
• Excel database authentication
• Encrypted password storage
• Admin role verification""",
                    theme_text_color="Secondary",
                    font_style="Body2"
                ),
                orientation="vertical",
                spacing="15dp",
                padding="25dp"
            ),
            size_hint_y=None,
            height="280dp",
            elevation=2,
            radius=[15],
            md_bg_color=[1, 1, 0.9, 1]
        )

    def admin_login(self, *args):
        email = self.admin_email_field.text.strip().lower()
        password = self.admin_password_field.text.strip()
        security_code = self.security_code_field.text.strip()

        if not email or not password:
            self.show_error("Please enter admin email and password")
            return

        print(f"🔐 Admin login attempt: {email}")

        try:
            from utils.excel_db import ExcelUserDatabase
            excel_db = ExcelUserDatabase()
            success, user_data = excel_db.authenticate_admin_user(email, password, security_code)

            if success:
                print("✅ Admin authentication successful!")

                app = App.get_running_app()
                app.current_user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    student_id=user_data['student_id'],
                    department=user_data['department'],
                    year=user_data['year'],
                    interests=user_data['interests'],
                    is_admin=True
                )

                print(f"👨‍💼 Admin user object created: {app.current_user.name}")
                self.navigate_to_admin_dashboard_direct()

            else:
                self.show_error(f"❌ Admin Authentication Failed!\n\n{user_data}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error(f"Admin System Error!\n\nError: {str(e)}")

    def navigate_to_admin_dashboard_direct(self):
        """Navigate directly to admin dashboard"""
        print("🔄 Navigating to admin dashboard...")

        app = App.get_running_app()
        if 'admin_dashboard' in [s.name for s in app.sm.screens]:
            app.sm.current = 'admin_dashboard'
        else:
            try:
                from screens.admin_dashboard import AdminDashboard
                admin_screen = AdminDashboard(name='admin_dashboard')
                app.sm.add_widget(admin_screen)
                app.sm.current = 'admin_dashboard'
            except Exception as e:
                print(f"❌ Could not create admin dashboard: {e}")
                app.sm.current = 'home'

    def show_error(self, message):
        """Show error dialog"""
        self.dialog = MDDialog(
            title="🚫 Admin Access Denied",
            text=message,
            buttons=[
                Button(
                    text="Try Again",
                    background_color=[0.8, 0.3, 0.3, 1],
                    color=[1, 1, 1, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def go_back(self, *args):
        App.get_running_app().sm.current = 'home'
