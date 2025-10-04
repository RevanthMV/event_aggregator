# main.py
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from screens.home_screen import HomeScreen
from screens.login_screen import LoginScreen
from screens.admin_login_screen import AdminLoginScreen
from screens.register_screen import RegisterScreen
from screens.dashboard import Dashboard
from screens.event_details import EventDetailsScreen
from screens.my_events_screen import MyEventsScreen
from screens.admin_dashboard import AdminDashboard
import threading


class EventAggregatorApp(MDApp):
    def __init__(self):
        super().__init__()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # App state
        self.current_user = None
        self.selected_event = None

        # Initialize systems
        self.init_databases()
        self.start_notification_system()   # ✅ Unified background notification scheduler

    def build(self):
        self.sm = ScreenManager()
        
        # Add all screens
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(AdminLoginScreen(name='admin_login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(Dashboard(name='dashboard'))
        self.sm.add_widget(EventDetailsScreen(name='event_details'))
        self.sm.add_widget(MyEventsScreen(name='my_events'))
        self.sm.add_widget(AdminDashboard(name='admin_dashboard'))
        
        return self.sm
    
    def on_start(self):
        """App startup"""
        self.sm.current = 'home'
        print("✅ Event Aggregator started")
        print("📱 Available screens:", [screen.name for screen in self.sm.screens])
    
    def init_databases(self):
        """Initialize Excel databases"""
        try:
            from utils.excel_db import ExcelUserDatabase
            excel_db = ExcelUserDatabase()
            self.excel_db = excel_db   # ✅ Keep a reference for registration/login
            print("✅ Databases ready")
        except Exception as e:
            print(f"⚠️ Database warning: {e}")
    
    def start_notification_system(self):
        """Start background notification + 24hr/48hr reminder scheduler"""
        def run_notifications():
            try:
                from utils.notification_system import NotificationSystem
                notification_system = NotificationSystem()
                notification_system.start_scheduler()
                print("✅ Notification system started (24hr + 48hr reminders enabled)")
            except Exception as e:
                print(f"⚠️ Notification system warning: {e}")
        
        threading.Thread(target=run_notifications, daemon=True).start()


if __name__ == '__main__':
    print("🚀 Starting Event Aggregator...")
    EventAggregatorApp().run()
