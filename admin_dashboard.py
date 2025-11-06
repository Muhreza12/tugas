# enhanced_admin_dashboard.py - Admin Dashboard dengan Monitoring Terintegrasi
from PyQt5 import QtWidgets, QtCore, QtGui
from db import connect
import datetime
import sqlite3
import json
from pathlib import Path

class EnhancedAdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username
        self.setWindowTitle("Crypto Insight — Enhanced Admin Dashboard with Monitoring")
        self.resize(1200, 800)
        
        # Setup logging database
        self.setup_monitoring_db()
        
        # Timer untuk auto-refresh
        self.auto_refresh_timer = QtCore.QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_check_new_users)
        self.auto_refresh_enabled = True
        self.last_user_count = 0
        
        # Setup UI
        self.setup_ui()
        
        # Muat data awal dan mulai auto-refresh
        self.load_users()
        self.load_monitoring_data()
        self.start_auto_refresh()
        self.add_log("✅ Enhanced Admin dashboard dimulai - Monitoring aktif")
        
        # Log admin login
        self.log_admin_activity("ADMIN_LOGIN", f"Admin {username} logged into dashboard")
        
    def setup_monitoring_db(self):
        """Setup database untuk monitoring."""
        self.monitoring_db = "admin_monitoring.db"
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    username TEXT,
                    action TEXT,
                    details TEXT,
                    ip_address TEXT DEFAULT 'localhost',
                    success BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    logout_time DATETIME,
                    session_duration INTEGER,
                    role TEXT,
                    ip_address TEXT DEFAULT 'localhost'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    admin_username TEXT,
                    action TEXT,
                    target_user TEXT,
                    details TEXT
                )
            """)
        
    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        # Main layout dengan tab widget
        main_layout = QtWidgets.QVBoxLayout(central)
        
        # Header
        title = QtWidgets.QLabel(f"👑 Enhanced Admin Dashboard - {self.username}")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 700; margin: 8px 0; color: #4f46e5;")
        main_layout.addWidget(title)
        
        # Tab widget untuk berbagai fungsi
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: User Management (existing functionality)
        self.setup_user_management_tab()
        
        # Tab 2: Activity Monitoring
        self.setup_monitoring_tab()
        
        # Tab 3: Statistics & Reports
        self.setup_statistics_tab()
        
        # Tab 4: System Logs
        self.setup_logs_tab()
        
        # Logout button
        logout_layout = QtWidgets.QHBoxLayout()
        logout_layout.addStretch()
        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: #dc2626; color: white; font-weight: 600;
                padding: 8px 16px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        logout_layout.addWidget(self.logout_btn)
        main_layout.addLayout(logout_layout)
        
    def setup_user_management_tab(self):
        """Tab untuk manajemen user (existing functionality)."""
        user_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(user_tab)
        
        # Status bar untuk monitoring
        self.status_label = QtWidgets.QLabel("🟢 Auto-monitoring aktif - Menunggu user baru...")
        self.status_label.setStyleSheet("color: #059669; font-weight: 600; padding: 8px; background: #ecfdf5; border-radius: 6px; margin: 4px 0;")
        layout.addWidget(self.status_label)
        
        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("🔄 Refresh Manual")
        self.copy_btn = QtWidgets.QPushButton("📋 Copy Terpilih")
        
        # Toggle auto-refresh
        self.auto_refresh_btn = QtWidgets.QPushButton("⏸️ Pause Auto-Check")
        self.auto_refresh_btn.setStyleSheet("background: #f59e0b; color: white; font-weight: 600; padding: 6px 12px; border-radius: 6px;")
        
        # Interval setting
        interval_layout = QtWidgets.QHBoxLayout()
        interval_layout.addWidget(QtWidgets.QLabel("Check setiap:"))
        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        self.interval_spin.setSuffix(" detik")
        interval_layout.addWidget(self.interval_spin)
        
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.copy_btn)
        toolbar.addLayout(interval_layout)
        toolbar.addWidget(self.auto_refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Tabel user
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Status", "Last Login"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 100)
        layout.addWidget(self.table)
        
        # Signals
        self.refresh_btn.clicked.connect(self.manual_refresh)
        self.copy_btn.clicked.connect(self.copy_selected_rows)
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        self.interval_spin.valueChanged.connect(self.update_refresh_interval)
        
        self.tab_widget.addTab(user_tab, "👥 User Management")
        
    def setup_monitoring_tab(self):
        """Tab untuk monitoring aktivitas real-time."""
        monitoring_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(monitoring_tab)
        
        # Control panel
        control_panel = QtWidgets.QHBoxLayout()
        
        refresh_monitoring_btn = QtWidgets.QPushButton("🔄 Refresh Monitoring")
        refresh_monitoring_btn.clicked.connect(self.load_monitoring_data)
        refresh_monitoring_btn.setStyleSheet("""
            QPushButton {
                background: #059669; color: white; font-weight: 600;
                padding: 8px 16px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #047857; }
        """)
        
        export_btn = QtWidgets.QPushButton("📊 Export Data")
        export_btn.clicked.connect(self.export_monitoring_data)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #7c3aed; color: white; font-weight: 600;
                padding: 8px 16px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #6d28d9; }
        """)
        
        control_panel.addWidget(refresh_monitoring_btn)
        control_panel.addWidget(export_btn)
        control_panel.addStretch()
        layout.addLayout(control_panel)
        
        # Statistics cards
        stats_layout = QtWidgets.QGridLayout()
        
        self.stats_cards = {}
        stats_info = [
            ("total_logins", "Total Logins", "#3b82f6"),
            ("active_today", "Active Today", "#10b981"),
            ("failed_attempts", "Failed Attempts", "#dc2626"),
            ("admin_actions", "Admin Actions", "#7c3aed")
        ]
        
        for i, (key, label, color) in enumerate(stats_info):
            card = self.create_stat_card(label, "0", color)
            self.stats_cards[key] = card['value_label']
            stats_layout.addWidget(card['widget'], i // 2, i % 2)
        
        layout.addLayout(stats_layout)
        
        # Recent activities table
        activities_group = QtWidgets.QGroupBox("📋 Recent User Activities")
        activities_layout = QtWidgets.QVBoxLayout(activities_group)
        
        self.activities_table = QtWidgets.QTableWidget(0, 5)
        self.activities_table.setHorizontalHeaderLabels(["Time", "Username", "Action", "Details", "Success"])
        
        header = self.activities_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 120)
        header.resizeSection(1, 100)
        header.resizeSection(2, 150)
        header.resizeSection(4, 80)
        
        self.activities_table.setAlternatingRowColors(True)
        activities_layout.addWidget(self.activities_table)
        
        layout.addWidget(activities_group)
        
        self.tab_widget.addTab(monitoring_tab, "📊 Activity Monitor")
        
    def setup_statistics_tab(self):
        """Tab untuk statistik dan laporan."""
        stats_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(stats_tab)
        
        # Period selector
        period_layout = QtWidgets.QHBoxLayout()
        period_layout.addWidget(QtWidgets.QLabel("Period:"))
        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["Last 24 hours", "Last 7 days", "Last 30 days"])
        self.period_combo.setCurrentText("Last 7 days")
        self.period_combo.currentTextChanged.connect(self.update_statistics)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Statistics display
        self.stats_text = QtWidgets.QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QtGui.QFont("Courier New", 10))
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background: #f8fafc; border: 1px solid #e2e8f0;
                border-radius: 6px; padding: 12px;
            }
        """)
        layout.addWidget(self.stats_text)
        
        # Generate report button
        report_btn = QtWidgets.QPushButton("📋 Generate Detailed Report")
        report_btn.clicked.connect(self.generate_detailed_report)
        report_btn.setStyleSheet("""
            QPushButton {
                background: #dc2626; color: white; font-weight: 600;
                padding: 10px 20px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        layout.addWidget(report_btn)
        
        self.tab_widget.addTab(stats_tab, "📈 Statistics")
        
    def setup_logs_tab(self):
        """Tab untuk system logs."""
        logs_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(logs_tab)
        
        # Log area untuk aktivitas terbaru
        log_label = QtWidgets.QLabel("📋 System & Admin Activity Logs:")
        log_label.setStyleSheet("font-weight: 600; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        layout.addWidget(self.log_text)
        
        # Clear logs button
        clear_btn = QtWidgets.QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #6b7280; color: white; font-weight: 600;
                padding: 8px 16px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #4b5563; }
        """)
        layout.addWidget(clear_btn)
        
        self.tab_widget.addTab(logs_tab, "📝 System Logs")
        
    def create_stat_card(self, title, value, color):
        """Create a statistics card widget."""
        card_widget = QtWidgets.QFrame()
        card_widget.setStyleSheet(f"""
            QFrame {{
                background: white; border: 1px solid #e2e8f0;
                border-radius: 8px; padding: 16px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(card_widget)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 600;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return {'widget': card_widget, 'value_label': value_label}
        
    def log_admin_activity(self, action, details="", target_user=""):
        """Log admin activities untuk monitoring."""
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                INSERT INTO admin_actions (admin_username, action, target_user, details)
                VALUES (?, ?, ?, ?)
            """, (self.username, action, target_user, details))
        
        self.add_log(f"🔧 ADMIN: {action} - {details}")
        
    def log_user_activity(self, username, action, details="", success=True):
        """Log user activities."""
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                INSERT INTO user_activities (username, action, details, success)
                VALUES (?, ?, ?, ?)
            """, (username, action, details, success))
            
    def load_monitoring_data(self):
        """Load monitoring data untuk tab monitoring."""
        try:
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # Total logins
                cursor.execute("SELECT COUNT(*) FROM user_activities WHERE action LIKE '%LOGIN%'")
                total_logins = cursor.fetchone()[0]
                
                # Active today
                cursor.execute("""
                    SELECT COUNT(DISTINCT username) FROM user_activities 
                    WHERE date(timestamp) = date('now') AND action LIKE '%LOGIN%'
                """)
                active_today = cursor.fetchone()[0]
                
                # Failed attempts
                cursor.execute("""
                    SELECT COUNT(*) FROM user_activities 
                    WHERE action LIKE '%LOGIN%' AND success = 0
                """)
                failed_attempts = cursor.fetchone()[0]
                
                # Admin actions
                cursor.execute("SELECT COUNT(*) FROM admin_actions")
                admin_actions = cursor.fetchone()[0]
                
                # Update statistics cards
                self.stats_cards["total_logins"].setText(str(total_logins))
                self.stats_cards["active_today"].setText(str(active_today))
                self.stats_cards["failed_attempts"].setText(str(failed_attempts))
                self.stats_cards["admin_actions"].setText(str(admin_actions))
                
                # Load recent activities
                cursor.execute("""
                    SELECT timestamp, username, action, details, success
                    FROM user_activities 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """)
                
                activities = cursor.fetchall()
                self.activities_table.setRowCount(len(activities))
                
                for row, (timestamp, username, action, details, success) in enumerate(activities):
                    # Format timestamp
                    try:
                        dt = datetime.datetime.fromisoformat(timestamp)
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp.split(' ')[-1] if ' ' in timestamp else timestamp
                    
                    self.activities_table.setItem(row, 0, QtWidgets.QTableWidgetItem(time_str))
                    self.activities_table.setItem(row, 1, QtWidgets.QTableWidgetItem(username or "N/A"))
                    self.activities_table.setItem(row, 2, QtWidgets.QTableWidgetItem(action or "N/A"))
                    self.activities_table.setItem(row, 3, QtWidgets.QTableWidgetItem(details or "N/A"))
                    
                    # Success indicator with color
                    success_item = QtWidgets.QTableWidgetItem("✅" if success else "❌")
                    if not success:
                        success_item.setBackground(QtGui.QColor("#fecaca"))
                    self.activities_table.setItem(row, 4, success_item)
                    
        except Exception as e:
            self.add_log(f"❌ Error loading monitoring data: {str(e)}")
            
    def update_statistics(self):
        """Update statistics based on selected period."""
        period_map = {
            "Last 24 hours": 1,
            "Last 7 days": 7,
            "Last 30 days": 30
        }
        days = period_map.get(self.period_combo.currentText(), 7)
        
        try:
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # Generate statistics report
                cursor.execute(f"""
                    SELECT COUNT(*) FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days')
                """)
                total_activities = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT username) FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days') AND action LIKE '%LOGIN%'
                """)
                unique_users = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT username, COUNT(*) as count FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days')
                    GROUP BY username ORDER BY count DESC LIMIT 10
                """)
                top_users = cursor.fetchall()
                
                # Format report
                report = f"""
=== CRYPTO INSIGHT MONITORING REPORT ===
Period: {self.period_combo.currentText()}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY:
• Total Activities: {total_activities}
• Unique Active Users: {unique_users}
• Average Activities per User: {total_activities/unique_users if unique_users > 0 else 0:.1f}

👥 TOP ACTIVE USERS:
"""
                for i, (username, count) in enumerate(top_users, 1):
                    report += f"{i:2d}. {username}: {count} activities\n"
                
                report += f"""

📈 INSIGHTS:
• Most active period: {self.period_combo.currentText()}
• Monitoring since: Admin dashboard launch
• Real-time tracking: ✅ Active

=== END REPORT ===
"""
                
                self.stats_text.setPlainText(report)
                
        except Exception as e:
            self.stats_text.setPlainText(f"Error generating statistics: {str(e)}")
            
    def generate_detailed_report(self):
        """Generate detailed report in new window."""
        try:
            report_dialog = QtWidgets.QDialog(self)
            report_dialog.setWindowTitle("Detailed Monitoring Report")
            report_dialog.resize(800, 600)
            
            layout = QtWidgets.QVBoxLayout(report_dialog)
            
            # Generate comprehensive report
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # All activities
                cursor.execute("""
                    SELECT timestamp, username, action, details, success
                    FROM user_activities 
                    ORDER BY timestamp DESC
                """)
                all_activities = cursor.fetchall()
                
                # Admin actions
                cursor.execute("""
                    SELECT timestamp, admin_username, action, target_user, details
                    FROM admin_actions 
                    ORDER BY timestamp DESC
                """)
                admin_actions = cursor.fetchall()
            
            report_text = QtWidgets.QTextEdit()
            report_text.setFont(QtGui.QFont("Courier New", 9))
            
            detailed_report = f"""
=== COMPREHENSIVE MONITORING REPORT ===
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Admin: {self.username}

📋 ALL USER ACTIVITIES ({len(all_activities)} total):
"""
            
            for timestamp, username, action, details, success in all_activities[:100]:  # Limit to 100
                status = "✅" if success else "❌"
                detailed_report += f"{timestamp} | {username} | {action} | {details} {status}\n"
            
            detailed_report += f"""

🔧 ADMIN ACTIONS ({len(admin_actions)} total):
"""
            
            for timestamp, admin_user, action, target, details in admin_actions:
                detailed_report += f"{timestamp} | {admin_user} | {action} | Target: {target} | {details}\n"
            
            report_text.setPlainText(detailed_report)
            layout.addWidget(report_text)
            
            # Export button
            export_btn = QtWidgets.QPushButton("💾 Export to File")
            export_btn.clicked.connect(lambda: self.export_report_to_file(detailed_report))
            layout.addWidget(export_btn)
            
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(report_dialog.accept)
            layout.addWidget(close_btn)
            
            report_dialog.exec_()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def export_report_to_file(self, report_content):
        """Export report to text file."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Report", 
            f"crypto_insight_report_{datetime.date.today()}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                QtWidgets.QMessageBox.information(self, "Success", f"Report exported to:\n{filename}")
                self.log_admin_activity("EXPORT_REPORT", f"Exported monitoring report to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}")
                
    def export_monitoring_data(self):
        """Export monitoring data to JSON."""
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Monitoring Data", 
                f"monitoring_data_{datetime.date.today()}.json",
                "JSON Files (*.json)"
            )
            
            if filename:
                with sqlite3.connect(self.monitoring_db) as conn:
                    cursor = conn.cursor()
                    
                    # Get all data
                    cursor.execute("SELECT * FROM user_activities ORDER BY timestamp DESC")
                    activities = cursor.fetchall()
                    
                    cursor.execute("SELECT * FROM admin_actions ORDER BY timestamp DESC")
                    admin_actions = cursor.fetchall()
                
                export_data = {
                    'export_info': {
                        'generated_at': datetime.datetime.now().isoformat(),
                        'admin_user': self.username,
                        'total_activities': len(activities),
                        'total_admin_actions': len(admin_actions)
                    },
                    'user_activities': activities,
                    'admin_actions': admin_actions
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                QtWidgets.QMessageBox.information(self, "Export Complete", f"Data exported to:\n{filename}")
                self.log_admin_activity("EXPORT_DATA", f"Exported monitoring data to JSON: {filename}")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            
    def clear_logs(self):
        """Clear system logs display."""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear the log display?\n(This won't delete database records)",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.log_text.clear()
            self.add_log("🗑️ Log display cleared by admin")
            self.log_admin_activity("CLEAR_LOGS", "Cleared system log display")
            
    # Existing methods with monitoring integration
    def start_auto_refresh(self):
        """Mulai auto-refresh dengan interval yang ditentukan."""
        interval = self.interval_spin.value() * 1000  # Convert to milliseconds
        self.auto_refresh_timer.start(interval)
        self.auto_refresh_enabled = True
        
    def stop_auto_refresh(self):
        """Hentikan auto-refresh."""
        self.auto_refresh_timer.stop()
        self.auto_refresh_enabled = False
        
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        if self.auto_refresh_enabled:
            self.stop_auto_refresh()
            self.auto_refresh_btn.setText("▶️ Resume Auto-Check")
            self.auto_refresh_btn.setStyleSheet("background: #059669; color: white; font-weight: 600; padding: 6px 12px; border-radius: 6px;")
            self.status_label.setText("⏸️ Auto-monitoring dijeda")
            self.status_label.setStyleSheet("color: #dc2626; font-weight: 600; padding: 8px; background: #fef2f2; border-radius: 6px; margin: 4px 0;")
            self.add_log("⏸️ Auto-monitoring dijeda oleh admin")
            self.log_admin_activity("PAUSE_MONITORING", "Paused auto-refresh monitoring")
        else:
            self.start_auto_refresh()
            self.auto_refresh_btn.setText("⏸️ Pause Auto-Check")
            self.auto_refresh_btn.setStyleSheet("background: #f59e0b; color: white; font-weight: 600; padding: 6px 12px; border-radius: 6px;")
            self.status_label.setText("🟢 Auto-monitoring aktif - Menunggu user baru...")
            self.status_label.setStyleSheet("color: #059669; font-weight: 600; padding: 8px; background: #ecfdf5; border-radius: 6px; margin: 4px 0;")
            self.add_log("▶️ Auto-monitoring dilanjutkan")
            self.log_admin_activity("RESUME_MONITORING", "Resumed auto-refresh monitoring")
            
    def update_refresh_interval(self):
        """Update interval auto-refresh."""
        if self.auto_refresh_enabled:
            self.stop_auto_refresh()
            self.start_auto_refresh()
            interval = self.interval_spin.value()
            self.add_log(f"⚙️ Interval auto-check diubah menjadi {interval} detik")
            self.log_admin_activity("CHANGE_INTERVAL", f"Changed refresh interval to {interval} seconds")
            
    def auto_check_new_users(self):
        """Cek otomatis apakah ada user baru."""
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            current_count = cur.fetchone()[0]
            conn.close()
            
            if self.last_user_count == 0:
                # First time initialization
                self.last_user_count = current_count
                return
                
            if current_count > self.last_user_count:
                # Ada user baru!
                new_users = current_count - self.last_user_count
                self.add_log(f"🚨 ALERT: {new_users} user baru terdeteksi!")
                self.status_label.setText(f"🔔 {new_users} user baru terdeteksi! Memuat ulang data...")
                self.status_label.setStyleSheet("color: #dc2626; font-weight: 600; padding: 8px; background: #fef2f2; border-radius: 6px; margin: 4px 0;")
                
                # Log new user detection
                self.log_admin_activity("NEW_USER_DETECTED", f"{new_users} new users detected")
                
                # Refresh table
                self.load_users()
                self.load_monitoring_data()  # Refresh monitoring data too
                self.last_user_count = current_count
                
                # Show notification
                QtWidgets.QMessageBox.information(
                    self, 
                    "User Baru Terdeteksi!", 
                    f"🎉 {new_users} user baru telah mendaftar!\n\nTabel telah diperbarui secara otomatis."
                )
                
                # Reset status after 3 seconds
                QtCore.QTimer.singleShot(3000, self.reset_status_message)
                
        except Exception as e:
            self.add_log(f"❌ Error saat auto-check: {str(e)}")
            
    def reset_status_message(self):
        """Reset status message ke normal."""
        if self.auto_refresh_enabled:
            self.status_label.setText("🟢 Auto-monitoring aktif - Menunggu user baru...")
            self.status_label.setStyleSheet("color: #059669; font-weight: 600; padding: 8px; background: #ecfdf5; border-radius: 6px; margin: 4px 0;")
            
    def manual_refresh(self):
        """Refresh manual oleh admin."""
        self.add_log("🔄 Refresh manual oleh admin")
        self.log_admin_activity("MANUAL_REFRESH", "Performed manual refresh of user data")
        self.load_users()
        self.load_monitoring_data()
        
    def load_users(self):
        """Ambil semua user dari database dan tampilkan di tabel."""
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute("SELECT id, username, role FROM users ORDER BY id DESC")  # DESC untuk user terbaru di atas
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", str(e))
            self.add_log(f"❌ DB Error: {str(e)}")
            return

        self.table.setRowCount(0)
        for r, (uid, uname, role) in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(uid)))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(uname))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(role))
            
            # Status column - highlight user baru (ID tinggi)
            if uid > self.last_user_count - len(rows) + 5:  # Rough estimation for "new"
                status_item = QtWidgets.QTableWidgetItem("🆕 Baru")
                status_item.setBackground(QtCore.Qt.yellow)
            else:
                status_item = QtWidgets.QTableWidgetItem("✅ Lama")
            
            self.table.setItem(r, 3, status_item)
            
            # Last login info (placeholder - could be enhanced with actual login tracking)
            last_login_item = QtWidgets.QTableWidgetItem("N/A")
            self.table.setItem(r, 4, last_login_item)
            
        self.table.resizeColumnsToContents()
        
        # Update last user count
        if rows:
            self.last_user_count = len(rows)
            
        # Log user view action
        self.log_admin_activity("VIEW_USERS", f"Viewed user list - {len(rows)} users total")
        
    def copy_selected_rows(self):
        """Salin baris terpilih (ID, Username, Role) ke clipboard."""
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QtWidgets.QMessageBox.information(self, "Info", "Pilih minimal satu baris.")
            return
        lines = []
        for idx in sel:
            rid = self.table.item(idx.row(), 0).text()
            uname = self.table.item(idx.row(), 1).text()
            role = self.table.item(idx.row(), 2).text()
            status = self.table.item(idx.row(), 3).text()
            lines.append(f"{rid}\t{uname}\t{role}\t{status}")
        QtWidgets.QApplication.clipboard().setText("\n".join(lines))
        QtWidgets.QMessageBox.information(self, "Disalin", "Data user sudah disalin ke clipboard.")
        self.add_log(f"📋 Data {len(sel)} user disalin ke clipboard")
        
        # Log copy action
        copied_users = [self.table.item(idx.row(), 1).text() for idx in sel]
        self.log_admin_activity("COPY_USER_DATA", f"Copied data for users: {', '.join(copied_users)}")
        
    def add_log(self, message):
        """Tambahkan pesan ke log aktivitas."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def closeEvent(self, event):
        """Override close event untuk stop timer dan log logout."""
        self.stop_auto_refresh()
        self.add_log("🔴 Enhanced Admin dashboard ditutup")
        self.log_admin_activity("ADMIN_LOGOUT", f"Admin {self.username} logged out from dashboard")
        event.accept()