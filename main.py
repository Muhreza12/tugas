# main_enhanced.py — Launcher untuk Enhanced Auth UI
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer

class SplashScreen(QtWidgets.QWidget):
    """Splash screen dengan animasi loading"""
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(450, 600) 
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.main_frame = QtWidgets.QFrame(self)
        self.main_frame.setObjectName("mainFrame")
        
        layout = QtWidgets.QVBoxLayout(self.main_frame)
        layout.setContentsMargins(50, 60, 50, 60) 
        layout.setSpacing(30)

        # Logo & Brand
        logo_layout = QtWidgets.QHBoxLayout()
        logo_circle = QtWidgets.QLabel("🚀")
        logo_circle.setFixedSize(40, 40) 
        logo_circle.setObjectName("logoCircle")
        logo_circle.setAlignment(QtCore.Qt.AlignCenter)
        
        logo_text = QtWidgets.QLabel("Crypto Insight")
        logo_text.setObjectName("logoText")
        
        logo_layout.addWidget(logo_circle)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()

        # Title
        self.title = QtWidgets.QLabel("Discover crypto insights\nin one glance.")
        self.title.setObjectName("titleText")
        self.title.setWordWrap(True)
        
        # Subtitle
        self.subtitle = QtWidgets.QLabel("Enhanced Edition")
        self.subtitle.setObjectName("subtitleText")

        # Loading animation
        self.loading_label = QtWidgets.QLabel("Loading")
        self.loading_label.setObjectName("loadingText")
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Dots animation
        self.dots = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self._update_loading)
        self.loading_timer.start(400)

        layout.addLayout(logo_layout)
        layout.addStretch(1) 
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        layout.addWidget(self.loading_label)

        self.window_layout = QtWidgets.QVBoxLayout(self)
        self.window_layout.addWidget(self.main_frame)
        
        self.setStyleSheet("""
            #mainFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b
                );
                border-radius: 20px;
            }
            #logoCircle {
                font-size: 28px;
            }
            #logoText {
                color: #f1f5f9;
                font-size: 20px;
                font-weight: 700;
                padding-left: 8px;
            }
            #titleText {
                color: #f1f5f9;
                font-size: 48px;
                font-weight: 800;
                line-height: 52px;
            }
            #subtitleText {
                color: #6366f1;
                font-size: 18px;
                font-weight: 600;
                margin-top: 10px;
            }
            #loadingText {
                color: #94a3b8;
                font-size: 14px;
                font-weight: 500;
            }
        """)
    
    def _update_loading(self):
        """Update loading animation"""
        self.dots = (self.dots + 1) % 4
        dots_text = "." * self.dots
        self.loading_label.setText(f"Loading{dots_text}")

def main():
    """Launch Enhanced Auth UI"""
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Set font
    app.setFont(QtGui.QFont("Segoe UI", 10))
    
    try:
        from auth_ui_enhanced import EnhancedAuthWindow
        
        # Create splash screen
        splash = SplashScreen()
        
        # Center on screen
        screen_geo = QtWidgets.QApplication.desktop().screenGeometry()
        center_pos = screen_geo.center() - splash.rect().center()
        splash.move(center_pos)
        
        # Show splash
        splash.show()
        
        # Create main window
        main_window = EnhancedAuthWindow()
        
        # Function to switch windows
        def show_main_window():
            splash.loading_timer.stop()
            splash.close()
            
            # Center main window
            screen_geo = QtWidgets.QApplication.desktop().screenGeometry()
            center_pos = screen_geo.center() - main_window.rect().center()
            main_window.move(center_pos)
            
            main_window.show()

        # Switch after 2.5 seconds
        QTimer.singleShot(2500, show_main_window)
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Import Error")
        msg.setText(f"Failed to import required modules:\n\n{str(e)}\n\n"
                   "Required files:\n"
                   "- auth_ui_enhanced.py\n"
                   "- app_db_fixed.py\n"
                   "- modern_notification.py")
        msg.exec_()
        sys.exit(1)
        
    except Exception as e:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(f"An error occurred:\n\n{str(e)}")
        msg.exec_()
        sys.exit(1)

if __name__ == "__main__":
    main()
