# user_dashboard.py — User Dashboard dengan Session Management
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Optional
from app_db_fixed import heartbeat, end_session

class UserDashboard(QtWidgets.QMainWindow):
    """User Dashboard untuk Crypto Insight"""
    
    def __init__(self, username: str = "user", session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle("Crypto Insight — User Dashboard")
        self.resize(960, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QtWidgets.QLabel(f"Welcome, {username}! 🚀")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #7c5cff; margin: 12px 0;")
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

        # Logout button
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setFixedHeight(42)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white;
                border: none; border-radius: 8px;
                padding: 10px 20px; font-weight: 600;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        self.logout_btn.clicked.connect(self._logout)
        layout.addWidget(self.logout_btn, 0, QtCore.Qt.AlignCenter)

        # Apply dark theme
        self.setStyleSheet("QMainWindow, QWidget { background: #0e0f12; color: #eaeaea; }")

        # Heartbeat timer - untuk menjaga session tetap aktif
        if self.session_id:
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(self.session_id))
            self.hb_timer.start(20000)  # Every 20 seconds

    def _logout(self):
        """Logout dan close dashboard dengan proper cleanup"""
        # Stop heartbeat timer
        if hasattr(self, 'hb_timer') and self.hb_timer.isActive():
            self.hb_timer.stop()

        # End session di database
        if self.session_id:
            try:
                end_session(self.session_id)
            except Exception as e:
                print(f"Error ending session: {e}")

        # Close window
        self.close()

    def closeEvent(self, event):
        """Handle window close event"""
        self._logout()
        event.accept()
