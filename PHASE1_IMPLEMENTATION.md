# 🚀 Phase 1 Implementation - Like, View, Bookmark

## 📦 Package yang Dibutuhkan

```bash
pip install PyQt5>=5.15.0 psycopg2-binary>=2.9.0
```

---

## 🗄️ Step 1: Database Migration

Jalankan SQL berikut di Railway PostgreSQL (atau database Anda):

```sql
-- ============================================
-- PHASE 1: Like, View Count, Bookmark
-- ============================================

-- 1. Article Likes
CREATE TABLE IF NOT EXISTS article_likes (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)
);
CREATE INDEX IF NOT EXISTS idx_article_likes_article ON article_likes(article_id);
CREATE INDEX IF NOT EXISTS idx_article_likes_user ON article_likes(username);

-- 2. Article Views
ALTER TABLE news ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;

CREATE TABLE IF NOT EXISTS article_views (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) REFERENCES users(username) ON DELETE SET NULL,
    viewed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_article_views_article ON article_views(article_id);
CREATE INDEX IF NOT EXISTS idx_article_views_time ON article_views(viewed_at DESC);

-- 3. Article Bookmarks
CREATE TABLE IF NOT EXISTS article_bookmarks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    bookmarked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)
);
CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON article_bookmarks(username);
CREATE INDEX IF NOT EXISTS idx_bookmarks_article ON article_bookmarks(article_id);

-- Add columns to news table for quick access
ALTER TABLE news ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0;
ALTER TABLE news ADD COLUMN IF NOT EXISTS bookmark_count INTEGER DEFAULT 0;

-- Success message
SELECT 'Phase 1 tables created successfully!' as message;
```

---

## 📚 Step 2: Backend Functions (app_db_interactions.py)

Buat file baru: `app_db_interactions.py`

