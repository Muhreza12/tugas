# interaction_widgets.py — UI Components untuk User Interactions
"""
Complete UI widgets untuk Phase 1 features:
- ArticleInteractionBar (Like, Bookmark, Share buttons)
- ArticleCard (Card dengan preview + interaction)
- StatsDisplay (Display statistics)

Author: Claude + Reza
Version: 1.0 - Phase 1 Complete
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Optional
from app_db_interactions import (
    like_article, unlike_article, is_article_liked,
    bookmark_article, unbookmark_article, is_article_bookmarked,
    track_article_view, get_article_stats
)


class ArticleInteractionBar(QtWidgets.QWidget):
    """
    Widget dengan Like, Bookmark, dan Share buttons
    """
    
    # Signals
    liked_changed = QtCore.pyqtSignal(bool)  # Emits True when liked, False when unliked
    bookmarked_changed = QtCore.pyqtSignal(bool)
    share_clicked = QtCore.pyqtSignal()
    
    def __init__(self, article_id: int, username: str, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.username = username
        
        self._setup_ui()
        self._load_states()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Like button
        self.btn_like = QtWidgets.QPushButton()
        self.btn_like.setObjectName("likeBtn")
        self.btn_like.setFixedHeight(40)
        self.btn_like.setMinimumWidth(90)
        self.btn_like.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_like.clicked.connect(self._toggle_like)
        
        # Bookmark button
        self.btn_bookmark = QtWidgets.QPushButton()
        self.btn_bookmark.setObjectName("bookmarkBtn")
        self.btn_bookmark.setFixedHeight(40)
        self.btn_bookmark.setMinimumWidth(110)
        self.btn_bookmark.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_bookmark.clicked.connect(self._toggle_bookmark)
        
        # Share button
        self.btn_share = QtWidgets.QPushButton("📤 Share")
        self.btn_share.setObjectName("shareBtn")
        self.btn_share.setFixedHeight(40)
        self.btn_share.setMinimumWidth(90)
        self.btn_share.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_share.clicked.connect(lambda: self.share_clicked.emit())
        
        # Views label
        self.label_views = QtWidgets.QLabel()
        self.label_views.setObjectName("viewsLabel")
        
        layout.addWidget(self.btn_like)
        layout.addWidget(self.btn_bookmark)
        layout.addWidget(self.btn_share)
        layout.addStretch()
        layout.addWidget(self.label_views)
        
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply button styles"""
        self.setStyleSheet("""
            #likeBtn, #bookmarkBtn, #shareBtn {
                background: transparent;
                color: #9ca3af;
                border: 1px solid #25262f;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 16px;
            }
            #likeBtn:hover, #bookmarkBtn:hover, #shareBtn:hover {
                background: #15161d;
                color: #e5e7eb;
                border-color: #374151;
            }
            #viewsLabel {
                color: #6b7280;
                font-size: 13px;
                font-weight: 500;
            }
        """)
    
    def _load_states(self):
        """Load current states from database"""
        # Check if liked
        self.is_liked = is_article_liked(self.article_id, self.username)
        self._update_like_button()
        
        # Check if bookmarked
        self.is_bookmarked = is_article_bookmarked(self.article_id, self.username)
        self._update_bookmark_button()
        
        # Get stats
        self._refresh_stats()
        
        # Track view
        track_article_view(self.article_id, self.username)
    
    def _toggle_like(self):
        """Toggle like status"""
        if self.is_liked:
            success = unlike_article(self.article_id, self.username)
            if success:
                self.is_liked = False
                self.liked_changed.emit(False)
        else:
            success = like_article(self.article_id, self.username)
            if success:
                self.is_liked = True
                self.liked_changed.emit(True)
        
        if success:
            self._update_like_button()
            self._refresh_stats()
    
    def _update_like_button(self):
        """Update like button appearance"""
        stats = get_article_stats(self.article_id)
        
        if self.is_liked:
            self.btn_like.setText(f"❤️ {stats['likes']}")
            self.btn_like.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ef4444, stop:1 #dc2626);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #dc2626, stop:1 #b91c1c);
                }
            """)
        else:
            self.btn_like.setText(f"🤍 {stats['likes']}")
            self.btn_like.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #9ca3af;
                    border: 1px solid #25262f;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 13px;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background: #15161d;
                    color: #e5e7eb;
                    border-color: #374151;
                }
            """)
    
    def _toggle_bookmark(self):
        """Toggle bookmark status"""
        if self.is_bookmarked:
            success = unbookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = False
                self.bookmarked_changed.emit(False)
        else:
            success = bookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = True
                self.bookmarked_changed.emit(True)
        
        if success:
            self._update_bookmark_button()
            self._refresh_stats()
    
    def _update_bookmark_button(self):
        """Update bookmark button appearance"""
        stats = get_article_stats(self.article_id)
        
        if self.is_bookmarked:
            self.btn_bookmark.setText(f"🔖 Saved ({stats['bookmarks']})")
            self.btn_bookmark.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #7c5cff, stop:1 #6a4cf7);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 13px;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #6a4cf7, stop:1 #5840e6);
                }
            """)
        else:
            self.btn_bookmark.setText(f"🔖 Save ({stats['bookmarks']})")
            self.btn_bookmark.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #9ca3af;
                    border: 1px solid #25262f;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 13px;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background: #15161d;
                    color: #e5e7eb;
                    border-color: #374151;
                }
            """)
    
    def _refresh_stats(self):
        """Refresh statistics display"""
        stats = get_article_stats(self.article_id)
        self.label_views.setText(f"👁️ {stats['views']:,} views")
    
    def refresh(self):
        """Public method to refresh all states"""
        self._load_states()


