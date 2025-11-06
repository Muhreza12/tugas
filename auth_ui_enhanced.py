# auth_ui_enhanced.py — Enhanced Auth UI dengan Warna yang Lebih Baik
"""
Login/Register UI dengan panel yang flip dan warna yang lebih menarik

Features:
- 3D Flip animation (0.6s)
- Glassmorphism design
- Multi-Language (English & Indonesia)
- Beautiful color scheme
- Smooth transitions
"""

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect
)

# Backend
from app_db_fixed import (
    verify_user, create_user, user_exists, setup_database,
    start_session, health_check
)

# Modern notification
from modern_notification import ModernNotification

APP_NAME = "Crypto Insight"


class EnhancedAuthWindow(QtWidgets.QWidget):
    """Enhanced auth window dengan warna yang lebih baik"""
    
    ANIMATION_DURATION = 600 
    EASING_CURVE = QEasingCurve.InOutCubic

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State tracking
        self.is_login_mode = True  
        self.current_theme = "dark"  # Default dark theme
        self.is_animating = False 
        
        # Bahasa default (hanya English dan Indonesia)
        self.current_lang = "English" 
        
        self._define_themes()
        self._define_translations()
        self._setup_ui()
        self._apply_style(self.current_theme)
        
        # Terapkan teks awal
        self.retranslateUi() 
        
        self._init_database()
        
    def _define_themes(self):
        """Mendefinisikan palet warna yang lebih menarik"""
        
        # Warna brand yang lebih modern
        BRAND_PRIMARY = "#6366f1"      # Indigo
        BRAND_SECONDARY = "#8b5cf6"    # Purple
        BRAND_ACCENT = "#ec4899"       # Pink
        
        self.common_colors = {
            "welcome_bg": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {BRAND_PRIMARY}, stop:1 {BRAND_SECONDARY})",
            "welcome_text": "#ffffff",
            "welcome_btn_border": "#ffffff",
            "primary_btn_bg": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {BRAND_PRIMARY}, stop:1 {BRAND_ACCENT})",
            "primary_btn_hover": BRAND_SECONDARY,
            "primary_btn_text": "#ffffff",
            "link_text": BRAND_PRIMARY,
            "accent_color": BRAND_ACCENT
        }
        
        self.themes = {
            "dark": {
                "root_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #1e293b)",
                "card_bg": self.common_colors["welcome_bg"], 
                "form_bg": "rgba(30, 41, 59, 0.95)", 
                "card_border": "rgba(148, 163, 184, 0.2)", 
                "form_title": "#f1f5f9",
                "input_bg": "#1e293b", 
                "input_text": "#f1f5f9",
                "input_border": "#334155",
                "input_border_focus": BRAND_PRIMARY,
                "input_icon": "#94a3b8",
                "social_label": "#94a3b8",
                "combo_bg": "#1e293b",
                "combo_text": "#f1f5f9",
                "combo_border": "#334155",
                "combo_item_bg": "#1e293b",
                "combo_item_hover": "#334155",
                "combo_item_selected": BRAND_PRIMARY,
                "social_btn_bg": "#334155",
                "social_btn_text": "#f1f5f9",
                "social_btn_border": "#475569",
                "social_btn_hover_bg": "#475569"
            },
            "light": {
                "root_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8fafc, stop:1 #e2e8f0)",
                "card_bg": self.common_colors["welcome_bg"], 
                "form_bg": "rgba(255, 255, 255, 0.95)", 
                "card_border": "rgba(203, 213, 225, 0.5)", 
                "form_title": "#0f172a",
                "input_bg": "#f8fafc", 
                "input_text": "#0f172a",
                "input_border": "#cbd5e1",
                "input_border_focus": BRAND_PRIMARY,
                "input_icon": "#64748b",
                "social_label": "#64748b",
                "combo_bg": "#f8fafc",
                "combo_text": "#0f172a",
                "combo_border": "#cbd5e1",
                "combo_item_bg": "#ffffff",
                "combo_item_hover": "#f1f5f9",
                "combo_item_selected": BRAND_PRIMARY,
                "social_btn_bg": "#ffffff",
                "social_btn_text": "#0f172a",
                "social_btn_border": "#e2e8f0",
                "social_btn_hover_bg": "#f8fafc"
            }
        }
        
    def _define_translations(self):
        """Kamus bahasa (hanya English dan Indonesia)"""
        self.translations = {
            "English": {
                "window_title": "Crypto Insight • Sign in",
                "welcome_title": "Hello, Welcome!",
                "welcome_subtitle": "Don't have an account?",
                "btn_register": "Register",
                "welcome_back_title": "Welcome Back!",
                "welcome_back_subtitle": "Already have an account?",
                "btn_login": "Login",
                "login_title": "Login",
                "placeholder_username": "Username",
                "placeholder_password": "Password",
                "forgot_password": "Forgot Password?",
                "register_title": "Registration",
                "placeholder_email": "Email",
                "role_label": "Role:",
                "toast_fill_fields": "Fill in username and password.",
                "toast_session_failed": "Could not create online session.",
                "toast_dashboard_not_found": "Dashboard not found:",
                "toast_wrong_user_pass": "Wrong username or password.",
                "toast_fill_all_fields": "Fill in all fields.",
                "toast_username_min": "Username must be at least 3 characters.",
                "toast_password_min": "Password must be at least 4 characters.",
                "toast_username_taken": "Username is already taken.",
                "toast_register_success": "Account '{0}' created successfully!",
                "toast_register_failed": "Failed to create account.",
                "toast_db_failed": "Database connection failed.",
                "toast_db_error": "Database error:",
                "notif_success": "Success!",
                "notif_error": "Error",
                "notif_warning": "Warning",
                "notif_info": "Info"
            },
            "Indonesia": {
                "window_title": "Crypto Insight • Masuk",
                "welcome_title": "Halo, Selamat Datang!",
                "welcome_subtitle": "Belum punya akun?",
                "btn_register": "Daftar",
                "welcome_back_title": "Selamat Datang Kembali!",
                "welcome_back_subtitle": "Sudah punya akun?",
                "btn_login": "Masuk",
                "login_title": "Masuk",
                "placeholder_username": "Nama Pengguna",
                "placeholder_password": "Kata Sandi",
                "forgot_password": "Lupa Kata Sandi?",
                "register_title": "Pendaftaran",
                "placeholder_email": "Email",
                "role_label": "Peran:",
                "toast_fill_fields": "Isi username dan password.",
                "toast_session_failed": "Tidak bisa membuat sesi online.",
                "toast_dashboard_not_found": "Dashboard tidak ditemukan:",
                "toast_wrong_user_pass": "Username atau password salah.",
                "toast_fill_all_fields": "Isi semua field.",
                "toast_username_min": "Username minimal 3 karakter.",
                "toast_password_min": "Password minimal 4 karakter.",
                "toast_username_taken": "Username sudah dipakai.",
                "toast_register_success": "Akun '{0}' berhasil dibuat!",
                "toast_register_failed": "Gagal membuat akun.",
                "toast_db_failed": "Koneksi database gagal.",
                "toast_db_error": "Database error:",
                "notif_success": "Berhasil!",
                "notif_error": "Error",
                "notif_warning": "Peringatan",
                "notif_info": "Info"
            }
        }

    def _setup_ui(self):
        """Setup UI dengan dua panel yang bisa swap"""
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.card_container = QtWidgets.QFrame()
        self.card_container.setObjectName("cardContainer")
        self.card_container.setFixedSize(900, 550)
        
        # ===== LEFT WELCOME PANEL (untuk Login mode) =====
        self.welcome_left = QtWidgets.QFrame(self.card_container)
        self.welcome_left.setObjectName("welcomePanel") 
        self.welcome_left.setGeometry(0, 0, 450, 550)
        
        welcome_left_layout = QtWidgets.QVBoxLayout(self.welcome_left)
        welcome_left_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_left_layout.setSpacing(25)
        welcome_left_layout.setContentsMargins(50, 50, 50, 50)
        
        # Icon/Logo
        welcome_icon_left = QtWidgets.QLabel("🚀")
        welcome_icon_left.setObjectName("welcomeIcon")
        welcome_icon_left.setAlignment(QtCore.Qt.AlignCenter)
        welcome_left_layout.addWidget(welcome_icon_left)
        
        self.welcome_left_title = QtWidgets.QLabel()
        self.welcome_left_title.setObjectName("welcomeTitle")
        self.welcome_left_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.welcome_left_subtitle = QtWidgets.QLabel()
        self.welcome_left_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_left_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_register = QtWidgets.QPushButton()
        self.btn_switch_to_register.setObjectName("welcomeBtn")
        self.btn_switch_to_register.setFixedSize(200, 50)
        self.btn_switch_to_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_register.clicked.connect(self.switch_to_register)
        
        welcome_left_layout.addWidget(self.welcome_left_title)
        welcome_left_layout.addWidget(self.welcome_left_subtitle)
        welcome_left_layout.addWidget(self.btn_switch_to_register, 0, QtCore.Qt.AlignCenter)
        
        # ===== RIGHT WELCOME PANEL (untuk Register mode) =====
        self.welcome_right = QtWidgets.QFrame(self.card_container)
        self.welcome_right.setObjectName("welcomePanel") 
        self.welcome_right.setGeometry(450, 0, 450, 550)
        self.welcome_right.hide()
        
        welcome_right_layout = QtWidgets.QVBoxLayout(self.welcome_right)
        welcome_right_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_right_layout.setSpacing(25)
        welcome_right_layout.setContentsMargins(50, 50, 50, 50)
        
        # Icon/Logo
        welcome_icon_right = QtWidgets.QLabel("👋")
        welcome_icon_right.setObjectName("welcomeIcon")
        welcome_icon_right.setAlignment(QtCore.Qt.AlignCenter)
        welcome_right_layout.addWidget(welcome_icon_right)
        
        self.welcome_right_title = QtWidgets.QLabel()
        self.welcome_right_title.setObjectName("welcomeTitle")
        self.welcome_right_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.welcome_right_subtitle = QtWidgets.QLabel()
        self.welcome_right_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_right_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_login = QtWidgets.QPushButton()
        self.btn_switch_to_login.setObjectName("welcomeBtn")
        self.btn_switch_to_login.setFixedSize(200, 50)
        self.btn_switch_to_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_login.clicked.connect(self.switch_to_login)
        
        welcome_right_layout.addWidget(self.welcome_right_title)
        welcome_right_layout.addWidget(self.welcome_right_subtitle)
        welcome_right_layout.addWidget(self.btn_switch_to_login, 0, QtCore.Qt.AlignCenter)
        
        # ===== LOGIN FORM PANEL (kanan saat login mode) =====
        self.login_panel = QtWidgets.QFrame(self.card_container)
        self.login_panel.setObjectName("formPanel") 
        self.login_panel.setGeometry(450, 0, 450, 550)
        
        login_layout = QtWidgets.QVBoxLayout(self.login_panel)
        login_layout.setContentsMargins(50, 50, 50, 50)
        login_layout.setSpacing(20)
        
        self.login_title = QtWidgets.QLabel() 
        self.login_title.setObjectName("formTitle")
        self.login_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.login_username_container = self._create_input(icon="👤")
        self.login_password_container = self._create_input(icon="🔒", is_password=True) 
        
        self.forgot_password_label = QtWidgets.QLabel() 
        self.forgot_password_label.setObjectName("linkText")
        self.forgot_password_label.setAlignment(QtCore.Qt.AlignRight)
        self.forgot_password_label.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.btn_login = QtWidgets.QPushButton() 
        self.btn_login.setObjectName("primaryBtn")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.do_login)
        
        login_layout.addWidget(self.login_title)
        login_layout.addSpacing(15)
        login_layout.addWidget(self.login_username_container)
        login_layout.addWidget(self.login_password_container) 
        login_layout.addWidget(self.forgot_password_label) 
        login_layout.addSpacing(15)
        login_layout.addWidget(self.btn_login)
        login_layout.addStretch() 
        
        # ===== REGISTER FORM PANEL (kiri saat register mode) =====
        self.register_panel = QtWidgets.QFrame(self.card_container)
        self.register_panel.setObjectName("formPanel") 
        self.register_panel.setGeometry(0, 0, 450, 550)
        self.register_panel.hide()
        
        register_layout = QtWidgets.QVBoxLayout(self.register_panel)
        register_layout.setContentsMargins(50, 40, 50, 40)
        register_layout.setSpacing(18)
        
        self.register_title = QtWidgets.QLabel() 
        self.register_title.setObjectName("formTitle")
        self.register_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.register_username_container = self._create_input(icon="👤")
        self.register_email_container = self._create_input(icon="✉️")
        self.register_password_container = self._create_input(icon="🔒", is_password=True) 
        
        role_container = QtWidgets.QWidget()
        role_layout = QtWidgets.QHBoxLayout(role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        self.role_label = QtWidgets.QLabel()
        self.role_label.setObjectName("roleLabel")
        self.register_role = QtWidgets.QComboBox()
        self.register_role.addItems(["user", "penerbit"])
        self.register_role.setObjectName("comboBox")
        role_layout.addWidget(self.role_label)
        role_layout.addWidget(self.register_role, 1)
        
        self.btn_register = QtWidgets.QPushButton() 
        self.btn_register.setObjectName("primaryBtn")
        self.btn_register.setFixedHeight(50)
        self.btn_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self.do_register)
        
        register_layout.addWidget(self.register_title)
        register_layout.addSpacing(10)
        register_layout.addWidget(self.register_username_container)
        register_layout.addWidget(self.register_email_container)
        register_layout.addWidget(self.register_password_container) 
        register_layout.addWidget(role_container)
        register_layout.addSpacing(10)
        register_layout.addWidget(self.btn_register)
        register_layout.addStretch() 
        
        main_layout.addWidget(self.card_container)
        
        # --- TOMBOL THEME & BAHASA ---
        controls_container = QtWidgets.QWidget(self.card_container)
        controls_layout = QtWidgets.QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.setObjectName("langCombo")
        self.lang_combo.addItems(self.translations.keys())
        self.lang_combo.setFixedSize(120, 38)
        self.lang_combo.activated[str].connect(self.switch_language)
        
        self.btn_theme_toggle = QtWidgets.QPushButton("🌙")
        self.btn_theme_toggle.setObjectName("themeBtn")
        self.btn_theme_toggle.setFixedSize(45, 38)
        self.btn_theme_toggle.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        
        controls_layout.addWidget(self.lang_combo)
        controls_layout.addWidget(self.btn_theme_toggle)
        
        controls_container.setGeometry(self.card_container.width() - 185, 15, 170, 38)
        controls_container.raise_()

    def _create_input(self, icon="", is_password=False):
        """Helper untuk create input dengan icon"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        input_field = QtWidgets.QLineEdit()
        input_field.setObjectName("formInput")
        input_field.setFixedHeight(50)
        if is_password:
            input_field.setEchoMode(QtWidgets.QLineEdit.Password)
        
        if icon:
            icon_label = QtWidgets.QLabel(icon)
            icon_label.setObjectName("inputIcon")
            layout.addWidget(icon_label)
        
        layout.addWidget(input_field)
        
        container.setObjectName("inputContainer")
        return container
    
    # ==========================================================
    # LOGIKA TERJEMAHAN
    # ==========================================================
    
    def switch_language(self, lang_text):
        """Ganti bahasa saat ini dan terjemahkan ulang UI"""
        self.current_lang = lang_text
        self.retranslateUi()

    def retranslateUi(self):
        """Atur ulang semua teks UI dengan versi terjemahan"""
        t = self.translations.get(self.current_lang, self.translations["English"])
        
        self.setWindowTitle(t["window_title"])
        
        self.welcome_left_title.setText(t["welcome_title"])
        self.welcome_left_subtitle.setText(t["welcome_subtitle"])
        self.btn_switch_to_register.setText(t["btn_register"])
        
        self.welcome_right_title.setText(t["welcome_back_title"])
        self.welcome_right_subtitle.setText(t["welcome_back_subtitle"])
        self.btn_switch_to_login.setText(t["btn_login"])
        
        self.login_title.setText(t["login_title"])
        self.login_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.login_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.forgot_password_label.setText(t["forgot_password"])
        self.btn_login.setText(t["btn_login"])
        
        self.register_title.setText(t["register_title"])
        self.register_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.register_email_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_email"])
        self.register_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.role_label.setText(t["role_label"])
        self.btn_register.setText(t["btn_register"])

    # ==========================================================
    # ANIMASI & INTERAKSI
    # ==========================================================

    def toggle_theme(self):
        if self.is_animating: return
        
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.btn_theme_toggle.setText("☀️")
        else:
            self.current_theme = "dark"
            self.btn_theme_toggle.setText("🌙")
        
        self._apply_style(self.current_theme)

    def switch_to_register(self):
        if not self.is_login_mode or self.is_animating:
            return
        
        self.is_login_mode = False
        self.is_animating = True
        
        anim_group_hide = QParallelAnimationGroup(self)
        
        anim_hide_1 = QPropertyAnimation(self.welcome_left, b"geometry")
        anim_hide_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_1.setStartValue(QRect(0, 0, 450, 550))
        anim_hide_1.setEndValue(QRect(225, 0, 0, 550)) 
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(450, 0, 450, 550))
        anim_hide_2.setEndValue(QRect(675, 0, 0, 550)) 
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_register)
        anim_group_hide.start()

    def _finish_flip_to_register(self):
        self.welcome_left.hide()
        self.login_panel.hide()
        
        self.register_panel.setGeometry(225, 0, 0, 550)
        self.welcome_right.setGeometry(675, 0, 0, 550)
        self.register_panel.show()
        self.welcome_right.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.register_panel, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(225, 0, 0, 550))
        anim_show_1.setEndValue(QRect(0, 0, 450, 550)) 
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(675, 0, 0, 550))
        anim_show_2.setEndValue(QRect(450, 0, 450, 550)) 
        anim_show_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_show.addAnimation(anim_show_1)
        anim_group_show.addAnimation(anim_show_2)
        anim_group_show.finished.connect(lambda: setattr(self, 'is_animating', False))
        anim_group_show.start()

    def switch_to_login(self):
        if self.is_login_mode or self.is_animating:
            return
        
        self.is_login_mode = True
        self.is_animating = True
        
        anim_group_hide = QParallelAnimationGroup(self)
        
        anim_hide_1 = QPropertyAnimation(self.register_panel, b"geometry")
        anim_hide_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_1.setStartValue(QRect(0, 0, 450, 550))
        anim_hide_1.setEndValue(QRect(225, 0, 0, 550))
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(450, 0, 450, 550))
        anim_hide_2.setEndValue(QRect(675, 0, 0, 550))
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_login)
        anim_group_hide.start()

    def _finish_flip_to_login(self):
        self.register_panel.hide()
        self.welcome_right.hide()
        
        self.welcome_left.setGeometry(225, 0, 0, 550)
        self.login_panel.setGeometry(675, 0, 0, 550)
        self.welcome_left.show()
        self.login_panel.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.welcome_left, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(225, 0, 0, 550))
        anim_show_1.setEndValue(QRect(0, 0, 450, 550))
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(675, 0, 0, 550))
        anim_show_2.setEndValue(QRect(450, 0, 450, 550))
        anim_show_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_show.addAnimation(anim_show_1)
        anim_group_show.addAnimation(anim_show_2)
        anim_group_show.finished.connect(lambda: setattr(self, 'is_animating', False))
        anim_group_show.start()

    def _get_trans_text(self, key):
        """Helper untuk mendapatkan teks terjemahan"""
        return self.translations[self.current_lang].get(key, f"<{key}>")

    def _get_trans_text_fmt(self, key, *args):
        """Helper untuk teks terjemahan dengan format"""
        text = self.translations[self.current_lang].get(key, f"<{key}>")
        try:
            return text.format(*args)
        except:
            return text

    # ==========================================================
    # LOGIC LOGIN & REGISTER
    # ==========================================================

    def do_login(self):
        if self.is_animating: return
        username_container = self.login_username_container
        password_container = self.login_password_container 
        
        username_input = username_container.findChild(QtWidgets.QLineEdit)
        password_input = password_container.findChild(QtWidgets.QLineEdit) 
        
        if not username_input or not password_input:
            return
        
        u = username_input.text().strip()
        p = password_input.text() 
        
        if not u or not p: 
            return self.toast(self._get_trans_text("toast_fill_fields"), "warning")
        
        role = verify_user(u, p)
        if role:
            sid = start_session(u)
            if sid is None:
                return self.toast(self._get_trans_text("toast_session_failed"), "error")
            
            try:
                from dashboard_ui import DashboardWindow
            except ImportError as e:
                return self.toast(f"{self._get_trans_text('toast_dashboard_not_found')} {str(e)}", "error")
            
            self.hide()
            self.dashboard = DashboardWindow(u, role, sid)
            self.dashboard.destroyed.connect(self.show)
            self.dashboard.show()
        else:
            return self.toast(self._get_trans_text("toast_wrong_user_pass"), "error")
    
    def do_register(self):
        if self.is_animating: return
        username_container = self.register_username_container
        email_container = self.register_email_container
        password_container = self.register_password_container 
        
        username_input = username_container.findChild(QtWidgets.QLineEdit)
        email_input = email_container.findChild(QtWidgets.QLineEdit)
        password_input = password_container.findChild(QtWidgets.QLineEdit) 
        
        if not username_input or not email_input or not password_input:
            return
        
        u = username_input.text().strip()
        e = email_input.text().strip()
        p = password_input.text() 
        role = self.register_role.currentText()
        
        if not u or not e or not p: 
            return self.toast(self._get_trans_text("toast_fill_all_fields"), "warning")
        if len(u) < 3:
            return self.toast(self._get_trans_text("toast_username_min"), "warning")
        if len(p) < 4: 
            return self.toast(self._get_trans_text("toast_password_min"), "warning")
        if user_exists(u):
            return self.toast(self._get_trans_text("toast_username_taken"), "error")
        
        ok = create_user(u, p, role) 
        if ok:
            self.toast(self._get_trans_text_fmt("toast_register_success", u), "success") 
            username_input.clear()
            email_input.clear()
            password_input.clear() 
            QtCore.QTimer.singleShot(1500, self.switch_to_login)
        else:
            self.toast(self._get_trans_text("toast_register_failed"), "error")
    
    def toast(self, text: str, notification_type="info"):
        """Show notification"""
        if notification_type == "success":
            title = self._get_trans_text("notif_success")
            notif = ModernNotification.success(self, title, text)
        elif notification_type == "error":
            title = self._get_trans_text("notif_error")
            notif = ModernNotification.error(self, title, text)
        elif notification_type == "warning":
            title = self._get_trans_text("notif_warning")
            notif = ModernNotification.warning(self, title, text)
        else:
            title = self._get_trans_text("notif_info")
            notif = ModernNotification.info(self, title, text)
        notif.show_notification()
    
    def _init_database(self):
        """Initialize database"""
        try:
            if not health_check():
                self.toast(self._get_trans_text("toast_db_failed"), "error")
                return
            setup_database()
        except Exception as e:
            self.toast(f"{self._get_trans_text('toast_db_error')} {str(e)}", "error")
    
    def _apply_style(self, theme):
        """Apply enhanced stylesheet dengan warna yang lebih baik"""
        if theme not in self.themes:
            theme = "dark"
        
        c = self.themes[theme]     
        com = self.common_colors   
            
        self.setStyleSheet(f"""
            /* Root */
            #root {{
                background: {c["root_bg"]};
            }}
            
            #cardContainer {{
                background: {c["card_bg"]}; 
                border-radius: 30px;
                border: 1px solid {c["card_border"]};
                overflow: hidden;
            }}
            
            /* --- Controls (Theme & Language) --- */
            #themeBtn, #langCombo {{
                background: {c["input_bg"]};
                color: {c["input_text"]};
                border: 1px solid {c["input_border"]};
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }}
            #themeBtn:hover, #langCombo:hover {{
                background: {c["social_btn_hover_bg"]};
                border-color: {c["input_border_focus"]};
            }}
            
            #langCombo::drop-down {{
                border: none;
                margin-right: 8px;
            }}
            #langCombo QAbstractItemView {{
                background: {c["combo_item_bg"]};
                color: {c["combo_text"]};
                border: 1px solid {c["combo_border"]};
                selection-background-color: {c["combo_item_selected"]};
                selection-color: white;
            }}
            
            /* Welcome Panel */
            #welcomePanel {{
                background: transparent; 
                border-radius: 30px;
            }}
            
            #welcomeIcon {{
                font-size: 64px;
            }}
            
            #welcomeTitle {{
                color: {com["welcome_text"]};
                font-size: 36px;
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            
            #welcomeSubtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin-top: 5px;
            }}
            
            #welcomeBtn {{
                background: transparent;
                color: {com["welcome_text"]};
                border: 2px solid {com["welcome_btn_border"]};
                border-radius: 25px;
                font-size: 16px;
                font-weight: 600;
                padding: 12px 35px;
            }}
            
            #welcomeBtn:hover {{
                background: rgba(255, 255, 255, 0.15);
                transform: scale(1.05);
            }}
            
            /* Form Panel */
            #formPanel {{
                background: {c["form_bg"]}; 
                border-radius: 30px;
                border: 1px solid {c["card_border"]}; 
            }}
            
            #formTitle {{
                color: {c["form_title"]};
                font-size: 32px;
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            
            /* Input Container */
            #inputContainer {{
                background: {c["input_bg"]}; 
                border: 1px solid {c["input_border"]};
                border-radius: 14px;
                min-height: 50px;
            }}
            
            #inputContainer:focus-within {{
                border: 2px solid {c["input_border_focus"]};
            }}
            
            #inputIcon {{
                color: {c["input_icon"]};
                font-size: 20px;
            }}
            
            #formInput {{
                background: transparent;
                border: none;
                color: {c["input_text"]};
                font-size: 15px;
                padding: 0;
            }}
            
            #formInput:focus {{
                background: transparent;
            }}
            
            /* ComboBox */
            #comboBox {{
                background: {c["combo_bg"]};
                color: {c["combo_text"]};
                border: 1px solid {c["combo_border"]};
                border-radius: 14px;
                padding: 14px;
                font-size: 15px;
            }}
            
            #comboBox:focus {{
                border: 2px solid {c["input_border_focus"]};
            }}
            
            #comboBox::drop-down {{
                border: none;
            }}
            
            #comboBox QAbstractItemView {{
                background: {c["combo_item_bg"]};
                color: {c["combo_text"]};
                border: 1px solid {c["combo_border"]};
                selection-background-color: {c["combo_item_selected"]};
                selection-color: white;
            }}
            
            #roleLabel {{
                color: {c["input_icon"]}; 
                font-size: 15px;
                font-weight: 600;
            }}
            
            /* Primary Button */
            #primaryBtn {{
                background: {com["primary_btn_bg"]};
                color: {com["primary_btn_text"]};
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: 700;
                padding: 14px;
            }}
            
            #primaryBtn:hover {{
                background: {com["primary_btn_hover"]};
                transform: translateY(-2px);
            }}
            
            /* Link Text */
            #linkText {{
                color: {com["link_text"]};
                font-size: 13px;
                font-weight: 600;
            }}
            
            #linkText:hover {{
                text-decoration: underline;
            }}
        """)
        
        font = QtGui.QFont("Segoe UI")
        font.setPointSize(10)
        self.setFont(font)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = EnhancedAuthWindow()
    w.show()
    sys.exit(app.exec_())
