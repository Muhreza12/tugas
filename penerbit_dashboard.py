# penerbit_dashboard.py — Modern & Beautiful Penerbit Dashboard
"""
Enhanced Penerbit (Publisher) Dashboard dengan:
- Modern card-based layout
- Rich statistics display
- Better news management interface
- Smooth animations
- Beautiful dark theme
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from typing import Optional
from app_db_fixed import (
    heartbeat, end_session, 
    create_news, list_my_news, list_published_news
)

class StatCard(QtWidgets.QFrame):
    """Modern statistics card widget"""
    
    def __init__(self, title, value, icon, color, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setFixedHeight(120)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Header dengan icon
        header = QtWidgets.QHBoxLayout()
        
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setStyleSheet(f"color: {color}; font-size: 28px;")
        
        header.addWidget(icon_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Value
        self.value_label = QtWidgets.QLabel(str(value))
        self.value_label.setObjectName("statValue")
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("statTitle")
        layout.addWidget(title_label)
        
    def update_value(self, value):
        """Update card value"""
        self.value_label.setText(str(value))


class ModernTextEditor(QtWidgets.QWidget):
    """Modern text editor with formatting toolbar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QtWidgets.QFrame()
        toolbar.setObjectName("editorToolbar")
        toolbar.setFixedHeight(48)
        
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)
        
        # Format buttons
        self.btn_bold = self._create_tool_button("B", "Bold (Ctrl+B)")
        self.btn_italic = self._create_tool_button("I", "Italic (Ctrl+I)")
        self.btn_underline = self._create_tool_button("U", "Underline (Ctrl+U)")
        
        toolbar_layout.addWidget(self.btn_bold)
        toolbar_layout.addWidget(self.btn_italic)
        toolbar_layout.addWidget(self.btn_underline)
        toolbar_layout.addWidget(self._create_separator())
        
        # Heading buttons
        self.btn_h1 = self._create_tool_button("H1", "Heading 1")
        self.btn_h2 = self._create_tool_button("H2", "Heading 2")
        
        toolbar_layout.addWidget(self.btn_h1)
        toolbar_layout.addWidget(self.btn_h2)
        toolbar_layout.addWidget(self._create_separator())
        
        # List buttons
        self.btn_bullet = self._create_tool_button("•", "Bullet List")
        self.btn_number = self._create_tool_button("1.", "Numbered List")
        
        toolbar_layout.addWidget(self.btn_bullet)
        toolbar_layout.addWidget(self.btn_number)
        
        toolbar_layout.addStretch()
        
        # Word count
        self.word_count = QtWidgets.QLabel("0 words")
        self.word_count.setObjectName("wordCount")
        toolbar_layout.addWidget(self.word_count)
        
        layout.addWidget(toolbar)
        
        # Text editor
        self.editor = QtWidgets.QTextEdit()
        self.editor.setObjectName("contentEditor")
        self.editor.setPlaceholderText("Write your article here...\n\nStart typing to create engaging content for your readers.")
        layout.addWidget(self.editor)
        
        # Connect signals
        self.btn_bold.clicked.connect(self._toggle_bold)
        self.btn_italic.clicked.connect(self._toggle_italic)
        self.btn_underline.clicked.connect(self._toggle_underline)
        self.btn_h1.clicked.connect(lambda: self._insert_heading(1))
        self.btn_h2.clicked.connect(lambda: self._insert_heading(2))
        self.btn_bullet.clicked.connect(self._insert_bullet_list)
        self.btn_number.clicked.connect(self._insert_numbered_list)
        
        self.editor.textChanged.connect(self._update_word_count)
        
    def _create_tool_button(self, text, tooltip):
        """Create toolbar button"""
        btn = QtWidgets.QPushButton(text)
        btn.setObjectName("toolButton")
        btn.setFixedSize(36, 32)
        btn.setToolTip(tooltip)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        return btn
    
    def _create_separator(self):
        """Create toolbar separator"""
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setObjectName("toolbarSeparator")
        return sep
    
    def _toggle_bold(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontWeight(QtGui.QFont.Normal if fmt.fontWeight() == QtGui.QFont.Bold else QtGui.QFont.Bold)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()
    
    def _toggle_italic(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()
    
    def _toggle_underline(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()
    
    def _insert_heading(self, level):
        cursor = self.editor.textCursor()
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        
        block_fmt = QtGui.QTextBlockFormat()
        char_fmt = QtGui.QTextCharFormat()
        
        if level == 1:
            char_fmt.setFontPointSize(24)
            char_fmt.setFontWeight(QtGui.QFont.Bold)
        elif level == 2:
            char_fmt.setFontPointSize(18)
            char_fmt.setFontWeight(QtGui.QFont.Bold)
        
        cursor.setBlockFormat(block_fmt)
        cursor.mergeCharFormat(char_fmt)
        self.editor.setFocus()
    
    def _insert_bullet_list(self):
        cursor = self.editor.textCursor()
        list_fmt = QtGui.QTextListFormat()
        list_fmt.setStyle(QtGui.QTextListFormat.ListDisc)
        cursor.createList(list_fmt)
        self.editor.setFocus()
    
    def _insert_numbered_list(self):
        cursor = self.editor.textCursor()
        list_fmt = QtGui.QTextListFormat()
        list_fmt.setStyle(QtGui.QTextListFormat.ListDecimal)
        cursor.createList(list_fmt)
        self.editor.setFocus()
    
    def _update_word_count(self):
        text = self.editor.toPlainText()
        words = len([w for w in text.split() if w])
        self.word_count.setText(f"{words} words")
    
    def get_html(self):
        """Get HTML content"""
        return self.editor.toHtml()
    
    def get_plain_text(self):
        """Get plain text content"""
        return self.editor.toPlainText()
    
    def set_text(self, text):
        """Set text content"""
        self.editor.setPlainText(text)
    
    def clear(self):
        """Clear editor"""
        self.editor.clear()


class PenerbitDashboard(QtWidgets.QMainWindow):
    """Modern Penerbit Dashboard"""
    
    def __init__(self, username: str, session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle(f"Crypto Insight • Penerbit Dashboard")
        self.resize(1400, 900)
        
        self._setup_ui()
        self._apply_style()
        self._load_statistics()
        self._load_my_articles()
        
        # Heartbeat timer
        if self.session_id:
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(self.session_id))
            self.hb_timer.start(20000)
        
        # Auto-refresh timer
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._load_statistics)
        self.refresh_timer.start(30000)  # Every 30 seconds
    
    def _setup_ui(self):
        """Setup UI components"""
        
        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Statistics cards
        stats_row = self._create_statistics_row()
        main_layout.addLayout(stats_row)
        
        # Tab widget for content
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("mainTabs")
        
        # Tab 1: Create Article
        self.tab_create = self._create_article_tab()
        self.tabs.addTab(self.tab_create, "✍️  Create Article")
        
        # Tab 2: My Articles
        self.tab_articles = self._create_articles_tab()
        self.tabs.addTab(self.tab_articles, "📚  My Articles")
        
        # Tab 3: Published Feed
        self.tab_feed = self._create_feed_tab()
        self.tabs.addTab(self.tab_feed, "🌐  Published Feed")
        
        main_layout.addWidget(self.tabs)
        
    def _create_header(self):
        """Create header with title and logout"""
        header = QtWidgets.QFrame()
        header.setObjectName("header")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title section
        title_layout = QtWidgets.QVBoxLayout()
        
        title = QtWidgets.QLabel(f"Welcome, {self.username} 👋")
        title.setObjectName("headerTitle")
        
        subtitle = QtWidgets.QLabel("Penerbit Dashboard • Create and manage your articles")
        subtitle.setObjectName("headerSubtitle")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Logout button
        self.btn_logout = QtWidgets.QPushButton("Logout")
        self.btn_logout.setObjectName("logoutBtn")
        self.btn_logout.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self._logout)
        
        layout.addWidget(self.btn_logout)
        
        return header
    
    def _create_statistics_row(self):
        """Create statistics cards row"""
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        
        # Create stat cards
        self.card_total = StatCard("Total Articles", "0", "📝", "#7c5cff")
        self.card_published = StatCard("Published", "0", "✅", "#10b981")
        self.card_draft = StatCard("Drafts", "0", "📄", "#f59e0b")
        self.card_views = StatCard("Total Views", "N/A", "👁️", "#3b82f6")
        
        row.addWidget(self.card_total)
        row.addWidget(self.card_published)
        row.addWidget(self.card_draft)
        row.addWidget(self.card_views)
        
        return row
    
    def _create_article_tab(self):
        """Create article creation tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Form container
        form_container = QtWidgets.QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QtWidgets.QVBoxLayout(form_container)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)
        
        # Title input
        title_label = QtWidgets.QLabel("Article Title")
        title_label.setObjectName("formLabel")
        
        self.input_title = QtWidgets.QLineEdit()
        self.input_title.setObjectName("titleInput")
        self.input_title.setPlaceholderText("Enter your article title...")
        self.input_title.setMinimumHeight(48)
        
        form_layout.addWidget(title_label)
        form_layout.addWidget(self.input_title)
        
        # Content editor
        content_label = QtWidgets.QLabel("Article Content")
        content_label.setObjectName("formLabel")
        
        self.editor = ModernTextEditor()
        
        form_layout.addWidget(content_label)
        form_layout.addWidget(self.editor, 1)
        
        # Action buttons
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(12)
        
        self.btn_save_draft = QtWidgets.QPushButton("💾 Save as Draft")
        self.btn_save_draft.setObjectName("secondaryBtn")
        self.btn_save_draft.setMinimumHeight(44)
        self.btn_save_draft.clicked.connect(lambda: self._save_article(publish=False))
        
        self.btn_publish = QtWidgets.QPushButton("🚀 Publish Article")
        self.btn_publish.setObjectName("primaryBtn")
        self.btn_publish.setMinimumHeight(44)
        self.btn_publish.clicked.connect(lambda: self._save_article(publish=True))
        
        self.btn_clear = QtWidgets.QPushButton("🗑️ Clear")
        self.btn_clear.setObjectName("dangerBtn")
        self.btn_clear.setMinimumHeight(44)
        self.btn_clear.clicked.connect(self._clear_form)
        
        action_row.addWidget(self.btn_save_draft, 1)
        action_row.addWidget(self.btn_publish, 2)
        action_row.addWidget(self.btn_clear, 1)
        
        form_layout.addLayout(action_row)
        
        layout.addWidget(form_container)
        
        return widget
    
    def _create_articles_tab(self):
        """Create my articles management tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("toolbarBtn")
        refresh_btn.clicked.connect(self._load_my_articles)
        
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        
        search_input = QtWidgets.QLineEdit()
        search_input.setObjectName("searchInput")
        search_input.setPlaceholderText("🔍 Search articles...")
        search_input.setFixedWidth(300)
        
        toolbar.addWidget(search_input)
        
        layout.addLayout(toolbar)
        
        # Articles table
        self.table_articles = QtWidgets.QTableWidget(0, 5)
        self.table_articles.setObjectName("articlesTable")
        self.table_articles.setHorizontalHeaderLabels([
            "ID", "Title", "Status", "Created", "Actions"
        ])
        
        header = self.table_articles.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.table_articles.setColumnWidth(4, 150)
        
        self.table_articles.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_articles.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_articles.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_articles)
        
        return widget
    
    def _create_feed_tab(self):
        """Create published feed tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Info label
        info = QtWidgets.QLabel("📰 All Published Articles from All Publishers")
        info.setObjectName("infoLabel")
        layout.addWidget(info)
        
        # Feed table
        self.table_feed = QtWidgets.QTableWidget(0, 4)
        self.table_feed.setObjectName("feedTable")
        self.table_feed.setHorizontalHeaderLabels([
            "ID", "Title", "Author", "Published"
        ])
        
        header = self.table_feed.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        
        self.table_feed.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_feed.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_feed.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_feed)
        
        # Auto-refresh button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh Feed")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.clicked.connect(self._load_feed)
        layout.addWidget(refresh_btn)
        
        return widget
    
    def _save_article(self, publish=True):
        """Save article as draft or publish"""
        title = self.input_title.text().strip()
        content = self.editor.get_plain_text().strip()
        
        if not title:
            QtWidgets.QMessageBox.warning(
                self, "Missing Title",
                "Please enter an article title."
            )
            self.input_title.setFocus()
            return
        
        if not content:
            QtWidgets.QMessageBox.warning(
                self, "Missing Content",
                "Please write some content for your article."
            )
            self.editor.editor.setFocus()
            return
        
        # Save to database
        success = create_news(self.username, title, content, publish=publish)
        
        if success:
            status = "published" if publish else "saved as draft"
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Article '{title}' has been {status}!"
            )
            
            self._clear_form()
            self._load_statistics()
            self._load_my_articles()
            
            if publish:
                self._load_feed()
        else:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                "Failed to save article. Please check database connection."
            )
    
    def _clear_form(self):
        """Clear article form"""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear Form",
            "Are you sure you want to clear the form?\nAll unsaved changes will be lost.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.input_title.clear()
            self.editor.clear()
            self.input_title.setFocus()
    
    def _load_statistics(self):
        """Load and update statistics"""
        articles = list_my_news(self.username, limit=1000)
        
        total = len(articles)
        published = len([a for a in articles if a[2] == 'published'])
        draft = len([a for a in articles if a[2] == 'draft'])
        
        self.card_total.update_value(total)
        self.card_published.update_value(published)
        self.card_draft.update_value(draft)
    
    def _load_my_articles(self):
        """Load my articles into table"""
        articles = list_my_news(self.username, limit=100)
        
        self.table_articles.setRowCount(len(articles))
        
        for row, (aid, title, status, created) in enumerate(articles):
            # ID
            id_item = QtWidgets.QTableWidgetItem(str(aid))
            self.table_articles.setItem(row, 0, id_item)
            
            # Title
            title_item = QtWidgets.QTableWidgetItem(title)
            self.table_articles.setItem(row, 1, title_item)
            
            # Status with badge
            status_widget = QtWidgets.QWidget()
            status_layout = QtWidgets.QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 4, 8, 4)
            
            status_label = QtWidgets.QLabel(status.upper())
            status_label.setObjectName("statusBadge")
            
            if status == 'published':
                status_label.setStyleSheet("""
                    background: #10b981; color: white;
                    padding: 4px 12px; border-radius: 12px;
                    font-size: 11px; font-weight: 600;
                """)
            else:
                status_label.setStyleSheet("""
                    background: #6b7280; color: white;
                    padding: 4px 12px; border-radius: 12px;
                    font-size: 11px; font-weight: 600;
                """)
            
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            
            self.table_articles.setCellWidget(row, 2, status_widget)
            
            # Created
            created_item = QtWidgets.QTableWidgetItem(created or "N/A")
            self.table_articles.setItem(row, 3, created_item)
            
            # Actions
            actions_widget = QtWidgets.QWidget()
            actions_layout = QtWidgets.QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            btn_view = QtWidgets.QPushButton("👁️")
            btn_view.setToolTip("View article")
            btn_view.setFixedSize(32, 32)
            btn_view.setObjectName("actionBtn")
            
            btn_edit = QtWidgets.QPushButton("✏️")
            btn_edit.setToolTip("Edit article")
            btn_edit.setFixedSize(32, 32)
            btn_edit.setObjectName("actionBtn")
            
            btn_delete = QtWidgets.QPushButton("🗑️")
            btn_delete.setToolTip("Delete article")
            btn_delete.setFixedSize(32, 32)
            btn_delete.setObjectName("actionBtnDanger")
            
            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            actions_layout.addStretch()
            
            self.table_articles.setCellWidget(row, 4, actions_widget)
    
    def _load_feed(self):
        """Load published feed"""
        articles = list_published_news(limit=100)
        
        self.table_feed.setRowCount(len(articles))
        
        for row, (aid, title, author, published) in enumerate(articles):
            self.table_feed.setItem(row, 0, QtWidgets.QTableWidgetItem(str(aid)))
            self.table_feed.setItem(row, 1, QtWidgets.QTableWidgetItem(title))
            self.table_feed.setItem(row, 2, QtWidgets.QTableWidgetItem(author))
            self.table_feed.setItem(row, 3, QtWidgets.QTableWidgetItem(published or "N/A"))
    
    def _logout(self):
        """Logout and close dashboard"""
        if self.hb_timer and self.hb_timer.isActive():
            self.hb_timer.stop()
        
        if self.session_id:
            try:
                end_session(self.session_id)
            except:
                pass
        
        self.close()
    
    def _apply_style(self):
        """Apply beautiful dark theme"""
        self.setStyleSheet("""
            /* Global */
            QMainWindow, QWidget {
                background: #0a0b0e;
                color: #e5e7eb;
            }
            
            /* Header */
            #header {
                background: transparent;
            }
            #headerTitle {
                font-size: 28px;
                font-weight: 700;
                color: #f9fafb;
            }
            #headerSubtitle {
                font-size: 14px;
                color: #9ca3af;
                margin-top: 4px;
            }
            
            /* Stat Cards */
            #statCard {
                background: #15161d;
                border: 1px solid #25262f;
                border-radius: 16px;
            }
            #statIcon {
                font-size: 28px;
            }
            #statValue {
                font-size: 32px;
                font-weight: 700;
                color: #f9fafb;
            }
            #statTitle {
                font-size: 13px;
                color: #9ca3af;
                font-weight: 500;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #25262f;
                border-radius: 12px;
                background: #15161d;
                top: -1px;
            }
            QTabBar::tab {
                background: transparent;
                color: #9ca3af;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #15161d;
                color: #7c5cff;
                border-bottom: 2px solid #7c5cff;
            }
            QTabBar::tab:hover:!selected {
                background: #1a1b26;
                color: #d1d5db;
            }
            
            /* Form Container */
            #formContainer {
                background: #15161d;
                border: 1px solid #25262f;
                border-radius: 12px;
            }
            #formLabel {
                font-size: 14px;
                font-weight: 600;
                color: #f9fafb;
                margin-bottom: 8px;
            }
            
            /* Inputs */
            #titleInput {
                background: #0e0f12;
                color: #e5e7eb;
                border: 1px solid #25262f;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 16px;
            }
            #titleInput:focus {
                border: 2px solid #7c5cff;
                background: #1a1b26;
            }
            
            /* Text Editor */
            #editorToolbar {
                background: #0e0f12;
                border: 1px solid #25262f;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            #toolButton {
                background: transparent;
                color: #9ca3af;
                border: 1px solid #25262f;
                border-radius: 6px;
                font-weight: 600;
            }
            #toolButton:hover {
                background: #25262f;
                color: #e5e7eb;
            }
            #toolButton:pressed {
                background: #7c5cff;
                color: white;
            }
            #toolbarSeparator {
                background: #25262f;
                max-width: 1px;
            }
            #wordCount {
                color: #6b7280;
                font-size: 12px;
            }
            
            #contentEditor {
                background: #0e0f12;
                color: #e5e7eb;
                border: 1px solid #25262f;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.6;
            }
            
            /* Buttons */
            #primaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c5cff, stop:1 #6a4cf7);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                padding: 12px 24px;
            }
            #primaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b6cff, stop:1 #7a5cf7);
            }
            #primaryBtn:pressed {
                background: #5840e6;
            }
            
            #secondaryBtn {
                background: transparent;
                color: #7c5cff;
                border: 2px solid #7c5cff;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                padding: 12px 24px;
            }
            #secondaryBtn:hover {
                background: #7c5cff;
                color: white;
            }
            
            #dangerBtn {
                background: transparent;
                color: #ef4444;
                border: 2px solid #ef4444;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                padding: 12px 24px;
            }
            #dangerBtn:hover {
                background: #ef4444;
                color: white;
            }
            
            #logoutBtn {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
            }
            #logoutBtn:hover {
                background: #dc2626;
            }
            
            #toolbarBtn {
                background: #15161d;
                color: #e5e7eb;
                border: 1px solid #25262f;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }
            #toolbarBtn:hover {
                background: #25262f;
            }
            
            #actionBtn {
                background: transparent;
                border: 1px solid #25262f;
                border-radius: 6px;
            }
            #actionBtn:hover {
                background: #25262f;
            }
            
            #actionBtnDanger {
                background: transparent;
                border: 1px solid #ef4444;
                border-radius: 6px;
            }
            #actionBtnDanger:hover {
                background: #ef4444;
            }
            
            /* Search Input */
            #searchInput {
                background: #15161d;
                color: #e5e7eb;
                border: 1px solid #25262f;
                border-radius: 10px;
                padding: 8px 16px;
            }
            #searchInput:focus {
                border: 1px solid #7c5cff;
            }
            
            /* Tables */
            QTableWidget {
                background: #15161d;
                color: #e5e7eb;
                border: 1px solid #25262f;
                border-radius: 12px;
                gridline-color: #25262f;
                selection-background-color: #1f2937;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #0e0f12;
                color: #9ca3af;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #25262f;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
            }
            QTableWidget::item:alternate {
                background: #1a1b26;
            }
            
            /* Info Label */
            #infoLabel {
                font-size: 14px;
                color: #9ca3af;
                padding: 12px 16px;
                background: #15161d;
                border: 1px solid #25262f;
                border-radius: 8px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #25262f;
                min-height: 24px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #374151;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            
            QScrollBar:horizontal {
                background: transparent;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #25262f;
                min-width: 24px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #374151;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)
        
        # Set font
        font = QtGui.QFont("Segoe UI", 10)
        self.setFont(font)
    
    def closeEvent(self, event):
        """Handle close event"""
        self._logout()
        event.accept()


# For testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = PenerbitDashboard("test_penerbit", None)
    window.show()
    sys.exit(app.exec_())