```python
# app_db_interactions.py — User Interactions dengan Artikel
"""
Backend functions untuk fitur interaksi user-penerbit:
- Like/Unlike artikel
- View tracking
- Bookmark/Unbookmark artikel
"""

from app_db_fixed import connect
from typing import Optional, List, Tuple
import psycopg2

# ============================================
# LIKE FUNCTIONS
# ============================================

def like_article(article_id: int, username: str) -> bool:
    """
    User like artikel. Returns True if successful.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Insert like
        cur.execute("""
            INSERT INTO article_likes (article_id, username)
            VALUES (%s, %s)
            ON CONFLICT (article_id, username) DO NOTHING
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        
        if result:
            # Update like count
            cur.execute("""
                UPDATE news SET like_count = like_count + 1
                WHERE id = %s;
            """, (article_id,))
        
        conn.commit()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error liking article: {e}")
        return False


def unlike_article(article_id: int, username: str) -> bool:
    """
    User unlike artikel. Returns True if successful.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Delete like
        cur.execute("""
            DELETE FROM article_likes
            WHERE article_id = %s AND username = %s
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        
        if result:
            # Update like count
            cur.execute("""
                UPDATE news SET like_count = GREATEST(like_count - 1, 0)
                WHERE id = %s;
            """, (article_id,))
        
        conn.commit()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error unliking article: {e}")
        return False


def is_article_liked(article_id: int, username: str) -> bool:
    """
    Check if user sudah like artikel. Returns True if liked.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM article_likes
            WHERE article_id = %s AND username = %s;
        """, (article_id, username))
        
        result = cur.fetchone()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error checking like status: {e}")
        return False


def get_article_likes_count(article_id: int) -> int:
    """
    Get total likes untuk artikel.
    """
    try:
        conn, _ = connect()
        if not conn:
            return 0
        
        cur = conn.cursor()
        cur.execute("""
            SELECT like_count FROM news WHERE id = %s;
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        return result[0] if result else 0
        
    except Exception as e:
        print(f"❌ Error getting likes count: {e}")
        return 0


def get_user_liked_articles(username: str, limit: int = 50) -> List[Tuple]:
    """
    Get list artikel yang di-like oleh user.
    Returns: [(article_id, title, author, liked_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT n.id, n.title, n.author, al.liked_at
            FROM article_likes al
            JOIN news n ON al.article_id = n.id
            WHERE al.username = %s
            ORDER BY al.liked_at DESC
            LIMIT %s;
        """, (username, limit))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting liked articles: {e}")
        return []


# ============================================
# VIEW TRACKING
# ============================================

def track_article_view(article_id: int, username: Optional[str] = None, ip_address: str = "0.0.0.0") -> bool:
    """
    Track artikel view. Returns True if successful.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Insert view record
        cur.execute("""
            INSERT INTO article_views (article_id, username, ip_address)
            VALUES (%s, %s, %s);
        """, (article_id, username, ip_address))
        
        # Update view count
        cur.execute("""
            UPDATE news SET views = views + 1
            WHERE id = %s;
        """, (article_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error tracking view: {e}")
        return False


def get_article_views(article_id: int) -> int:
    """
    Get total views untuk artikel.
    """
    try:
        conn, _ = connect()
        if not conn:
            return 0
        
        cur = conn.cursor()
        cur.execute("""
            SELECT views FROM news WHERE id = %s;
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        return result[0] if result else 0
        
    except Exception as e:
        print(f"❌ Error getting views: {e}")
        return 0


def get_trending_articles(limit: int = 10, days: int = 7) -> List[Tuple]:
    """
    Get trending articles berdasarkan views dalam N hari terakhir.
    Returns: [(article_id, title, author, views, likes), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute(f"""
            SELECT n.id, n.title, n.author, n.views, n.like_count
            FROM news n
            WHERE n.status = 'published'
            AND n.created_at > NOW() - INTERVAL '{days} days'
            ORDER BY n.views DESC, n.like_count DESC
            LIMIT %s;
        """, (limit,))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting trending articles: {e}")
        return []


# ============================================
# BOOKMARK FUNCTIONS
# ============================================

def bookmark_article(article_id: int, username: str) -> bool:
    """
    User bookmark artikel. Returns True if successful.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Insert bookmark
        cur.execute("""
            INSERT INTO article_bookmarks (article_id, username)
            VALUES (%s, %s)
            ON CONFLICT (article_id, username) DO NOTHING
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        
        if result:
            # Update bookmark count
            cur.execute("""
                UPDATE news SET bookmark_count = bookmark_count + 1
                WHERE id = %s;
            """, (article_id,))
        
        conn.commit()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error bookmarking article: {e}")
        return False


def unbookmark_article(article_id: int, username: str) -> bool:
    """
    User unbookmark artikel. Returns True if successful.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Delete bookmark
        cur.execute("""
            DELETE FROM article_bookmarks
            WHERE article_id = %s AND username = %s
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        
        if result:
            # Update bookmark count
            cur.execute("""
                UPDATE news SET bookmark_count = GREATEST(bookmark_count - 1, 0)
                WHERE id = %s;
            """, (article_id,))
        
        conn.commit()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error unbookmarking article: {e}")
        return False


def is_article_bookmarked(article_id: int, username: str) -> bool:
    """
    Check if user sudah bookmark artikel. Returns True if bookmarked.
    """
    try:
        conn, _ = connect()
        if not conn:
            return False
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM article_bookmarks
            WHERE article_id = %s AND username = %s;
        """, (article_id, username))
        
        result = cur.fetchone()
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Error checking bookmark status: {e}")
        return False


def get_user_bookmarked_articles(username: str, limit: int = 50) -> List[Tuple]:
    """
    Get list artikel yang di-bookmark oleh user.
    Returns: [(article_id, title, author, bookmarked_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT n.id, n.title, n.author, ab.bookmarked_at
            FROM article_bookmarks ab
            JOIN news n ON ab.article_id = n.id
            WHERE ab.username = %s
            ORDER BY ab.bookmarked_at DESC
            LIMIT %s;
        """, (username, limit))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting bookmarked articles: {e}")
        return []


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_article_stats(article_id: int) -> dict:
    """
    Get semua stats untuk artikel.
    Returns: {views, likes, bookmarks}
    """
    try:
        conn, _ = connect()
        if not conn:
            return {'views': 0, 'likes': 0, 'bookmarks': 0}
        
        cur = conn.cursor()
        cur.execute("""
            SELECT views, like_count, bookmark_count
            FROM news WHERE id = %s;
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                'views': result[0] or 0,
                'likes': result[1] or 0,
                'bookmarks': result[2] or 0
            }
        return {'views': 0, 'likes': 0, 'bookmarks': 0}
        
    except Exception as e:
        print(f"❌ Error getting article stats: {e}")
        return {'views': 0, 'likes': 0, 'bookmarks': 0}


def get_user_interaction_summary(username: str) -> dict:
    """
    Get summary interaksi user.
    Returns: {liked_count, bookmarked_count}
    """
    try:
        conn, _ = connect()
        if not conn:
            return {'liked': 0, 'bookmarked': 0}
        
        cur = conn.cursor()
        
        # Count likes
        cur.execute("""
            SELECT COUNT(*) FROM article_likes WHERE username = %s;
        """, (username,))
        liked = cur.fetchone()[0]
        
        # Count bookmarks
        cur.execute("""
            SELECT COUNT(*) FROM article_bookmarks WHERE username = %s;
        """, (username,))
        bookmarked = cur.fetchone()[0]
        
        conn.close()
        
        return {
            'liked': liked,
            'bookmarked': bookmarked
        }
        
    except Exception as e:
        print(f"❌ Error getting user summary: {e}")
        return {'liked': 0, 'bookmarked': 0}


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("🧪 Testing interaction functions...")
    
    # Test like
    print("\n1. Testing like_article...")
    success = like_article(1, "testuser")
    print(f"   Like article 1: {success}")
    
    # Test check liked
    print("\n2. Testing is_article_liked...")
    is_liked = is_article_liked(1, "testuser")
    print(f"   Article 1 liked: {is_liked}")
    
    # Test get likes count
    print("\n3. Testing get_article_likes_count...")
    count = get_article_likes_count(1)
    print(f"   Article 1 likes: {count}")
    
    # Test unlike
    print("\n4. Testing unlike_article...")
    success = unlike_article(1, "testuser")
    print(f"   Unlike article 1: {success}")
    
    # Test bookmark
    print("\n5. Testing bookmark_article...")
    success = bookmark_article(1, "testuser")
    print(f"   Bookmark article 1: {success}")
    
    # Test get bookmarks
    print("\n6. Testing get_user_bookmarked_articles...")
    bookmarks = get_user_bookmarked_articles("testuser")
    print(f"   User bookmarks: {len(bookmarks)} articles")
    
    # Test article stats
    print("\n7. Testing get_article_stats...")
    stats = get_article_stats(1)
    print(f"   Article stats: {stats}")
    
    print("\n✅ All tests completed!")
```

