# 🎨 Fitur Interaksi User-Penerbit - Crypto Insight

## 📋 Daftar Fitur (Berdasarkan Prioritas)

### 🔥 PRIORITY 1 - MUST HAVE (Quick Wins)

#### 1. ❤️ Like/Unlike Artikel
**Kenapa Penting:**
- Feedback langsung untuk penerbit
- Metrik engagement yang simple
- Mudah diimplementasi

**Fitur:**
- User bisa like artikel yang sudah dipublish
- User bisa unlike artikel
- Penerbit bisa lihat jumlah likes per artikel
- User bisa lihat artikel yang di-like (My Liked Articles)

**Database Schema:**
```sql
CREATE TABLE article_likes (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)  -- Prevent duplicate likes
);
CREATE INDEX idx_article_likes_article ON article_likes(article_id);
CREATE INDEX idx_article_likes_user ON article_likes(username);
```

---

#### 2. 👁️ View Count
**Kenapa Penting:**
- Analytics untuk penerbit
- Menunjukkan artikel populer
- Sangat mudah diimplementasi

**Fitur:**
- Track setiap kali artikel dibuka
- Tampilkan jumlah views di artikel
- Penerbit bisa lihat artikel paling banyak dilihat

**Database Schema:**
```sql
ALTER TABLE news ADD COLUMN views INTEGER DEFAULT 0;

CREATE TABLE article_views (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) REFERENCES users(username) ON DELETE SET NULL,
    viewed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(50)
);
CREATE INDEX idx_article_views_article ON article_views(article_id);
CREATE INDEX idx_article_views_time ON article_views(viewed_at DESC);
```

---

#### 3. 🔖 Bookmark/Save Artikel
**Kenapa Penting:**
- User bisa save artikel untuk dibaca nanti
- Meningkatkan retention
- Mudah diimplementasi

**Fitur:**
- User bisa bookmark artikel
- User punya halaman "Saved Articles"
- Unbookmark kapan saja

**Database Schema:**
```sql
CREATE TABLE article_bookmarks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    bookmarked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)
);
CREATE INDEX idx_bookmarks_user ON article_bookmarks(username);
CREATE INDEX idx_bookmarks_article ON article_bookmarks(article_id);
```

---

### 🚀 PRIORITY 2 - SHOULD HAVE (Engagement Boosters)

#### 4. 💬 Comment System
**Kenapa Penting:**
- Diskusi dan engagement tinggi
- Community building
- Feedback detail untuk penerbit

**Fitur:**
- User bisa comment di artikel
- User bisa reply ke comment (nested comments)
- User bisa edit/delete comment sendiri
- Penerbit bisa reply ke comment
- Moderasi comment (admin/penerbit bisa hapus comment)

**Database Schema:**
```sql
CREATE TABLE article_comments (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    parent_comment_id INTEGER REFERENCES article_comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);
CREATE INDEX idx_comments_article ON article_comments(article_id);
CREATE INDEX idx_comments_user ON article_comments(username);
CREATE INDEX idx_comments_parent ON article_comments(parent_comment_id);

-- Comment Likes (optional)
CREATE TABLE comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL REFERENCES article_comments(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(comment_id, username)
);
```

---

#### 5. ⭐ Rating System (1-5 stars)
**Kenapa Penting:**
- Kualitas konten metrics
- Help users find best articles
- Motivasi penerbit untuk improve

**Fitur:**
- User bisa rate artikel 1-5 bintang
- User bisa update rating
- Tampilkan average rating per artikel
- Filter artikel by rating

**Database Schema:**
```sql
CREATE TABLE article_ratings (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    rated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    UNIQUE(article_id, username)
);
CREATE INDEX idx_ratings_article ON article_ratings(article_id);

-- Add average rating to news table
ALTER TABLE news ADD COLUMN avg_rating DECIMAL(3,2) DEFAULT 0.0;
ALTER TABLE news ADD COLUMN total_ratings INTEGER DEFAULT 0;
```

