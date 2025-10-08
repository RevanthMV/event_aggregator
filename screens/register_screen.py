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
from kivymd.uix.button import MDIconButton

class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.selected_interests = set()
        self.step = 1
        self.total_steps = 3

    def on_enter(self):
        self.clear_widgets()
        self.md_bg_color = [0.96, 0.97, 0.99, 1]
        
        # Main layout
        main_layout = MDBoxLayout(orientation="vertical")
        
        # Premium Top App Bar with gradient effect
        toolbar = MDTopAppBar(
            title="🎓 Student Registration",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["help-circle", lambda x: self.show_help()]],
            elevation=8,
            md_bg_color=[0.11, 0.35, 0.85, 1]
        )
        
        # Progress indicator
        progress_card = self.create_progress_indicator()
        
        # Main content scroll
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing="18dp",
            size_hint_y=None,
            padding=["16dp", "8dp", "16dp", "16dp"]
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
        """Create beautiful progress indicator"""
        container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="85dp",
            padding=["20dp", "12dp", "20dp", "8dp"]
        )
        
        # Progress bar with steps
        progress_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height="48dp"
        )
        
        # Step indicators
        for i in range(1, self.total_steps + 1):
            if i <= self.step:
                bg_color = [0.13, 0.75, 0.35, 1]
                text_color = [1, 1, 1, 1]
                elevation = 6
            else:
                bg_color = [0.88, 0.88, 0.88, 1]
                text_color = [0.55, 0.55, 0.55, 1]
                elevation = 2
            
            step_card = MDCard(
                MDLabel(
                    text=str(i),
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=text_color,
                    halign="center",
                    valign="center",
                    bold=True
                ),
                size_hint=(None, None),
                size=("48dp", "48dp"),
                md_bg_color=bg_color,
                radius=[24],
                elevation=elevation
            )
            progress_layout.add_widget(step_card)
            
            # Add connector line
            if i < self.total_steps:
                line_color = [0.13, 0.75, 0.35, 1] if i < self.step else [0.88, 0.88, 0.88, 1]
                connector = MDLabel(
                    text="━",
                    theme_text_color="Custom",
                    text_color=line_color,
                    size_hint_x=0.15,
                    halign="center",
                    valign="center",
                    font_size="18sp"
                )
                progress_layout.add_widget(connector)
        
        container.add_widget(progress_layout)
        
        # Progress text
        progress_text = MDLabel(
            text=f"Step {self.step} of {self.total_steps}  •  {int((self.step/self.total_steps)*100)}% Complete",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height="22dp"
        )
        container.add_widget(progress_text)
        
        return MDCard(
            container,
            size_hint_y=None,
            height="85dp",
            elevation=3,
            radius=[0, 0, 18, 18],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_hero_section(self):
        """Create beautiful hero section"""
        step_info = {
            1: ("👋 Welcome!", "Let's get started with your basic information"),
            2: ("🎯 Your Interests", "Select categories to personalize your experience"),
            3: ("🔐 Almost Done", "Create your secure account credentials")
        }
        
        title, desc = step_info[self.step]
        
        hero_layout = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            padding=["24dp", "18dp", "24dp", "18dp"],
            size_hint_y=None,
            height="110dp"
        )
        
        hero_layout.add_widget(
            MDLabel(
                text=title,
                font_style="H4",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],
                halign="center",
                bold=True,
                size_hint_y=None,
                height="40dp"
            )
        )
        
        hero_layout.add_widget(
            MDLabel(
                text=desc,
                font_style="Body1",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 0.92],
                halign="center",
                size_hint_y=None,
                height="32dp"
            )
        )
        
        return MDCard(
            hero_layout,
            size_hint_y=None,
            height="110dp",
            elevation=8,
            radius=[22],
            md_bg_color=[0.11, 0.42, 0.92, 1]
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
            spacing="14dp",
            padding=["24dp", "20dp", "24dp", "20dp"],
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Form title
        form_layout.add_widget(
            MDLabel(
                text="📝 Personal Information",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height="32dp"
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
            height="470dp",
            elevation=5,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_step2_interests(self):
        """Step 2: Beautiful Interest Selection"""
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            padding=["24dp", "20dp", "24dp", "20dp"],
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Title
        form_layout.add_widget(
            MDLabel(
                text="🎯 Select Your Interests",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height="32dp"
            )
        )
        
        # Description
        form_layout.add_widget(
            MDLabel(
                text="Tap to select categories you're interested in:",
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="28dp"
            )
        )
        
        # Interests grid
        interests_grid = self.create_interests_grid()
        form_layout.add_widget(interests_grid)
        
        # Selection count with beautiful styling
        count_card = MDCard(
            MDLabel(
                text=f"✅ {len(self.selected_interests)} interests selected",
                font_style="Subtitle2",
                theme_text_color="Custom",
                text_color=[0.13, 0.75, 0.35, 1],
                halign="center",
                valign="center",
                bold=True
            ),
            size_hint_y=None,
            height="42dp",
            md_bg_color=[0.9, 0.98, 0.9, 1],
            radius=[12],
            elevation=2,
            padding="10dp"
        )
        form_layout.add_widget(count_card)
        
        return MDCard(
            form_layout,
            size_hint_y=None,
            height="590dp",
            elevation=5,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_step3_credentials(self):
        """Step 3: Account Credentials"""
        form_layout = MDBoxLayout(
            orientation="vertical",
            spacing="14dp",
            padding=["24dp", "20dp", "24dp", "20dp"],
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Title
        form_layout.add_widget(
            MDLabel(
                text="🔐 Secure Your Account",
                font_style="H6",
                theme_text_color="Primary",
                bold=True,
                size_hint_y=None,
                height="32dp"
            )
        )
        
        # Description
        form_layout.add_widget(
            MDLabel(
                text="Create secure login credentials:",
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="26dp"
            )
        )
        
        # Password field
        self.password_field = self.create_simple_textfield("Password", "Minimum 6 characters", password=True)
        form_layout.add_widget(self.password_field)
        
        # Confirm password field
        self.confirm_password_field = self.create_simple_textfield("Confirm Password", "Re-enter your password", password=True)
        form_layout.add_widget(self.confirm_password_field)
        
        # Terms checkbox
        terms_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="12dp",
            size_hint_y=None,
            height="48dp",
            padding=["4dp", "8dp", "4dp", "8dp"]
        )
        
        self.terms_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=("32dp", "32dp"),
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
        
        # Beautiful benefits card
        benefits_layout = MDBoxLayout(
            orientation="vertical",
            padding=["16dp", "14dp", "16dp", "14dp"],
            spacing="6dp",
            size_hint_y=None,
            height="115dp"
        )
        
        benefits_layout.add_widget(
            MDLabel(
                text="🎉 Account Benefits",
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=[0.11, 0.42, 0.92, 1],
                bold=True,
                size_hint_y=None,
                height="28dp"
            )
        )
        
        benefits_text = MDLabel(
            text="• Personalized event recommendations\n• 48-hour event reminders\n• Easy registration management\n• Secure data protection",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="68dp"
        )
        benefits_layout.add_widget(benefits_text)
        
        benefits_card = MDCard(
            benefits_layout,
            size_hint_y=None,
            height="115dp",
            md_bg_color=[0.95, 0.97, 1, 1],
            radius=[14],
            elevation=2
        )
        form_layout.add_widget(benefits_card)
        
        return MDCard(
            form_layout,
            size_hint_y=None,
            height="490dp",
            elevation=5,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_simple_textfield(self, hint, helper, password=False):
        """Create beautiful text field"""
        return MDTextField(
            hint_text=hint,
            helper_text=helper,
            helper_text_mode="persistent",
            mode="rectangle",
            line_color_focus=[0.11, 0.42, 0.92, 1],
            size_hint_y=None,
            height="72dp",
            password=password
        )
    
    def create_interests_grid(self):
        """Create beautiful interests grid"""
        interests = [
            ("laptop", "Technical", [0.2, 0.6, 1, 1]), 
            ("drama-masks", "Cultural", [1, 0.4, 0.6, 1]), 
            ("soccer", "Sports", [0.2, 0.8, 0.2, 1]), 
            ("briefcase", "Placement", [0.9, 0.5, 0.1, 1]),
            ("account-group", "Social", [0.4, 0.4, 1, 1]), 
            ("bullseye-arrow", "Clubs", [1, 0.3, 0.3, 1]),
            ("trophy", "Competitions", [1, 0.7, 0, 1]), 
            ("book-open-variant", "Academic", [0.3, 0.7, 0.9, 1])
        ]
        
        grid = MDGridLayout(
            cols=2,
            spacing="14dp",
            size_hint_y=None,
            height="370dp",
            padding=["2dp", "8dp", "2dp", "8dp"]
        )
        
        for icon, interest, color in interests:
            interest_card = self.create_interest_card(icon, interest, color)
            grid.add_widget(interest_card)
        
        return grid
    
    def create_interest_card(self, icon, interest, icon_color):
        """Create beautiful interest card with animation effect"""
        is_selected = interest in self.selected_interests
        
        card_layout = MDBoxLayout(
            orientation="vertical",
            spacing="4dp",
            padding=["12dp", "12dp", "12dp", "12dp"]
        )
        
        # Icon button with proper Material Design Icons
        icon_btn = MDIconButton(
            icon=icon,
            icon_size="42sp",
            theme_icon_color="Custom",
            icon_color=icon_color if not is_selected else [0.13, 0.75, 0.35, 1],
            pos_hint={"center_x": 0.5},
            disabled=True
        )
        card_layout.add_widget(icon_btn)
        
        # Interest name
        interest_label = MDLabel(
            text=interest,
            font_style="Subtitle1",
            halign="center",
            valign="center",
            bold=True,
            size_hint_y=None,
            height="28dp"
        )
        card_layout.add_widget(interest_label)
        
        if is_selected:
            bg_color = [0.88, 0.98, 0.88, 1]
            elevation = 8
        else:
            bg_color = [1, 1, 1, 1]
            elevation = 3
        
        card = MDCard(
            card_layout,
            size_hint_y=None,
            height="95dp",
            elevation=elevation,
            radius=[14],
            md_bg_color=bg_color,
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
        """Create beautiful navigation buttons"""
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="14dp",
            padding=["20dp", "16dp", "20dp", "16dp"],
            size_hint_y=None,
            height="90dp"
        )
        
        # Previous button (if not first step)
        if self.step > 1:
            prev_btn = Button(
                text="⬅  Previous",
                size_hint_x=0.38,
                size_hint_y=None,
                height="58dp",
                background_color=[0.45, 0.45, 0.45, 1],
                color=[1, 1, 1, 1],
                font_size="15sp",
                bold=True,
                on_release=self.previous_step
            )
            buttons_layout.add_widget(prev_btn)
        else:
            # Spacer
            buttons_layout.add_widget(MDLabel(size_hint_x=0.38))
        
        # Next/Register button
        if self.step < self.total_steps:
            next_btn = Button(
                text="Next Step  ➡",
                size_hint_x=0.62,
                size_hint_y=None,
                height="58dp",
                background_color=[0.11, 0.42, 0.92, 1],
                color=[1, 1, 1, 1],
                font_size="16sp",
                bold=True,
                on_release=self.next_step
            )
        else:
            next_btn = Button(
                text="🎉  Create Account",
                size_hint_x=0.62,
                size_hint_y=None,
                height="58dp",
                background_color=[0.13, 0.75, 0.35, 1],
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
            elevation=6,
            radius=[20],
            md_bg_color=[1, 1, 1, 1]
        )
    
    def create_footer_section(self):
        """Create beautiful footer"""
        footer_layout = MDBoxLayout(
            orientation="vertical",
            spacing="6dp",
            padding=["20dp", "14dp", "20dp", "14dp"],
            size_hint_y=None,
            height="78dp"
        )
        
        footer_layout.add_widget(
            MDLabel(
                text="🛡️  Your data is secure and encrypted",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=[0.13, 0.75, 0.35, 1],
                halign="center",
                bold=True,
                size_hint_y=None,
                height="22dp"
            )
        )
        
        footer_layout.add_widget(
            MDLabel(
                text="Secured with industry-standard encryption\nNeed help? Contact: support@college.edu",
                font_style="Caption",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height="34dp"
            )
        )
        
        return MDCard(
            footer_layout,
            size_hint_y=None,
            height="78dp",
            elevation=2,
            radius=[16],
            md_bg_color=[0.97, 0.98, 0.99, 1]
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