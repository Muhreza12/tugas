# modern_notification.py — Beautiful Toast Notifications untuk PyQt5
"""
Modern notification widget yang cantik untuk menggantikan QMessageBox
Author: Claude + Reza
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class ModernNotification(QtWidgets.QFrame):
    """
    Modern toast notification dengan animasi smooth
    
    Usage:
        notification = ModernNotification.success(parent, "Berhasil!", "Akun berhasil dibuat")
        notification.show_notification()
    """
    
    # Notification types
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    
    def __init__(self, parent, title, message, notification_type=INFO, duration=3000):
        super().__init__(parent)
        
        self.notification_type = notification_type
        self.duration = duration
        
        # Setup UI
        self._setup_ui(title, message)
        self._apply_style()
        
        # Timer untuk auto-hide
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.hide_notification)
        
        # Animation
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
    def _setup_ui(self, title, message):
        """Setup notification UI"""
        self.setObjectName("notification")
        self.setFixedHeight(80)
        self.setMinimumWidth(350)
        self.setMaximumWidth(500)
        
        # Main layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon")
        layout.addWidget(self.icon_label)
        
        # Content
        content_layout = QtWidgets.QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setObjectName("title")
        self.title_label.setWordWrap(True)
        content_layout.addWidget(self.title_label)
        
        # Message
        self.message_label = QtWidgets.QLabel(message)
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        content_layout.addWidget(self.message_label)
        
        layout.addLayout(content_layout, 1)
        
        # Close button
        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide_notification)
        layout.addWidget(self.close_btn, 0, QtCore.Qt.AlignTop)
        
    def _apply_style(self):
        """Apply styling based on notification type"""
        
        # Icon dan warna berdasarkan type
        icons = {
            self.SUCCESS: "✓",
            self.ERROR: "✕",
            self.INFO: "ℹ",
            self.WARNING: "⚠"
        }
        
        colors = {
            self.SUCCESS: {
                'bg': '#10b981',
                'text': '#ffffff',
                'icon_bg': '#059669'
            },
            self.ERROR: {
                'bg': '#ef4444',
                'text': '#ffffff',
                'icon_bg': '#dc2626'
            },
            self.INFO: {
                'bg': '#3b82f6',
                'text': '#ffffff',
                'icon_bg': '#2563eb'
            },
            self.WARNING: {
                'bg': '#f59e0b',
                'text': '#ffffff',
                'icon_bg': '#d97706'
            }
        }
        
        icon = icons.get(self.notification_type, "ℹ")
        color = colors.get(self.notification_type, colors[self.INFO])
        
        self.icon_label.setText(icon)
        
        self.setStyleSheet(f"""
            #notification {{
                background: {color['bg']};
                border-radius: 12px;
                border: none;
            }}
            #icon {{
                background: {color['icon_bg']};
                color: {color['text']};
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
            }}
            #title {{
                color: {color['text']};
                font-size: 14px;
                font-weight: 700;
            }}
            #message {{
                color: {color['text']};
                font-size: 12px;
                opacity: 0.9;
            }}
            #closeBtn {{
                background: transparent;
                color: {color['text']};
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            #closeBtn:hover {{
                background: rgba(0, 0, 0, 0.1);
            }}
        """)
        
    def show_notification(self):
        """Show notification with animation"""
        # Position di tengah atas parent
        parent_rect = self.parent().rect()
        self.move(
            (parent_rect.width() - self.width()) // 2,
            20  # 20px dari atas
        )
        
        # Fade in animation
        self.fade_in = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        self.show()
        self.raise_()
        self.fade_in.start()
        
        # Auto-hide setelah duration
        if self.duration > 0:
            self.timer.start(self.duration)
        
    def hide_notification(self):
        """Hide notification with animation"""
        self.timer.stop()
        
        # Fade out animation
        self.fade_out = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QtCore.QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.deleteLater)
        
        self.fade_out.start()
        
    # Static methods untuk kemudahan
    @staticmethod
    def success(parent, title, message, duration=3000):
        """Create success notification"""
        return ModernNotification(parent, title, message, ModernNotification.SUCCESS, duration)
    
    @staticmethod
    def error(parent, title, message, duration=4000):
        """Create error notification"""
        return ModernNotification(parent, title, message, ModernNotification.ERROR, duration)
    
    @staticmethod
    def info(parent, title, message, duration=3000):
        """Create info notification"""
        return ModernNotification(parent, title, message, ModernNotification.INFO, duration)
    
    @staticmethod
    def warning(parent, title, message, duration=3500):
        """Create warning notification"""
        return ModernNotification(parent, title, message, ModernNotification.WARNING, duration)


# ========== EXAMPLE USAGE ==========
if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Demo window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Modern Notification Demo")
    window.resize(600, 400)
    window.setStyleSheet("background: #0e0f12;")
    
    layout = QtWidgets.QVBoxLayout(window)
    layout.setAlignment(QtCore.Qt.AlignCenter)
    
    # Test buttons
    btn_success = QtWidgets.QPushButton("Show Success")
    btn_error = QtWidgets.QPushButton("Show Error")
    btn_info = QtWidgets.QPushButton("Show Info")
    btn_warning = QtWidgets.QPushButton("Show Warning")
    
    for btn in [btn_success, btn_error, btn_info, btn_warning]:
        btn.setFixedSize(200, 40)
        layout.addWidget(btn, 0, QtCore.Qt.AlignCenter)
    
    # Handlers
    def show_success():
        notif = ModernNotification.success(
            window,
            "Berhasil!",
            "Akun 'testing111' (role: user) berhasil dibuat"
        )
        notif.show_notification()
    
    def show_error():
        notif = ModernNotification.error(
            window,
            "Error!",
            "Username atau password salah"
        )
        notif.show_notification()
    
    def show_info():
        notif = ModernNotification.info(
            window,
            "Info",
            "Isi username dan password untuk melanjutkan"
        )
        notif.show_notification()
    
    def show_warning():
        notif = ModernNotification.warning(
            window,
            "Peringatan!",
            "Password minimal 4 karakter"
        )
        notif.show_notification()
    
    btn_success.clicked.connect(show_success)
    btn_error.clicked.connect(show_error)
    btn_info.clicked.connect(show_info)
    btn_warning.clicked.connect(show_warning)
    
    window.show()
    sys.exit(app.exec_())