---

#### 6. 👥 Follow Penerbit
**Kenapa Penting:**
- Personalized feed untuk user
- Build fanbase untuk penerbit
- Notification untuk konten baru

**Fitur:**
- User bisa follow penerbit
- User punya feed "Following" dengan artikel dari penerbit yang difollow
- Penerbit bisa lihat jumlah followers
- Notification saat penerbit post artikel baru (optional)

**Database Schema:**
```sql
CREATE TABLE user_follows (
    id SERIAL PRIMARY KEY,
    follower_username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    following_username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    followed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(follower_username, following_username),
    CHECK (follower_username != following_username)  -- Can't follow yourself
);
CREATE INDEX idx_follows_follower ON user_follows(follower_username);
CREATE INDEX idx_follows_following ON user_follows(following_username);

-- Add follower count to users
ALTER TABLE users ADD COLUMN follower_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN following_count INTEGER DEFAULT 0;
```

---

### 🎁 PRIORITY 3 - NICE TO HAVE (Advanced Features)

#### 7. 🔔 Notification System
**Kenapa Penting:**
- Keep users engaged
- Update user tentang activity baru
- Meningkatkan retention

**Fitur:**
- Notif saat artikel baru dari penerbit yang difollow
- Notif saat ada reply ke comment user
- Notif saat artikel user di-like/comment
- Mark as read functionality

