# dashboard_ui.py — Dashboard Router untuk Crypto Insight
"""
Router yang mengarahkan user ke dashboard yang sesuai:
- admin → Admin Dashboard (dengan presence monitoring)
- penerbit → Penerbit Dashboard (modern UI untuk tulis berita)
- user → User Dashboard (crypto prices & portfolio)
"""

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except:
    from PyQt6 import QtCore, QtGui, QtWidgets

from typing import Optional

APP_NAME = "Crypto Insight"


def DashboardWindow(username: str, role: str, session_id: Optional[int] = None):
    """
    Factory function yang return dashboard sesuai role
    
    Args:
        username: Username yang login
        role: Role user (admin/penerbit/user)
        session_id: Session ID untuk heartbeat
    
    Returns:
        Dashboard window instance yang sesuai
    """
    
    role = role.lower()
    
    if role == "admin":
        # Import dan return admin dashboard
        try:
            from admin_dashboard import AdminDashboardEnhanced
            return AdminDashboardEnhanced(username, session_id)
        except ImportError:
            # Fallback ke admin dashboard biasa
            from admin_dashboard import AdminDashboard
            return AdminDashboard(username, session_id)
    
    elif role == "penerbit":
        # Import dan return penerbit dashboard (YANG BARU & CANTIK!)
        from penerbit_dashboard import PenerbitDashboard
        return PenerbitDashboard(username, session_id)
    
    else:
        # user atau role lain → user dashboard
        from user_dashboard import UserDashboard
        return UserDashboard(username, session_id)


# ========== FALLBACK DASHBOARDS (jika file terpisah tidak ada) ==========

class AdminDashboardSimple(QtWidgets.QMainWindow):
    """Simple admin dashboard dengan presence monitoring"""
    
    def __init__(self, username: str, session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle(f"{APP_NAME} • Admin Dashboard")
        self.resize(1200, 760)
        
        # Setup UI
        self._setup_simple_ui()
        self._apply_dark_style()
        
        # Heartbeat
        if session_id:
            from app_db import heartbeat
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(session_id))
            self.hb_timer.start(20000)
    
    def _setup_simple_ui(self):
        """Setup simple admin UI"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QtWidgets.QLabel(f"👑 Admin Dashboard • {self.username}")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #7c5cff;")
        layout.addWidget(header)
        
        # Presence table
        from app_db import latest_presence_per_user
        
        group = QtWidgets.QGroupBox("Users Presence")
        v = QtWidgets.QVBoxLayout(group)
        
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Username", "Role", "Online", "Last Seen"])
        self.table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.table)
        
        layout.addWidget(group)
        
        # Load data
        def load_presence():
            rows = latest_presence_per_user()
            self.table.setRowCount(len(rows))
            for i, (uname, role, online, last_seen) in enumerate(rows):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(uname))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(role or "user"))
                
                it = QtWidgets.QTableWidgetItem("Online" if online else "Offline")
                color = QtGui.QColor("#34d399") if online else QtGui.QColor("#ef4444")
                it.setForeground(QtGui.QBrush(color))
                self.table.setItem(i, 2, it)
                
                self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(last_seen or ""))
        
        load_presence()
        
        # Auto-refresh
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(load_presence)
        self.refresh_timer.start(10000)
        
        # Logout
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white;
                border: none; border-radius: 8px;
                padding: 10px 20px; font-weight: 600;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        layout.addWidget(self.logout_btn)
    
    def _apply_dark_style(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #0e0f12; color: #eaeaea; }
            QGroupBox {
                border: 1px solid #26263a; border-radius: 12px;
                margin-top: 12px; background: #0e0f12;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px;
                padding: 0 4px; color: #b6b8c3;
            }
            QTableWidget {
                background: #0e0f12; color: #eaeaea;
                alternate-background-color: #11131a;
                gridline-color: #2a2a3d; border: 1px solid #26263a;
            }
            QHeaderView::section {
                background: #121218; color: #d1d5db;
                padding: 6px 8px; border: 1px solid #26263a;
            }
        """)


class UserDashboardSimple(QtWidgets.QMainWindow):
    """Simple user dashboard"""
    
    def __init__(self, username: str, session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle(f"{APP_NAME} • User Dashboard")
        self.resize(960, 600)
        
        # Setup UI
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QtWidgets.QLabel(f"Welcome, {username}! 🚀")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #7c5cff;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QtWidgets.QLabel(
            "This is User Dashboard.\n\n"
            "Features coming soon:\n"
            "• Real-time crypto prices\n"
            "• Portfolio management\n"
            "• Latest news feed\n"
            "• Price alerts"
        )
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("font-size: 14px; color: #9ca3af; line-height: 1.6;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Logout
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white;
                border: none; border-radius: 8px;
                padding: 10px 20px; font-weight: 600;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        layout.addWidget(self.logout_btn, 0, QtCore.Qt.AlignCenter)
        
        # Dark theme
        self.setStyleSheet("QMainWindow, QWidget { background: #0e0f12; color: #eaeaea; }")
        
        # Heartbeat
        if session_id:
            from app_db import heartbeat
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(session_id))
            self.hb_timer.start(20000)
