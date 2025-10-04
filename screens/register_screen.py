from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.button import Button
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.app import App
from kivy.clock import Clock

class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_interests = set()
        self.step = 1
        self.total_steps = 3

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.98, 0.99, 1, 1]
        
        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")
        
        # Premium Top App Bar
        toolbar = MDTopAppBar(
            title="🎓 Student Registration",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["help-circle", lambda x: self.show_help()]],
            elevation=4,
            md_bg_color=[0.1, 0.3, 0.8, 1]
        )
        
        # Progress indicator
        progress_card = self.create_progress_indicator()
        
        # Main content scroll
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="25dp",
            size_hint_y=None,
            padding="20dp"
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Hero section
        hero_card = self.create_hero_section()
        
        # Registration form based on step
        form_card = self.create_current_step_form()
        
        # Navigation buttons
        nav_card = self.create_navigation_buttons()
        
        # Footer info
        footer_card = self.create_footer_section()
        
        content.add_widget(hero_card)
        content.add_widget(form_card)
        content.add_widget(nav_card)
        content.add_widget(footer_card)
        
        scroll.add_widget(content)
        main_layout.add_widget(toolbar)
        main_layout.add_widget(progress_card)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def create_progress_indicator(self):
        """Create progress indicator"""
        progress_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="15dp",
            padding="20dp"
        )
        
        # Step indicators
        for i in range(1, self.total_steps + 1):
            if i <= self.step:
                color = [0.1, 0.8, 0.3, 1]
                text_color = [1, 1, 1, 1]
            else:
                color = [0.9, 0.9, 0.9, 1]
                text_color = [0.6, 0.6, 0.6, 1]
            
            step_card = MDCard(
                MDLabel(
                    text=str(i),
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=text_color,
                    halign="center",
                    bold=True
                ),
                size_hint=(None, None),
                size=("40dp", "40dp"),
                md_bg_color=color,
                radius=[20],
                elevation=3 if i <= self.step else 1
            )
            progress_layout.add_widget(step_card)
            
            # Add connector line (except for last step)
            if i < self.total_steps:
                connector = MDLabel(
                    text="━━━",
                    theme_text_color="Custom",
                    text_color=[0.1, 0.8, 0.3, 1] if i < self.step else [0.9, 0.9, 0.9, 1],
                    size_hint_x=0.3
                )
                progress_layout.add_widget(connector)
        
        # Progress text
        progress_text = MDLabel(
            text=f"Step {self.step} of {self.total_steps} • {int((self.step/self.total_steps)*100)}% Complete",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="right"
        )
        progress_layout.add_widget(progress_text)
        
        return MDCard(
            progress_layout,
            size_hint_y=None,
            height="80dp",
            elevation=2,
            radius=[0, 0, 15, 15],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_hero_section(self):
        """Create hero section"""
        step_info = {
            1: ("👋 Welcome to Event Aggregator", "Join thousands of students discovering amazing campus events.\nLet's start with your basic information."),
            2: ("🎯 Choose Your Interests", "Select your interests to receive personalized event recommendations\ntailored just for you."),
            3: ("🔐 Secure Your Account", "Set up your secure login credentials and complete\nyour registration process.")
        }
        
        title, desc = step_info[self.step]
        
        return MDCard(
            MDBoxLayout(
                MDLabel(
                    text=title,
                    font_style="H4",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    halign="center",
                    bold=True
                ),
                MDLabel(
                    text=desc,
                    font_style="Body1",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 0.9],
                    halign="center"
                ),
                orientation="vertical",
                spacing="15dp",
                padding="30dp"
            ),
            size_hint_y=None,
            height="140dp",
            elevation=8,
            radius=[25],
            md_bg_color=[0.1, 0.4, 0.9, 1]
        )
    
    def create_current_step_form(self):
        """Create form based on current step"""
        if self.step == 1:
            return self.create_step1_personal_info()
        elif self.step == 2:
            return self.create_step2_interests()
        else:
            return self.create_step3_credentials()
    
    def create_step1_personal_info(self):
        """Step 1: Personal Information Form"""
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="30dp"
        )
        
        # Form title
        form_layout.add_widget(
            MDLabel(
                text="📝 Personal Information",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height="40dp"
            )
        )
        
        # Name field
        self.full_name_field = self.create_simple_textfield("Full Name", "Enter your complete name")
        form_layout.add_widget(self.full_name_field)
        
        # Student ID field
        self.student_id_field = self.create_simple_textfield("Student ID", "Your college student ID")
        form_layout.add_widget(self.student_id_field)
        
        # Email field
        self.email_address_field = self.create_simple_textfield("Email Address", "Your college email address")
        form_layout.add_widget(self.email_address_field)
        
        # Department field
        self.department_field = self.create_simple_textfield("Department", "e.g., Computer Science, MBA")
        form_layout.add_widget(self.department_field)
        
        # Year field
        self.year_field = self.create_simple_textfield("Academic Year", "e.g., 1st Year, 2nd Year")
        form_layout.add_widget(self.year_field)
        
        return MDCard(
            form_layout,
            size_hint_y=None,
            height="450dp",
            elevation=6,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_step2_interests(self):
        """Step 2: Interest Selection"""
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="30dp"
        )
        
        # Title
        form_layout.add_widget(
            MDLabel(
                text="🎯 Select Your Interests",
                font_style="H6",
                theme_text_color="Primary",
                bold=True
            )
        )
        
        # Description
        form_layout.add_widget(
            MDLabel(
                text="Choose categories you're interested in to receive personalized event recommendations:",
                font_style="Body2",
                theme_text_color="Secondary"
            )
        )
        
        # Interests grid
        interests_grid = self.create_interests_grid()
        form_layout.add_widget(interests_grid)
        
        # Selection count
        form_layout.add_widget(
            MDLabel(
                text=f"✅ Selected: {len(self.selected_interests)} interests",
                font_style="Caption",
                theme_text_color="Primary",
                halign="center"
            )
        )
        
        return MDCard(
            form_layout,
            size_hint_y=None,
            height="450dp",
            elevation=6,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_step3_credentials(self):
        """Step 3: Account Credentials"""
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="30dp"
        )
        
        # Title
        form_layout.add_widget(
            MDLabel(
                text="🔐 Secure Your Account",
                font_style="H6",
                theme_text_color="Primary",
                bold=True
            )
        )
        
        # Description
        form_layout.add_widget(
            MDLabel(
                text="Create secure login credentials for your account:",
                font_style="Body2",
                theme_text_color="Secondary"
            )
        )
        
        # Password field
        self.password_field = self.create_simple_textfield("Password", "Enter secure password", password=True)
        form_layout.add_widget(self.password_field)
        
        # Confirm password field
        self.confirm_password_field = self.create_simple_textfield("Confirm Password", "Re-enter your password", password=True)
        form_layout.add_widget(self.confirm_password_field)
        
        # Terms checkbox
        terms_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height="40dp"
        )
        
        self.terms_checkbox = MDCheckbox(
            size_hint_x=None,
            width="30dp",
            active=False
        )
        
        terms_label = MDLabel(
            text="I agree to the Terms & Conditions and Privacy Policy",
            font_style="Body2",
            theme_text_color="Secondary"
        )
        
        terms_layout.add_widget(self.terms_checkbox)
        terms_layout.add_widget(terms_label)
        form_layout.add_widget(terms_layout)
        
        # Account summary
        summary_card = MDCard(
            MDLabel(
                text="📋 Account Benefits:\n• Personalized event recommendations\n• 48-hour event reminders\n• Easy registration management\n• Secure data protection",
                font_style="Body2",
                theme_text_color="Secondary"
            ),
            size_hint_y=None,
            height="100dp",
            md_bg_color=[0.95, 1, 0.95, 1],
            radius=[10],
            elevation=1,
            padding="15dp"
        )
        form_layout.add_widget(summary_card)
        
        return MDCard(
            form_layout,
            size_hint_y=None,
            height="480dp",
            elevation=6,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_simple_textfield(self, hint, helper, password=False):
        """Create simple KivyMD compatible text field"""
        return MDTextField(
            hint_text=hint,
            helper_text=helper,
            helper_text_mode="persistent",
            mode="rectangle",
            line_color_focus=[0.1, 0.4, 0.9, 1],
            size_hint_y=None,
            height="70dp",
            password=password
        )
    
    def create_interests_grid(self):
        """Create interests selection grid"""
        interests = [
            ("💻", "Technical"), ("🎭", "Cultural"), 
            ("⚽", "Sports"), ("💼", "Placement"),
            ("🤝", "Social"), ("🎯", "Clubs"),
            ("🏆", "Competitions"), ("📚", "Academic")
        ]
        
        grid = MDGridLayout(
            cols=2,
            spacing="15dp",
            size_hint_y=None,
            height="200dp"
        )
        
        for emoji, interest in interests:
            interest_card = self.create_interest_card(emoji, interest)
            grid.add_widget(interest_card)
        
        return grid
    
    def create_interest_card(self, emoji, interest):
        """Create interest selection card"""
        is_selected = interest in self.selected_interests
        
        card = MDCard(
            MDBoxLayout(
                MDLabel(text=emoji, font_style="H4", halign="center"),
                MDLabel(text=interest, font_style="Subtitle1", halign="center", bold=True),
                orientation="vertical",
                spacing="5dp",
                padding="15dp"
            ),
            size_hint_y=None,
            height="80dp",
            elevation=6 if is_selected else 2,
            radius=[15],
            md_bg_color=[0.9, 1, 0.9, 1] if is_selected else [1, 1, 1, 1],
            on_release=lambda x, i=interest: self.toggle_interest(i)
        )
        
        return card
    
    def toggle_interest(self, interest):
        """Toggle interest selection"""
        if interest in self.selected_interests:
            self.selected_interests.remove(interest)
        else:
            self.selected_interests.add(interest)
        
        # Refresh the step to update UI
        self.on_enter()
    
    def create_navigation_buttons(self):
        """Create navigation buttons"""
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="15dp",
            padding="20dp"
        )
        
        # Previous button (if not first step)
        if self.step > 1:
            prev_btn = Button(
                text="⬅️ Previous",
                size_hint_x=0.3,
                height="50dp",
                background_color=[0.7, 0.7, 0.7, 1],
                color=[1, 1, 1, 1],
                font_size="14sp",
                on_release=self.previous_step
            )
            buttons_layout.add_widget(prev_btn)
        else:
            # Spacer
            buttons_layout.add_widget(MDLabel(size_hint_x=0.3))
        
        # Next/Register button
        if self.step < self.total_steps:
            next_btn = Button(
                text="Next Step ➡️",
                size_hint_x=0.7,
                height="50dp",
                background_color=[0.1, 0.4, 0.9, 1],
                color=[1, 1, 1, 1],
                font_size="16sp",
                bold=True,
                on_release=self.next_step
            )
        else:
            next_btn = Button(
                text="🎉 Create Account",
                size_hint_x=0.7,
                height="50dp",
                background_color=[0.1, 0.8, 0.3, 1],
                color=[1, 1, 1, 1],
                font_size="16sp",
                bold=True,
                on_release=self.complete_registration
            )
        
        buttons_layout.add_widget(next_btn)
        
        return MDCard(
            buttons_layout,
            size_hint_y=None,
            height="90dp",
            elevation=4,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_footer_section(self):
        """Create footer section"""
        return MDCard(
            MDBoxLayout(
                MDLabel(
                    text="🛡️ Your data is secure and encrypted",
                    font_style="Caption",
                    theme_text_color="Primary",
                    halign="center",
                    bold=True
                ),
                MDLabel(
                    text="All information is stored securely in Excel databases.\nNeed help? Contact: support@college.edu",
                    font_style="Caption",
                    theme_text_color="Secondary",
                    halign="center"
                ),
                orientation="vertical",
                spacing="8dp",
                padding="20dp"
            ),
            size_hint_y=None,
            height="80dp",
            elevation=1,
            radius=[15],
            md_bg_color=[0.98, 0.99, 1, 1]
        )
    
    def next_step(self, *args):
        """Move to next step"""
        if self.validate_current_step():
            self.step += 1
            self.on_enter()  # Refresh UI
    
    def previous_step(self, *args):
        """Move to previous step"""
        self.step -= 1
        self.on_enter()  # Refresh UI
    
    def validate_current_step(self):
        """Validate current step"""
        if self.step == 1:
            fields = [self.full_name_field, self.student_id_field, self.email_address_field, 
                     self.department_field, self.year_field]
            if not all(field.text.strip() for field in fields):
                self.show_error("Please fill all fields")
                return False
        elif self.step == 2:
            if len(self.selected_interests) == 0:
                self.show_error("Please select at least one interest")
                return False
        else:  # Step 3
            if not self.password_field.text.strip():
                self.show_error("Please enter a password")
                return False
            if self.password_field.text != self.confirm_password_field.text:
                self.show_error("Passwords do not match")
                return False
            if len(self.password_field.text) < 6:
                self.show_error("Password must be at least 6 characters")
                return False
            if not self.terms_checkbox.active:
                self.show_error("Please accept the terms and conditions")
                return False
        
        return True
    
    def complete_registration(self, *args):
        """Complete registration"""
        if not self.validate_current_step():
            return
        
        try:
            from utils.excel_db import ExcelUserDatabase
            
            excel_db = ExcelUserDatabase()
            success, message = excel_db.register_user(
                name=self.full_name_field.text.strip(),
                student_id=self.student_id_field.text.strip(),
                email=self.email_address_field.text.strip().lower(),
                department=self.department_field.text.strip(),
                year=self.year_field.text.strip(),
                password=self.password_field.text.strip(),
                interests=list(self.selected_interests)
            )
            
            if success:
                self.show_success()
            else:
                self.show_error(f"Registration failed: {message}")
                
        except Exception as e:
            self.show_error(f"System error: {str(e)}")
    
    def show_success(self):
        """Show success dialog and auto-redirect to login"""
        self.dialog = MDDialog(
            title="🎉 Registration Successful!",
            text=f"""Welcome to Event Aggregator!

👤 Name: {self.full_name_field.text}
🆔 Student ID: {self.student_id_field.text}
📧 Email: {self.email_address_field.text}
🏫 Department: {self.department_field.text}
🎯 Interests: {len(self.selected_interests)} selected

Your account has been created successfully!
Redirecting to login page in 3 seconds...""",
            buttons=[
                Button(
                    text="🚀 Login Now",
                    background_color=[0.1, 0.8, 0.3, 1],
                    color=[1, 1, 1, 1],
                    on_release=self.go_to_login
                )
            ],
        )
        self.dialog.open()
        
        # Auto-redirect after 3 seconds
        Clock.schedule_once(lambda dt: self.go_to_login(), 3)
    
    def show_error(self, message):
        """Show error dialog"""
        self.dialog = MDDialog(
            title="⚠️ Error",
            text=message,
            buttons=[
                Button(
                    text="OK",
                    background_color=[0.9, 0.3, 0.3, 1],
                    color=[1, 1, 1, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()
    
    def show_help(self, *args):
        """Show help dialog"""
        help_texts = {
            1: "Enter your personal information accurately.\nUse your official college email address.",
            2: "Select interests that match your preferences.\nThis helps recommend relevant events.",
            3: "Create a secure password with at least 6 characters.\nAccept terms to complete registration."
        }
        
        self.dialog = MDDialog(
            title=f"💡 Step {self.step} Help",
            text=help_texts[self.step],
            buttons=[
                Button(text="Got it!", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()
    
    def go_to_login(self, *args):
        """Navigate to login screen - FIXED METHOD"""
        print("🔄 Redirecting to login page...")
        if self.dialog:
            self.dialog.dismiss()
        App.get_running_app().sm.current = 'login'
    
    def go_back(self, *args):
        """Navigate back to home - FIXED METHOD"""
        print("🔄 Going back to home...")
        App.get_running_app().sm.current = 'home'