**Database Schema:**
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- 'new_article', 'new_comment', 'new_reply', 'article_liked'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_article_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    related_comment_id INTEGER REFERENCES article_comments(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(username);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

---

#### 8. 📤 Share Article
**Kenapa Penting:**
- Viral marketing
- Expand reach
- Social proof

**Fitur:**
- Generate shareable link
- Copy link to clipboard
- Track share count
- Share to external platforms (Twitter, Telegram, WhatsApp)

**Database Schema:**
```sql
ALTER TABLE news ADD COLUMN share_count INTEGER DEFAULT 0;

CREATE TABLE article_shares (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) REFERENCES users(username) ON DELETE SET NULL,
    platform VARCHAR(50),  -- 'twitter', 'telegram', 'whatsapp', 'clipboard'
    shared_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_shares_article ON article_shares(article_id);
```

---

#### 9. 🚩 Report System
**Kenapa Penting:**
- Content moderation
- User safety
- Maintain quality

**Fitur:**
- User bisa report artikel/comment
- Reason: spam, misleading, offensive, etc.
- Admin review dan action

**Database Schema:**
```sql
CREATE TABLE article_reports (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES article_comments(id) ON DELETE CASCADE,
    reported_by VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    reason VARCHAR(100) NOT NULL,  -- 'spam', 'misleading', 'offensive', 'plagiarism'
    details TEXT,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'reviewed', 'action_taken', 'dismissed'
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_by VARCHAR(100) REFERENCES users(username) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    CHECK (article_id IS NOT NULL OR comment_id IS NOT NULL)
);
CREATE INDEX idx_reports_status ON article_reports(status);
CREATE INDEX idx_reports_article ON article_reports(article_id);
```

---

#### 10. 📊 Reading Time & Progress
**Kenapa Penting:**
- UX improvement
- Analytics untuk penerbit
- Gamification

**Fitur:**
- Estimate reading time (words / 200 wpm)
- Track reading progress
- "Continue Reading" feature
- Reading history

**Database Schema:**
```sql
ALTER TABLE news ADD COLUMN reading_time_minutes INTEGER;  -- Auto-calculate from content

CREATE TABLE reading_progress (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    last_read_at TIMESTAMPTZ DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE,
    UNIQUE(article_id, username)
);
CREATE INDEX idx_progress_user ON reading_progress(username);
```

---

## 🎯 Recommended Implementation Order

### Phase 1: Basic Engagement (Week 1-2)
1. ✅ View Count
2. ✅ Like/Unlike
3. ✅ Bookmark

### Phase 2: Community Building (Week 3-4)
4. ✅ Comment System
5. ✅ Rating System
6. ✅ Follow Penerbit

### Phase 3: Advanced Features (Week 5-6)
7. ✅ Notification System
8. ✅ Share Article
9. ✅ Report System
10. ✅ Reading Progress

---

## 📈 Analytics Dashboard untuk Penerbit

Dengan fitur-fitur di atas, Penerbit akan punya dashboard dengan metrics:

### Article Performance:
- 📊 Total Views
- ❤️ Total Likes
- ⭐ Average Rating
- 💬 Comment Count
- 🔖 Bookmark Count
- 📤 Share Count

### Audience Insights:
- 👥 Total Followers
- 📈 Follower Growth
- 👁️ Most Viewed Articles
- ❤️ Most Liked Articles
- 💬 Most Discussed Articles

### Engagement Metrics:
- 📉 Engagement Rate = (Likes + Comments + Shares) / Views
- ⏱️ Average Reading Time
- 📊 Completion Rate
- 🔄 Return Reader Rate

---

## 🎨 UI/UX Components Needed

### For User Dashboard:
- 📰 News Feed (with filters: Following, Popular, Latest)
- ❤️ My Liked Articles
- 🔖 My Saved Articles
- 💬 My Comments
- 👥 Following List
- 🔔 Notifications Panel

### For Penerbit Dashboard:
- 📊 Analytics Dashboard (existing + new metrics)
- 💬 Comment Management
- 🚩 Reports to Review
- 👥 Followers List
- 📈 Performance Charts

### Shared Components:
- 💬 Comment Widget (with nested replies)
- ⭐ Rating Widget (5-star display)
- 📤 Share Dialog
- 🚩 Report Dialog
- 🔔 Notification Dropdown

---

## 🔐 Permission Matrix

| Action | User | Penerbit | Admin |
|--------|------|----------|-------|
| Like Article | ✅ | ✅ | ✅ |
| Comment | ✅ | ✅ | ✅ |
| Rate Article | ✅ | ❌ (can't rate own) | ✅ |
| Bookmark | ✅ | ✅ | ✅ |
| Follow Penerbit | ✅ | ✅ | ✅ |
| Delete Own Comment | ✅ | ✅ | ✅ |
| Delete Any Comment | ❌ | ✅ (on own article) | ✅ |
| Report Content | ✅ | ✅ | ✅ |
| Review Reports | ❌ | ❌ | ✅ |
| Share Article | ✅ | ✅ | ✅ |

---

## 📝 Next Steps

1. **Choose Phase 1 Features** (Quick wins untuk MVP)
2. **Update Database Schema** (run migration scripts)
3. **Implement Backend Functions** (di app_db_fixed.py)
4. **Create UI Components** (widgets untuk like, comment, etc)
5. **Update Dashboards** (add new tabs/sections)
6. **Testing** (test all interactions)
7. **Deploy** 🚀

---

## 💡 Pro Tips

1. **Start Simple**: Phase 1 bisa selesai dalam 1-2 minggu
2. **Use Icons**: Emoji atau icon untuk visual feedback
3. **Real-time Updates**: Consider using WebSocket untuk notifications
4. **Mobile Responsive**: Design untuk mobile juga
5. **Gamification**: Leaderboard untuk top penerbit, badges, etc.
6. **SEO**: Make articles shareable dengan Open Graph tags

---

## 🎉 Benefits

### For Users:
- ✨ Engaging experience
- 🎯 Personalized content
- 💬 Community participation
- 🔖 Organized reading

### For Penerbit:
- 📊 Clear analytics
- 👥 Build audience
- 💬 Direct feedback
- 🏆 Recognition

### For Platform:
- 📈 Increased engagement
- 🔄 Higher retention
- 🌟 Quality content
- 💰 Monetization potential

---

Pilih fitur mana yang mau diimplementasi dulu? Saya bisa bantu buatkan kode lengkapnya! 🚀