class ArticleCard(QtWidgets.QFrame):
    """
    Modern article card dengan preview dan interaction buttons
    """
    
    # Signals
    clicked = QtCore.pyqtSignal(int)  # Emits article_id when clicked
    
    def __init__(self, article_id: int, title: str, author: str, 
                 username: str, preview: str = "", parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.title = title
        self.author = author
        self.username = username
        self.preview = preview[:150] + "..." if len(preview) > 150 else preview
        
        self.setObjectName("articleCard")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Title
        title_label = QtWidgets.QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Author
        author_label = QtWidgets.QLabel(f"by {self.author}")
        author_label.setObjectName("cardAuthor")
        layout.addWidget(author_label)
        
        # Preview
        if self.preview:
            preview_label = QtWidgets.QLabel(self.preview)
            preview_label.setObjectName("cardPreview")
            preview_label.setWordWrap(True)
            layout.addWidget(preview_label)
        
        layout.addSpacing(8)
        
        # Interaction bar
        self.interaction_bar = ArticleInteractionBar(
            self.article_id,
            self.username
        )
        layout.addWidget(self.interaction_bar)
    
    def _apply_styles(self):
        """Apply card styles"""
        self.setStyleSheet("""
            #articleCard {
                background: #15161d;
                border: 1px solid #25262f;
                border-radius: 12px;
            }
            #articleCard:hover {
                background: #1a1b26;
                border-color: #374151;
            }
            #cardTitle {
                color: #f9fafb;
                font-size: 16px;
                font-weight: 700;
            }
            #cardAuthor {
                color: #7c5cff;
                font-size: 12px;
                font-weight: 600;
            }
            #cardPreview {
                color: #9ca3af;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.article_id)
        super().mousePressEvent(event)


class StatsDisplay(QtWidgets.QWidget):
    """
    Widget untuk menampilkan statistics (views, likes, bookmarks)
    """
    
    def __init__(self, views: int = 0, likes: int = 0, bookmarks: int = 0, parent=None):
        super().__init__(parent)
        self.views = views
        self.likes = likes
        self.bookmarks = bookmarks
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Views
        self.label_views = self._create_stat_item("👁️", self.views, "Views")
        layout.addWidget(self.label_views)
        
        # Likes
        self.label_likes = self._create_stat_item("❤️", self.likes, "Likes")
        layout.addWidget(self.label_likes)
        
        # Bookmarks
        self.label_bookmarks = self._create_stat_item("🔖", self.bookmarks, "Saved")
        layout.addWidget(self.label_bookmarks)
        
        layout.addStretch()
    
    def _create_stat_item(self, icon: str, value: int, label: str) -> QtWidgets.QWidget:
        """Create a stat item widget"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setObjectName("statIcon")
        layout.addWidget(icon_label)
        
        # Value and label
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QtWidgets.QLabel(f"{value:,}")
        value_label.setObjectName("statValue")
        text_layout.addWidget(value_label)
        
        label_widget = QtWidgets.QLabel(label)
        label_widget.setObjectName("statLabel")
        text_layout.addWidget(label_widget)
        
        layout.addLayout(text_layout)
        
        return container
    
    def _apply_styles(self):
        """Apply styles"""
        self.setStyleSheet("""
            #statIcon {
                font-size: 24px;
            }
            #statValue {
                color: #f9fafb;
                font-size: 18px;
                font-weight: 700;
            }
            #statLabel {
                color: #6b7280;
                font-size: 11px;
                font-weight: 500;
                text-transform: uppercase;
            }
        """)
    
    def update_stats(self, views: int, likes: int, bookmarks: int):
        """Update statistics"""
        self.views = views
        self.likes = likes
        self.bookmarks = bookmarks
        # Recreate UI
        self._clear_layout()
        self._setup_ui()
    
    def _clear_layout(self):
        """Clear all widgets from layout"""
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ============================================
# DEMO
# ============================================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Demo window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Interaction Widgets Demo")
    window.resize(700, 400)
    window.setStyleSheet("background: #0a0b0e;")
    
    layout = QtWidgets.QVBoxLayout(window)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(20)
    
    # Title
    title = QtWidgets.QLabel("Interaction Widgets Demo")
    title.setStyleSheet("color: #f9fafb; font-size: 20px; font-weight: 700;")
    layout.addWidget(title)
    
    # Demo 1: Article Card
    demo1_label = QtWidgets.QLabel("1. Article Card:")
    demo1_label.setStyleSheet("color: #9ca3af; font-size: 14px; font-weight: 600;")
    layout.addWidget(demo1_label)
    
    card = ArticleCard(
        article_id=1,
        title="The Future of Cryptocurrency in 2025",
        author="John Doe",
        username="testuser",
        preview="Bitcoin and Ethereum are showing strong bullish signals as institutional adoption continues to grow. Experts predict significant price movements in Q1 2025..."
    )
    card.clicked.connect(lambda aid: print(f"Article {aid} clicked!"))
    layout.addWidget(card)
    
    # Demo 2: Interaction Bar
    demo2_label = QtWidgets.QLabel("2. Interaction Bar:")
    demo2_label.setStyleSheet("color: #9ca3af; font-size: 14px; font-weight: 600;")
    layout.addWidget(demo2_label)
    
    interaction_bar = ArticleInteractionBar(
        article_id=1,
        username="testuser"
    )
    interaction_bar.liked_changed.connect(
        lambda liked: print(f"Liked: {liked}")
    )
    interaction_bar.bookmarked_changed.connect(
        lambda bookmarked: print(f"Bookmarked: {bookmarked}")
    )
    layout.addWidget(interaction_bar)
    
    # Demo 3: Stats Display
    demo3_label = QtWidgets.QLabel("3. Stats Display:")
    demo3_label.setStyleSheet("color: #9ca3af; font-size: 14px; font-weight: 600;")
    layout.addWidget(demo3_label)
    
    stats = StatsDisplay(views=1234, likes=56, bookmarks=23)
    layout.addWidget(stats)
    
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec_())
