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
from models.event_model import User


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.96, 0.97, 1, 1]  # Soft background
        
        # Main layout
        main_layout = MDBoxLayout(orientation="vertical", spacing="10dp")
        
        # Top App Bar
        toolbar = MDTopAppBar(
            title="🔑 Event Aggregator Login",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=4,
            md_bg_color=[0.09, 0.35, 0.77, 1],  # Gradient base blue
            specific_text_color=[1, 1, 1, 1],
        )
        
        # Content (scrollable for smaller screens)
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="25dp",
            size_hint_y=None,
            padding=["20dp", "40dp", "20dp", "40dp"]
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Welcome card
        welcome_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🎓 Welcome to Event Aggregator",
                    font_style="H5",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    bold=True,
                    size_hint_y=None,
                    height="40dp"
                ),
                MDLabel(
                    text="Secure login with Excel database verification",
                    font_style="Subtitle1",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 0.9],
                    size_hint_y=None,
                    height="30dp"
                ),
                orientation="vertical",
                spacing="5dp",
                padding="15dp"
            ),
            size_hint_y=None,
            height="120dp",
            md_bg_color=[0.09, 0.35, 0.77, 1],
            radius=[20],
            elevation=6
        )
        
        # Login form card
        form_card = MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🔐 Login Credentials",
                    font_style="H6",
                    theme_text_color="Primary",
                    bold=True,
                    size_hint_y=None,
                    height="30dp"
                ),
                
                # Email field
                self.create_email_field(),
                
                # Password field
                self.create_password_field(),
                
                # Login button
                Button(
                    text="🚀 LOGIN",
                    size_hint_y=None,
                    height="50dp",
                    background_color=[0.09, 0.35, 0.77, 1],
                    color=[1, 1, 1, 1],
                    font_size="16sp",
                    bold=True,
                    on_release=self.login_user
                ),
                
                # Register link
                Button(
                    text="Don't have an account? Register →",
                    background_color=[0, 0, 0, 0],
                    color=[0.09, 0.35, 0.77, 1],
                    size_hint_y=None,
                    height="40dp",
                    on_release=self.go_to_register
                ),
                
                orientation="vertical",
                spacing="20dp",
                padding="25dp"
            ),
            size_hint_y=None,
            height="380dp",
            radius=[20],
            elevation=4
        )
        
        content.add_widget(welcome_card)
        content.add_widget(form_card)
        
        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def create_email_field(self):
        """Create email input field"""
        self.email_field = MDTextField(
            hint_text="Your Registered Email",
            helper_text="📧 Enter email from Excel database",
            helper_text_mode="persistent",
            mode="rectangle",
            line_color_focus=[0.09, 0.35, 0.77, 1],
            size_hint_y=None,
            height="70dp"
        )
        return self.email_field
    
    def create_password_field(self):
        """Create password input field"""
        self.password_field = MDTextField(
            hint_text="Your Password",
            helper_text="🔒 Enter your secure password",
            helper_text_mode="persistent",
            mode="rectangle",
            password=True,
            line_color_focus=[0.09, 0.35, 0.77, 1],
            size_hint_y=None,
            height="70dp"
        )
        return self.password_field
    
    def login_user(self, *args):
        """Authenticate user from Excel database ONLY"""
        email = self.email_field.text.strip().lower()
        password = self.password_field.text.strip()
        
        # Validation
        if not email or not password:
            self.show_error("Please enter both email and password")
            return
        
        if "@" not in email or "." not in email:
            self.show_error("Please enter a valid email address")
            return
        
        # Authenticate from Excel database ONLY
        try:
            from utils.excel_db import ExcelUserDatabase
            excel_db = ExcelUserDatabase()
            success, user_data = excel_db.authenticate_user(email, password)
            
            if success:
                # Create user object
                app = App.get_running_app()
                app.current_user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    student_id=user_data['student_id'],
                    department=user_data['department'],
                    year=user_data['year'],
                    interests=user_data['interests'],
                    is_admin=user_data['is_admin']
                )
                
                if user_data['is_admin']:
                    print(f"✅ Admin login successful: {user_data['name']}")
                    app.sm.current = 'admin_dashboard'
                else:
                    print(f"✅ Student login successful: {user_data['name']}")
                    app.sm.current = 'dashboard'
                    
            else:
                self.show_error("❌ Invalid email or password.\nPlease try again or register first.")
                
        except Exception as e:
            print(f"Login error: {e}")
            self.show_error(f"Database Error!\n\nCould not connect to user database.\n\nError: {str(e)}")
    
    def show_error(self, message):
        """Show error dialog"""
        self.dialog = MDDialog(
            title="⚠️ Login Error",
            text=message,
            buttons=[
                Button(
                    text="Try Again",
                    size_hint_y=None,
                    height="40dp",
                    background_color=[0.9, 0.3, 0.3, 1],
                    color=[1, 1, 1, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()
    
    def go_to_register(self, *args):
        """Navigate to register"""
        App.get_running_app().sm.current = 'register'
    
    def go_back(self, *args):
        """Navigate back to home"""
        App.get_running_app().sm.current = 'home'