---

## 🎨 Step 3: UI Components (interaction_widgets.py)

```python
# interaction_widgets.py — UI Widgets untuk Interaksi
from PyQt5 import QtWidgets, QtCore, QtGui
from app_db_interactions import (
    like_article, unlike_article, is_article_liked,
    bookmark_article, unbookmark_article, is_article_bookmarked,
    track_article_view, get_article_stats
)


class ArticleInteractionBar(QtWidgets.QWidget):
    """
    Widget untuk like, bookmark, dan share buttons
    """
    
    def __init__(self, article_id: int, username: str, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.username = username
        
        self._setup_ui()
        self._load_states()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Like button
        self.btn_like = QtWidgets.QPushButton()
        self.btn_like.setObjectName("interactionBtn")
        self.btn_like.setFixedSize(100, 40)
        self.btn_like.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_like.clicked.connect(self._toggle_like)
        
        # Bookmark button
        self.btn_bookmark = QtWidgets.QPushButton()
        self.btn_bookmark.setObjectName("interactionBtn")
        self.btn_bookmark.setFixedSize(120, 40)
        self.btn_bookmark.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_bookmark.clicked.connect(self._toggle_bookmark)
        
        # Share button
        self.btn_share = QtWidgets.QPushButton("📤 Share")
        self.btn_share.setObjectName("interactionBtn")
        self.btn_share.setFixedSize(100, 40)
        self.btn_share.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Views label
        self.label_views = QtWidgets.QLabel()
        self.label_views.setObjectName("statsLabel")
        
        layout.addWidget(self.btn_like)
        layout.addWidget(self.btn_bookmark)
        layout.addWidget(self.btn_share)
        layout.addStretch()
        layout.addWidget(self.label_views)
    
    def _load_states(self):
        """Load current states from database"""
        # Check if liked
        self.is_liked = is_article_liked(self.article_id, self.username)
        self._update_like_button()
        
        # Check if bookmarked
        self.is_bookmarked = is_article_bookmarked(self.article_id, self.username)
        self._update_bookmark_button()
        
        # Get stats
        stats = get_article_stats(self.article_id)
        self.label_views.setText(f"👁️ {stats['views']} views")
        
        # Track view
        track_article_view(self.article_id, self.username)
    
    def _toggle_like(self):
        """Toggle like status"""
        if self.is_liked:
            success = unlike_article(self.article_id, self.username)
            if success:
                self.is_liked = False
        else:
            success = like_article(self.article_id, self.username)
            if success:
                self.is_liked = True
        
        self._update_like_button()
    
    def _update_like_button(self):
        """Update like button appearance"""
        stats = get_article_stats(self.article_id)
        
        if self.is_liked:
            self.btn_like.setText(f"❤️ {stats['likes']}")
            self.btn_like.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #dc2626;
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
                }
                QPushButton:hover {
                    background: #15161d;
                    color: #e5e7eb;
                }
            """)
    
    def _toggle_bookmark(self):
        """Toggle bookmark status"""
        if self.is_bookmarked:
            success = unbookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = False
        else:
            success = bookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = True
        
        self._update_bookmark_button()
    
    def _update_bookmark_button(self):
        """Update bookmark button appearance"""
        stats = get_article_stats(self.article_id)
        
        if self.is_bookmarked:
            self.btn_bookmark.setText(f"🔖 Saved ({stats['bookmarks']})")
            self.btn_bookmark.setStyleSheet("""
                QPushButton {
                    background: #7c5cff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #6a4cf7;
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
                }
                QPushButton:hover {
                    background: #15161d;
                    color: #e5e7eb;
                }
            """)
    
    def _apply_style(self):
        """Apply styles"""
        self.setStyleSheet("""
            #statsLabel {
                color: #6b7280;
                font-size: 13px;
            }
        """)


# ============================================
# DEMO
# ============================================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Demo window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Interaction Bar Demo")
    window.resize(600, 100)
    window.setStyleSheet("background: #0e0f12;")
    
    layout = QtWidgets.QVBoxLayout(window)
    
    # Article interaction bar
    interaction_bar = ArticleInteractionBar(
        article_id=1,
        username="testuser"
    )
    layout.addWidget(interaction_bar)
    
    window.show()
    sys.exit(app.exec_())
```

