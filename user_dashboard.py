# user_dashboard_enhanced.py — Enhanced User Dashboard with Phase 1 Features
"""
Enhanced User Dashboard dengan:
- News Feed (Trending, Popular, Latest articles)
- Liked Articles tab
- Saved/Bookmarked Articles tab
- Article cards dengan Like/Bookmark buttons
- Real-time stats

Author: Claude + Reza
Version: 1.0 - Phase 1 Enhanced UI
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Optional, List, Tuple
from app_db_fixed import heartbeat, end_session
from app_db_interactions import (
    get_trending_articles,
    get_popular_articles,
    get_most_liked_articles,
    get_user_liked_articles,
    get_user_bookmarked_articles,
    get_user_interaction_summary,
    get_article_full_info,
    like_article,
    unlike_article,
    bookmark_article,
    unbookmark_article,
    is_article_liked,
    is_article_bookmarked,
    track_article_view
)


class ArticleCardCompact(QtWidgets.QFrame):
    """
    Compact article card dengan Like/Bookmark buttons
    """
    
    article_clicked = QtCore.pyqtSignal(int)  # Emits article_id
    
    def __init__(self, article_id: int, title: str, author: str, 
                 username: str, views: int = 0, likes: int = 0, 
                 bookmarks: int = 0, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.title = title
        self.author = author
        self.username = username
        self.views = views
        self.likes = likes
        self.bookmarks = bookmarks
        
        self.is_liked = is_article_liked(article_id, username)
        self.is_bookmarked = is_article_bookmarked(article_id, username)
        
        self.setObjectName("articleCard")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Title
        title_label = QtWidgets.QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Author
        author_label = QtWidgets.QLabel(f"by {self.author}")
        author_label.setObjectName("cardAuthor")
        layout.addWidget(author_label)
        
        # Stats + Buttons row
        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(12)
        
        # Views
        views_label = QtWidgets.QLabel(f"👁️ {self.views:,}")
        views_label.setObjectName("cardStat")
        stats_row.addWidget(views_label)
        
        stats_row.addStretch()
        
        # Like button
        self.btn_like = QtWidgets.QPushButton()
        self.btn_like.setFixedSize(32, 32)
        self.btn_like.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_like.clicked.connect(self._toggle_like)
        self._update_like_button()
        stats_row.addWidget(self.btn_like)
        
        # Bookmark button
        self.btn_bookmark = QtWidgets.QPushButton()
        self.btn_bookmark.setFixedSize(32, 32)
        self.btn_bookmark.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_bookmark.clicked.connect(self._toggle_bookmark)
        self._update_bookmark_button()
        stats_row.addWidget(self.btn_bookmark)
        
        layout.addLayout(stats_row)
    
    def _apply_styles(self):
        """Apply card styles"""
        self.setStyleSheet("""
            #articleCard {
                background: #15161d;
                border: 1px solid #25262f;
                border-radius: 8px;
            }
            #articleCard:hover {
                background: #1a1b26;
                border-color: #374151;
            }
            #cardTitle {
                color: #f9fafb;
                font-size: 14px;
                font-weight: 700;
            }
            #cardAuthor {
                color: #7c5cff;
                font-size: 11px;
                font-weight: 600;
            }
            #cardStat {
                color: #9ca3af;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #25262f;
            }
        """)
    
    def _toggle_like(self):
        """Toggle like"""
        if self.is_liked:
            success = unlike_article(self.article_id, self.username)
            if success:
                self.is_liked = False
                self.likes = max(0, self.likes - 1)
        else:
            success = like_article(self.article_id, self.username)
            if success:
                self.is_liked = True
                self.likes += 1
        
        if success:
            self._update_like_button()
    
    def _update_like_button(self):
        """Update like button appearance"""
        if self.is_liked:
            self.btn_like.setText("❤️")
            self.btn_like.setToolTip(f"Liked • {self.likes} total")
        else:
            self.btn_like.setText("🤍")
            self.btn_like.setToolTip(f"Like • {self.likes} total")
    
    def _toggle_bookmark(self):
        """Toggle bookmark"""
        if self.is_bookmarked:
            success = unbookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = False
                self.bookmarks = max(0, self.bookmarks - 1)
        else:
            success = bookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = True
                self.bookmarks += 1
        
        if success:
            self._update_bookmark_button()
    
    def _update_bookmark_button(self):
        """Update bookmark button appearance"""
        if self.is_bookmarked:
            self.btn_bookmark.setText("🔖")
            self.btn_bookmark.setToolTip(f"Saved • {self.bookmarks} total")
        else:
            self.btn_bookmark.setText("📑")
            self.btn_bookmark.setToolTip(f"Save • {self.bookmarks} total")
    
    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == QtCore.Qt.LeftButton:
            # Track view
            track_article_view(self.article_id, self.username)
            self.article_clicked.emit(self.article_id)
        super().mousePressEvent(event)


class ArticleListWidget(QtWidgets.QWidget):
    """
    Widget untuk menampilkan list of articles
    """
    
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Container for articles
        self.container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch()
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
    
    def load_articles(self, articles: List[Tuple]):
        """
        Load articles into list
        articles: [(id, title, author, views, likes, bookmarks, created_at), ...]
        """
        # Clear existing
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add articles
        if not articles:
            no_data = QtWidgets.QLabel("No articles found")
            no_data.setAlignment(QtCore.Qt.AlignCenter)
            no_data.setStyleSheet("color: #6b7280; font-size: 14px; padding: 40px;")
            self.container_layout.insertWidget(0, no_data)
            return
        
        for article in articles:
            article_id, title, author, views, likes, bookmarks, _ = article
            
            card = ArticleCardCompact(
                article_id=article_id,
                title=title,
                author=author,
                username=self.username,
                views=views,
                likes=likes,
                bookmarks=bookmarks
            )
            card.article_clicked.connect(self._on_article_clicked)
            self.container_layout.insertWidget(self.container_layout.count() - 1, card)
    
    def _on_article_clicked(self, article_id: int):
        """Handle article click"""
        # For now, just print
        print(f"Article {article_id} clicked")
        # TODO: Open article detail view


class EnhancedUserDashboard(QtWidgets.QMainWindow):
    """
    Enhanced User Dashboard dengan Phase 1 features
    """
    
    def __init__(self, username: str = "user", session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle("Crypto Insight — User Dashboard")
        self.resize(1100, 700)
        
        self._setup_ui()
        self._apply_styles()
        self._load_initial_data()
        
        # Heartbeat timer
        if self.session_id:
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(self.session_id))
            self.hb_timer.start(20000)
    
    def _setup_ui(self):
        """Setup UI"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        # Title
        title = QtWidgets.QLabel(f"Welcome, {self.username}! 🚀")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Stats
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setObjectName("statsLabel")
        header_layout.addWidget(self.stats_label)
        
        # Refresh button
        refresh_btn = QtWidgets.QPushButton("🔄")
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.setObjectName("iconBtn")
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self._refresh_current_tab)
        header_layout.addWidget(refresh_btn)
        
        # Logout button
        logout_btn = QtWidgets.QPushButton("Logout")
        logout_btn.setFixedHeight(36)
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self._logout)
        header_layout.addWidget(logout_btn)
        
        layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Tab 1: News Feed
        self.news_feed_tab = self._create_news_feed_tab()
        self.tabs.addTab(self.news_feed_tab, "📰 News Feed")
        
        # Tab 2: Liked Articles
        self.liked_tab = ArticleListWidget(self.username)
        self.tabs.addTab(self.liked_tab, "❤️ Liked")
        
        # Tab 3: Saved Articles
        self.saved_tab = ArticleListWidget(self.username)
        self.tabs.addTab(self.saved_tab, "🔖 Saved")
        
        layout.addWidget(self.tabs)
    
    def _create_news_feed_tab(self) -> QtWidgets.QWidget:
        """Create news feed tab with sub-tabs"""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 8, 0, 0)
        
        # Sub-tabs for different feeds
        sub_tabs = QtWidgets.QTabWidget()
        sub_tabs.setObjectName("subTabs")
        
        # Trending
        self.trending_list = ArticleListWidget(self.username)
        sub_tabs.addTab(self.trending_list, "🔥 Trending")
        
        # Popular
        self.popular_list = ArticleListWidget(self.username)
        sub_tabs.addTab(self.popular_list, "⭐ Popular")
        
        # Most Liked
        self.most_liked_list = ArticleListWidget(self.username)
        sub_tabs.addTab(self.most_liked_list, "❤️ Most Liked")
        
        layout.addWidget(sub_tabs)
        
        return tab
    
    def _apply_styles(self):
        """Apply styles"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #0a0b0e;
                color: #eaeaea;
            }
            #pageTitle {
                font-size: 22px;
                font-weight: 700;
                color: #7c5cff;
            }
            #statsLabel {
                color: #9ca3af;
                font-size: 12px;
                font-weight: 500;
            }
            #iconBtn {
                background: transparent;
                border: 1px solid #25262f;
                border-radius: 6px;
                color: #9ca3af;
                font-size: 16px;
            }
            #iconBtn:hover {
                background: #15161d;
                border-color: #374151;
                color: #e5e7eb;
            }
            #logoutBtn {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-weight: 600;
                font-size: 13px;
            }
            #logoutBtn:hover {
                background: #dc2626;
            }
            #mainTabs, #subTabs {
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #25262f;
                border-radius: 8px;
                background: #0e0f12;
            }
            QTabBar::tab {
                background: transparent;
                color: #9ca3af;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #7c5cff;
                border-bottom: 2px solid #7c5cff;
            }
            QTabBar::tab:hover {
                color: #e5e7eb;
            }
        """)
    
    def _load_initial_data(self):
        """Load initial data"""
        self._update_stats()
        self._load_trending()
        self._load_popular()
        self._load_most_liked()
    
    def _update_stats(self):
        """Update user stats"""
        try:
            summary = get_user_interaction_summary(self.username)
            liked = summary.get('liked', 0)
            bookmarked = summary.get('bookmarked', 0)
            self.stats_label.setText(f"❤️ {liked} liked  •  🔖 {bookmarked} saved")
        except Exception as e:
            print(f"Error updating stats: {e}")
            self.stats_label.setText("Stats unavailable")
    
    def _load_trending(self):
        """Load trending articles"""
        try:
            articles = get_trending_articles(limit=20, days=7)
            self.trending_list.load_articles(articles)
        except Exception as e:
            print(f"Error loading trending: {e}")
    
    def _load_popular(self):
        """Load popular articles"""
        try:
            articles = get_popular_articles(limit=20)
            self.popular_list.load_articles(articles)
        except Exception as e:
            print(f"Error loading popular: {e}")
    
    def _load_most_liked(self):
        """Load most liked articles"""
        try:
            articles = get_most_liked_articles(limit=20)
            self.most_liked_list.load_articles(articles)
        except Exception as e:
            print(f"Error loading most liked: {e}")
    
    def _load_liked_articles(self):
        """Load user's liked articles"""
        try:
            articles = get_user_liked_articles(self.username, limit=50)
            self.liked_tab.load_articles(articles)
        except Exception as e:
            print(f"Error loading liked articles: {e}")
    
    def _load_saved_articles(self):
        """Load user's saved articles"""
        try:
            articles = get_user_bookmarked_articles(self.username, limit=50)
            self.saved_tab.load_articles(articles)
        except Exception as e:
            print(f"Error loading saved articles: {e}")
    
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        if index == 1:  # Liked tab
            self._load_liked_articles()
        elif index == 2:  # Saved tab
            self._load_saved_articles()
        
        self._update_stats()
    
    def _refresh_current_tab(self):
        """Refresh current tab"""
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:  # News Feed
            self._load_trending()
            self._load_popular()
            self._load_most_liked()
        elif current_tab == 1:  # Liked
            self._load_liked_articles()
        elif current_tab == 2:  # Saved
            self._load_saved_articles()
        
        self._update_stats()
        print("✅ Refreshed!")
    
    def _logout(self):
        """Logout"""
        if hasattr(self, 'hb_timer') and self.hb_timer.isActive():
            self.hb_timer.stop()
        
        if self.session_id:
            try:
                end_session(self.session_id)
            except Exception as e:
                print(f"Error ending session: {e}")
        
        self.close()
    
    def closeEvent(self, event):
        """Handle window close"""
        self._logout()
        event.accept()


# Alias for backward compatibility
UserDashboard = EnhancedUserDashboard


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Demo
    dashboard = EnhancedUserDashboard(username="demo_user")
    dashboard.show()
    
    sys.exit(app.exec_())
