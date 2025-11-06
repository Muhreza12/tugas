# auth_ui_tiktok_style.py — FINAL v5 (Manual Dictionary Translation)
"""
Login/Register UI dengan panel yang "dibalik" (flip)

Features:
- 3D Flip "squash/expand" animation (0.6s)
- 💎 "Glassmorphism"
- 🪄 Login/Register dengan Password
- 🌐 Multi-Language (Manual Dictionary) - Termasuk "Bahasa Kuin"
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


class TikTokAuthWindow(QtWidgets.QWidget):
    """Main auth window dengan 3D Flip style"""
    
    ANIMATION_DURATION = 600 
    EASING_CURVE = QEasingCurve.InOutCubic

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State tracking
        self.is_login_mode = True  
        self.current_theme = "light" 
        self.is_animating = False 
        
        # Bahasa default
        self.current_lang = "English" 
        
        self._define_themes()
        self._define_translations() # Buat kamus bahasa
        self._setup_ui()
        self._apply_style(self.current_theme)
        
        # Terapkan teks awal
        self.retranslateUi() 
        
        self._init_database()
        
    def _define_themes(self):
        """Mendefinisikan palet warna untuk Light dan Dark mode"""
        
        BRAND_COLOR_PRIMARY = "#8B5CF6" 
        BRAND_COLOR_SECONDARY = "#7C3AED" 
        
        self.common_colors = {
            "welcome_bg": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {BRAND_COLOR_PRIMARY}, stop:1 {BRAND_COLOR_SECONDARY})",
            "welcome_text": "white",
            "welcome_btn_border": "white",
            "primary_btn_bg": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {BRAND_COLOR_PRIMARY}, stop:1 {BRAND_COLOR_SECONDARY})",
            "primary_btn_hover": BRAND_COLOR_SECONDARY,
            "primary_btn_text": "white",
            "link_text": BRAND_COLOR_PRIMARY
        }
        
        self.themes = {
            "light": {
                "root_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0e7ff, stop:1 #ccd5ff)",
                "card_bg": self.common_colors["welcome_bg"], 
                "form_bg": "rgba(255, 255, 255, 0.7)", 
                "card_border": "rgba(255, 255, 255, 0.5)", 
                "form_title": "#1f2937",
                "input_bg": "#f3f4f6", 
                "input_text": "#1f2937",
                "input_icon": "#6b7280",
                "social_label": "#9ca3af",
                "combo_bg": "#f3f4f6",
                "combo_text": "#1f2937",
                "combo_item_bg": "#f3f4f6",
                "combo_item_selected": BRAND_COLOR_PRIMARY,
                "social_btn_bg": "white",
                "social_btn_text": "#1f2937",
                "social_btn_border": "#e5e7eb",
                "social_btn_hover_bg": "#f9fafb"
            },
            "dark": {
                "root_bg": "#111827", 
                "card_bg": self.common_colors["welcome_bg"], 
                "form_bg": "rgba(31, 41, 55, 0.7)", 
                "card_border": "rgba(255, 255, 255, 0.3)", 
                "form_title": "#ffffff",
                "input_bg": "#374151", 
                "input_text": "#ffffff",
                "input_icon": "#9ca3af",
                "social_label": "#9ca3af",
                "combo_bg": "#374151",
                "combo_text": "#ffffff",
                "combo_item_bg": "#374151",
                "combo_item_selected": BRAND_COLOR_PRIMARY,
                "social_btn_bg": "#374151",
                "social_btn_text": "#ffffff",
                "social_btn_border": "#4b5563",
                "social_btn_hover_bg": "#4b5563"
            }
        }
        
    def _define_translations(self):
        """
        Inilah kamus untuk semua bahasa Anda.
        Cukup tambahkan kata-kata Anda di "Bahasa Kuin".
        """
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
            },
            "Bahasa Kuin": {
                # --- INI DIA 20+ KATA ANDA ---
                "window_title": "Crypto Insight • jeMas",
                "welcome_title": "jeHal, jeDat!",
                "welcome_subtitle": "jeBel punya akun?",
                "btn_register": "jeDaf",
                "welcome_back_title": "jeBal!", # jeKembali
                "welcome_back_subtitle": "jeSud punya akun?",
                "btn_login": "jeMas",
                "login_title": "jeMas",
                "placeholder_username": "jeNam", # jeNama
                "placeholder_password": "jeSan", # jeSandi
                "forgot_password": "jeLup San?",
                "register_title": "jeDaf", # jeDaftar
                "placeholder_email": "jeMail",
                "role_label": "jePer:", # jePeran
                "toast_fill_fields": "jeIsi nam & san.",
                "toast_session_failed": "jeGag sesi.",
                "toast_dashboard_not_found": "jeDash tidak ada:",
                "toast_wrong_user_pass": "jeNam/san salah.",
                "toast_fill_all_fields": "jeIsi semua.",
                "toast_username_min": "jeNam min 3 kar.",
                "toast_password_min": "jeSan min 4 kar.",
                "toast_username_taken": "jeNam sudah ada.",
                "toast_register_success": "jeAkun '{0}' jadi!",
                "toast_register_failed": "jeGag buat akun.",
                "toast_db_failed": "jeDB gagal.",
                "toast_db_error": "jeDB error:",
                "notif_success": "jeSil!", # jeBerhasil
                "notif_error": "jeEror",
                "notif_warning": "jeAwas!",
                "notif_info": "jeInfo"
            }
        }

    def _setup_ui(self):
        """Setup UI dengan dua panel yang bisa swap"""
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.card_container = QtWidgets.QFrame()
        self.card_container.setObjectName("cardContainer")
        self.card_container.setFixedSize(800, 500)
        
        # ===== LEFT WELCOME PANEL (untuk Login mode) =====
        self.welcome_left = QtWidgets.QFrame(self.card_container)
        self.welcome_left.setObjectName("welcomePanel") 
        self.welcome_left.setGeometry(0, 0, 400, 500)
        
        welcome_left_layout = QtWidgets.QVBoxLayout(self.welcome_left)
        welcome_left_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_left_layout.setSpacing(20)
        
        # Jadikan widget sebagai properti self
        self.welcome_left_title = QtWidgets.QLabel()
        self.welcome_left_title.setObjectName("welcomeTitle")
        self.welcome_left_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.welcome_left_subtitle = QtWidgets.QLabel()
        self.welcome_left_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_left_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_register = QtWidgets.QPushButton()
        self.btn_switch_to_register.setObjectName("welcomeBtn")
        self.btn_switch_to_register.setFixedSize(180, 45)
        self.btn_switch_to_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_register.clicked.connect(self.switch_to_register)
        
        welcome_left_layout.addWidget(self.welcome_left_title)
        welcome_left_layout.addWidget(self.welcome_left_subtitle)
        welcome_left_layout.addWidget(self.btn_switch_to_register, 0, QtCore.Qt.AlignCenter)
        
        # ===== RIGHT WELCOME PANEL (untuk Register mode) =====
        self.welcome_right = QtWidgets.QFrame(self.card_container)
        self.welcome_right.setObjectName("welcomePanel") 
        self.welcome_right.setGeometry(400, 0, 400, 500)
        self.welcome_right.hide()
        
        welcome_right_layout = QtWidgets.QVBoxLayout(self.welcome_right)
        welcome_right_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_right_layout.setSpacing(20)
        
        self.welcome_right_title = QtWidgets.QLabel()
        self.welcome_right_title.setObjectName("welcomeTitle")
        self.welcome_right_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.welcome_right_subtitle = QtWidgets.QLabel()
        self.welcome_right_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_right_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_login = QtWidgets.QPushButton()
        self.btn_switch_to_login.setObjectName("welcomeBtn")
        self.btn_switch_to_login.setFixedSize(180, 45)
        self.btn_switch_to_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_login.clicked.connect(self.switch_to_login)
        
        welcome_right_layout.addWidget(self.welcome_right_title)
        welcome_right_layout.addWidget(self.welcome_right_subtitle)
        welcome_right_layout.addWidget(self.btn_switch_to_login, 0, QtCore.Qt.AlignCenter)
        
        # ===== LOGIN FORM PANEL (kanan saat login mode) =====
        self.login_panel = QtWidgets.QFrame(self.card_container)
        self.login_panel.setObjectName("formPanel") 
        self.login_panel.setGeometry(400, 0, 400, 500)
        
        login_layout = QtWidgets.QVBoxLayout(self.login_panel)
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_layout.setSpacing(15)
        
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
        self.btn_login.setFixedHeight(45)
        self.btn_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.do_login)
        
        login_layout.addWidget(self.login_title)
        login_layout.addSpacing(10)
        login_layout.addWidget(self.login_username_container)
        login_layout.addWidget(self.login_password_container) 
        login_layout.addWidget(self.forgot_password_label) 
        login_layout.addSpacing(10)
        login_layout.addWidget(self.btn_login)
        login_layout.addStretch() 
        
        # ===== REGISTER FORM PANEL (kiri saat register mode) =====
        self.register_panel = QtWidgets.QFrame(self.card_container)
        self.register_panel.setObjectName("formPanel") 
        self.register_panel.setGeometry(0, 0, 400, 500)
        self.register_panel.hide()
        
        register_layout = QtWidgets.QVBoxLayout(self.register_panel)
        register_layout.setContentsMargins(40, 30, 40, 30)
        register_layout.setSpacing(12)
        
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
        self.register_role.addItems(["user", "penerbit"]) # Ini tidak diterjemahkan
        self.register_role.setObjectName("comboBox")
        role_layout.addWidget(self.role_label)
        role_layout.addWidget(self.register_role, 1)
        
        self.btn_register = QtWidgets.QPushButton() 
        self.btn_register.setObjectName("primaryBtn")
        self.btn_register.setFixedHeight(45)
        self.btn_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self.do_register)
        
        register_layout.addWidget(self.register_title)
        register_layout.addSpacing(5)
        register_layout.addWidget(self.register_username_container)
        register_layout.addWidget(self.register_email_container)
        register_layout.addWidget(self.register_password_container) 
        register_layout.addWidget(role_container)
        register_layout.addSpacing(5)
        register_layout.addWidget(self.btn_register)
        register_layout.addStretch() 
        
        main_layout.addWidget(self.card_container)
        
        # --- TOMBOL THEME ---
        self.btn_theme_toggle = QtWidgets.QPushButton("🌙", self.card_container)
        self.btn_theme_toggle.setObjectName("themeBtn")
        self.btn_theme_toggle.setFixedSize(40, 40)
        self.btn_theme_toggle.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_theme_toggle.move(self.card_container.width() - 55, 15)
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        
        # --- COMBOBOX BAHASA BARU ---
        self.lang_combo = QtWidgets.QComboBox(self.card_container)
        self.lang_combo.setObjectName("langCombo")
        # Ambil nama bahasa dari kamus
        self.lang_combo.addItems(self.translations.keys())
        self.lang_combo.setFixedSize(110, 32) # Sedikit lebih lebar
        self.lang_combo.move(self.card_container.width() - 175, 20) # Geser ke kiri
        self.lang_combo.activated[str].connect(self.switch_language)
        
        self.btn_theme_toggle.raise_() 
        self.lang_combo.raise_()

    def _create_input(self, icon="", is_password=False):
        """Helper untuk create input dengan icon"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        input_field = QtWidgets.QLineEdit()
        input_field.setObjectName("formInput")
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
    # LOGIKA BARU UNTUK TERJEMAHAN
    # ==========================================================
    
    def switch_language(self, lang_text):
        """Ganti bahasa saat ini dan terjemahkan ulang UI"""
        self.current_lang = lang_text
        self.retranslateUi()

    def retranslateUi(self):
        """Atur ulang semua teks UI dengan versi terjemahan"""
        
        # Dapatkan kamus untuk bahasa saat ini
        t = self.translations.get(self.current_lang, self.translations["English"])
        
        # Teks Window
        self.setWindowTitle(t["window_title"])
        
        # Panel Welcome Kiri
        self.welcome_left_title.setText(t["welcome_title"])
        self.welcome_left_subtitle.setText(t["welcome_subtitle"])
        self.btn_switch_to_register.setText(t["btn_register"])
        
        # Panel Welcome Kanan
        self.welcome_right_title.setText(t["welcome_back_title"])
        self.welcome_right_subtitle.setText(t["welcome_back_subtitle"])
        self.btn_switch_to_login.setText(t["btn_login"])
        
        # Panel Login
        self.login_title.setText(t["login_title"])
        self.login_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.login_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.forgot_password_label.setText(t["forgot_password"])
        self.btn_login.setText(t["btn_login"])
        
        # Panel Register
        self.register_title.setText(t["register_title"])
        self.register_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.register_email_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_email"])
        self.register_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.role_label.setText(t["role_label"])
        self.btn_register.setText(t["btn_register"])

    # ==========================================================
    # SISA KODE (TETAP SAMA)
    # ==========================================================

    def toggle_theme(self):
        if self.is_animating: return
        
        if self.current_theme == "light":
            self.current_theme = "dark"
            self.btn_theme_toggle.setText("☀️")
        else:
            self.current_theme = "light"
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
        anim_hide_1.setStartValue(QRect(0, 0, 400, 500))
        anim_hide_1.setEndValue(QRect(200, 0, 0, 500)) 
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(400, 0, 400, 500))
        anim_hide_2.setEndValue(QRect(600, 0, 0, 500)) 
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_register)
        anim_group_hide.start()

    def _finish_flip_to_register(self):
        self.welcome_left.hide()
        self.login_panel.hide()
        
        self.register_panel.setGeometry(200, 0, 0, 500)
        self.welcome_right.setGeometry(600, 0, 0, 500)
        self.register_panel.show()
        self.welcome_right.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.register_panel, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(200, 0, 0, 500))
        anim_show_1.setEndValue(QRect(0, 0, 400, 500)) 
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(600, 0, 0, 500))
        anim_show_2.setEndValue(QRect(400, 0, 400, 500)) 
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
        anim_hide_1.setStartValue(QRect(0, 0, 400, 500))
        anim_hide_1.setEndValue(QRect(200, 0, 0, 500))
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(400, 0, 400, 500))
        anim_hide_2.setEndValue(QRect(600, 0, 0, 500))
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_login)
        anim_group_hide.start()

    def _finish_flip_to_login(self):
        self.register_panel.hide()
        self.welcome_right.hide()
        
        self.welcome_left.setGeometry(200, 0, 0, 500)
        self.login_panel.setGeometry(600, 0, 0, 500)
        self.welcome_left.show()
        self.login_panel.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.welcome_left, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(200, 0, 0, 500))
        anim_show_1.setEndValue(QRect(0, 0, 400, 500))
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(600, 0, 0, 500))
        anim_show_2.setEndValue(QRect(400, 0, 400, 500))
        anim_show_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_show.addAnimation(anim_show_1)
        anim_group_show.addAnimation(anim_show_2)
        anim_group_show.finished.connect(lambda: setattr(self, 'is_animating', False))
        anim_group_show.start()

    def _get_trans_text(self, key):
        """Helper untuk mendapatkan teks terjemahan dengan aman"""
        return self.translations[self.current_lang].get(key, f"<{key}>")

    def _get_trans_text_fmt(self, key, *args):
        """Helper untuk teks terjemahan dengan format .format()"""
        text = self.translations[self.current_lang].get(key, f"<{key}>")
        try:
            return text.format(*args)
        except:
            return text

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
        # Judul notifikasi juga diterjemahkan
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
        """Apply TikTok-style stylesheet SECARA DINAMIS"""
        if theme not in self.themes:
            theme = "light"
        
        c = self.themes[theme]     
        com = self.common_colors   
            
        self.setStyleSheet(f"""
            /* Root */
            #root {{
                background: {c["root_bg"]};
            }}
            
            #cardContainer {{
                background: {c["card_bg"]}; 
                border-radius: 25px;
                border: none; 
                overflow: hidden; 
            }}
            
            /* --- Theme & Language Buttons --- */
            #themeBtn {{
                background: {c["input_bg"]};
                color: {c["input_text"]};
                border: 1px solid {c["card_border"]};
                border-radius: 16px; /* Dibuat seragam */
                font-size: 18px;
            }}
            #themeBtn:hover {{
                background: {c["social_btn_hover_bg"]};
            }}
            
            #langCombo {{
                background: {c["input_bg"]};
                color: {c["input_text"]};
                border: 1px solid {c["card_border"]};
                border-radius: 16px;
                font-size: 12px;
                padding-left: 10px;
            }}
            #langCombo::drop-down {{
                border: none;
                margin-right: 5px;
            }}
            #langCombo QAbstractItemView {{
                background: {c["combo_item_bg"]};
                color: {c["combo_text"]};
                selection-background-color: {c["combo_item_selected"]};
                selection-color: white;
            }}
            
            /* Welcome Panel */
            #welcomePanel {{
                background: transparent; 
                border-radius: 25px;
            }}
            
            #welcomeTitle {{
                color: {com["welcome_text"]};
                font-size: 32px;
                font-weight: 800;
            }}
            
            #welcomeSubtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
            }}
            
            #welcomeBtn {{
                background: transparent;
                color: {com["welcome_text"]};
                border: 2px solid {com["welcome_btn_border"]};
                border-radius: 22px;
                font-size: 16px;
                font-weight: 600;
                padding: 10px 30px;
            }}
            
            #welcomeBtn:hover {{
                background: rgba(255, 255, 255, 0.1);
            }}
            
            /* Form Panel */
            #formPanel {{
                background: {c["form_bg"]}; 
                border-radius: 25px;
                border: 1px solid {c["card_border"]}; 
            }}
            
            #formTitle {{
                color: {c["form_title"]};
                font-size: 28px;
                font-weight: 700;
            }}
            
            /* Input Container */
            #inputContainer {{
                background: {c["input_bg"]}; 
                border-radius: 12px;
                min-height: 48px;
            }}
            
            #inputIcon {{
                color: {c["input_icon"]};
                font-size: 18px;
            }}
            
            #formInput {{
                background: transparent;
                border: none;
                color: {c["input_text"]};
                font-size: 14px;
                padding: 0;
            }}
            
            #formInput:focus {{
                background: transparent;
            }}
            
            /* ComboBox */
            #comboBox {{
                background: {c["combo_bg"]};
                color: {c["combo_text"]};
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }}
            
            #comboBox::drop-down {{
                border: none;
            }}
            
            #comboBox QAbstractItemView {{
                background: {c["combo_item_bg"]};
                color: {c["combo_text"]};
                selection-background-color: {c["combo_item_selected"]};
                selection-color: white;
            }}
            
            #roleLabel {{
                color: {c["input_icon"]}; 
                font-size: 14px;
            }}
            
            /* Primary Button */
            #primaryBtn {{
                background: {com["primary_btn_bg"]};
                color: {com["primary_btn_text"]};
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                padding: 12px;
            }}
            
            #primaryBtn:hover {{
                background: {com["primary_btn_hover"]};
            }}
            
            /* Labels */
            #socialLabel {{
                color: {c["social_label"]};
                font-size: 12px;
            }}
            
            #linkText {{
                color: {com["link_text"]};
                font-size: 12px;
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
    w = TikTokAuthWindow()
    w.show()
    sys.exit(app.exec_())