---

## 🎯 Step 4: Integration dengan User Dashboard

Update `user_dashboard.py` untuk menambahkan tabs baru:

```python
# Tambahkan di user_dashboard.py

def _setup_ui(self):
    # ... existing code ...
    
    # Create tab widget
    self.tabs = QtWidgets.QTabWidget()
    
    # Tab 1: News Feed
    self.tab_feed = self._create_feed_tab()
    self.tabs.addTab(self.tab_feed, "📰 News Feed")
    
    # Tab 2: Liked Articles (NEW!)
    self.tab_liked = self._create_liked_tab()
    self.tabs.addTab(self.tab_liked, "❤️ Liked Articles")
    
    # Tab 3: Saved Articles (NEW!)
    self.tab_saved = self._create_saved_tab()
    self.tabs.addTab(self.tab_saved, "🔖 Saved Articles")
    
    layout.addWidget(self.tabs)

def _create_liked_tab(self):
    """Create liked articles tab"""
    from app_db_interactions import get_user_liked_articles
    
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    
    # ... implement liked articles list ...
    
    return widget

def _create_saved_tab(self):
    """Create saved articles tab"""
    from app_db_interactions import get_user_bookmarked_articles
    
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    
    # ... implement saved articles list ...
    
    return widget
```

---

## ✅ Testing Checklist

- [ ] Database migration berhasil
- [ ] Backend functions tested
- [ ] Like button works
- [ ] Unlike button works
- [ ] Bookmark button works
- [ ] Unbookmark button works
- [ ] View count increases
- [ ] Stats displayed correctly
- [ ] UI responsive dan smooth

---

## 📊 Expected Results

Setelah implementasi Phase 1, user bisa:
✅ Like artikel (button berubah merah)
✅ Unlike artikel (button kembali abu-abu)
✅ Bookmark artikel untuk dibaca nanti
✅ Lihat semua artikel yang di-like
✅ Lihat semua artikel yang di-bookmark
✅ Penerbit bisa lihat metrics (views, likes, bookmarks)

---

Mau saya buatkan implementasi lengkap untuk semua file? 🚀
