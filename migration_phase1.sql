-- ============================================
-- CRYPTO INSIGHT - PHASE 1 MIGRATION
-- Like, Bookmark, View Count Features
-- ============================================
-- 
-- Run this script in your Railway PostgreSQL console
-- Or using psql: psql $DATABASE_URL -f migration_phase1.sql
--
-- ============================================

-- Start transaction
BEGIN;

-- ============================================
-- 1. ARTICLE LIKES
-- ============================================

CREATE TABLE IF NOT EXISTS article_likes (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)
);

CREATE INDEX IF NOT EXISTS idx_article_likes_article ON article_likes(article_id);
CREATE INDEX IF NOT EXISTS idx_article_likes_user ON article_likes(username);
CREATE INDEX IF NOT EXISTS idx_article_likes_time ON article_likes(liked_at DESC);

COMMENT ON TABLE article_likes IS 'Stores user likes for articles';

-- ============================================
-- 2. ARTICLE VIEWS
-- ============================================

-- Add views column to news table
ALTER TABLE news ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;

CREATE TABLE IF NOT EXISTS article_views (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) REFERENCES users(username) ON DELETE SET NULL,
    viewed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(50) DEFAULT '0.0.0.0'
);

CREATE INDEX IF NOT EXISTS idx_article_views_article ON article_views(article_id);
CREATE INDEX IF NOT EXISTS idx_article_views_user ON article_views(username);
CREATE INDEX IF NOT EXISTS idx_article_views_time ON article_views(viewed_at DESC);

COMMENT ON TABLE article_views IS 'Tracks individual article views';

-- ============================================
-- 3. ARTICLE BOOKMARKS
-- ============================================

CREATE TABLE IF NOT EXISTS article_bookmarks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    bookmarked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(article_id, username)
);

CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON article_bookmarks(username);
CREATE INDEX IF NOT EXISTS idx_bookmarks_article ON article_bookmarks(article_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_time ON article_bookmarks(bookmarked_at DESC);

COMMENT ON TABLE article_bookmarks IS 'Stores user bookmarks for articles';

-- ============================================
-- 4. ADD COUNTER COLUMNS TO NEWS TABLE
-- ============================================

-- Add like_count column
ALTER TABLE news ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0;

-- Add bookmark_count column
ALTER TABLE news ADD COLUMN IF NOT EXISTS bookmark_count INTEGER DEFAULT 0;

-- ============================================
-- 5. UPDATE EXISTING DATA (Initialize counts)
-- ============================================

-- Update like_count based on existing likes (if any)
UPDATE news n
SET like_count = (
    SELECT COUNT(*)
    FROM article_likes al
    WHERE al.article_id = n.id
)
WHERE EXISTS (SELECT 1 FROM article_likes al WHERE al.article_id = n.id);

-- Update bookmark_count based on existing bookmarks (if any)
UPDATE news n
SET bookmark_count = (
    SELECT COUNT(*)
    FROM article_bookmarks ab
    WHERE ab.article_id = n.id
)
WHERE EXISTS (SELECT 1 FROM article_bookmarks ab WHERE ab.article_id = n.id);

-- ============================================
-- 6. CREATE TRIGGER FUNCTIONS FOR AUTO-UPDATE
-- ============================================

-- Function to update like_count when like added/removed
CREATE OR REPLACE FUNCTION update_article_like_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE news SET like_count = like_count + 1 WHERE id = NEW.article_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE news SET like_count = GREATEST(like_count - 1, 0) WHERE id = OLD.article_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to update bookmark_count when bookmark added/removed
CREATE OR REPLACE FUNCTION update_article_bookmark_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE news SET bookmark_count = bookmark_count + 1 WHERE id = NEW.article_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE news SET bookmark_count = GREATEST(bookmark_count - 1, 0) WHERE id = OLD.article_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to update views when article viewed
CREATE OR REPLACE FUNCTION update_article_view_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE news SET views = views + 1 WHERE id = NEW.article_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. CREATE TRIGGERS
-- ============================================

-- Drop triggers if they exist (for re-running script)
DROP TRIGGER IF EXISTS trg_article_likes_update ON article_likes;
DROP TRIGGER IF EXISTS trg_article_bookmarks_update ON article_bookmarks;
DROP TRIGGER IF EXISTS trg_article_views_update ON article_views;

-- Create triggers
CREATE TRIGGER trg_article_likes_update
    AFTER INSERT OR DELETE ON article_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_article_like_count();

CREATE TRIGGER trg_article_bookmarks_update
    AFTER INSERT OR DELETE ON article_bookmarks
    FOR EACH ROW
    EXECUTE FUNCTION update_article_bookmark_count();

CREATE TRIGGER trg_article_views_update
    AFTER INSERT ON article_views
    FOR EACH ROW
    EXECUTE FUNCTION update_article_view_count();

-- ============================================
-- 8. CREATE USEFUL VIEWS
-- ============================================

-- View: Popular articles (by views)
CREATE OR REPLACE VIEW v_popular_articles AS
SELECT 
    n.id,
    n.title,
    n.author,
    n.views,
    n.like_count,
    n.bookmark_count,
    n.created_at,
    to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at_formatted
FROM news n
WHERE n.status = 'published'
ORDER BY n.views DESC, n.like_count DESC;

-- View: Trending articles (last 7 days)
CREATE OR REPLACE VIEW v_trending_articles AS
SELECT 
    n.id,
    n.title,
    n.author,
    n.views,
    n.like_count,
    n.bookmark_count,
    n.created_at,
    to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at_formatted
FROM news n
WHERE n.status = 'published'
AND n.created_at > NOW() - INTERVAL '7 days'
ORDER BY n.views DESC, n.like_count DESC;

-- View: Most liked articles
CREATE OR REPLACE VIEW v_most_liked_articles AS
SELECT 
    n.id,
    n.title,
    n.author,
    n.views,
    n.like_count,
    n.bookmark_count,
    n.created_at,
    to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at_formatted
FROM news n
WHERE n.status = 'published'
ORDER BY n.like_count DESC, n.views DESC;

-- ============================================
-- 9. VERIFY INSTALLATION
-- ============================================

-- Check if all tables exist
DO $$
DECLARE
    tables_exist BOOLEAN;
BEGIN
    SELECT 
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'article_likes') AND
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'article_views') AND
        EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'article_bookmarks')
    INTO tables_exist;
    
    IF tables_exist THEN
        RAISE NOTICE '✅ All Phase 1 tables created successfully!';
    ELSE
        RAISE EXCEPTION '❌ Some tables failed to create!';
    END IF;
END $$;

-- Display summary
SELECT 
    '✅ PHASE 1 MIGRATION COMPLETED!' as status,
    (SELECT COUNT(*) FROM article_likes) as total_likes,
    (SELECT COUNT(*) FROM article_bookmarks) as total_bookmarks,
    (SELECT COUNT(*) FROM article_views) as total_views,
    (SELECT COUNT(*) FROM news WHERE like_count > 0) as articles_with_likes,
    (SELECT COUNT(*) FROM news WHERE bookmark_count > 0) as articles_with_bookmarks,
    (SELECT COUNT(*) FROM news WHERE views > 0) as articles_with_views;

-- Commit transaction
COMMIT;

-- ============================================
-- ROLLBACK SCRIPT (In case you need to undo)
-- ============================================
-- Uncomment and run this if you need to rollback:
/*
BEGIN;
DROP VIEW IF EXISTS v_popular_articles CASCADE;
DROP VIEW IF EXISTS v_trending_articles CASCADE;
DROP VIEW IF EXISTS v_most_liked_articles CASCADE;
DROP TRIGGER IF EXISTS trg_article_likes_update ON article_likes;
DROP TRIGGER IF EXISTS trg_article_bookmarks_update ON article_bookmarks;
DROP TRIGGER IF EXISTS trg_article_views_update ON article_views;
DROP FUNCTION IF EXISTS update_article_like_count() CASCADE;
DROP FUNCTION IF EXISTS update_article_bookmark_count() CASCADE;
DROP FUNCTION IF EXISTS update_article_view_count() CASCADE;
DROP TABLE IF EXISTS article_likes CASCADE;
DROP TABLE IF EXISTS article_views CASCADE;
DROP TABLE IF EXISTS article_bookmarks CASCADE;
ALTER TABLE news DROP COLUMN IF EXISTS like_count;
ALTER TABLE news DROP COLUMN IF EXISTS bookmark_count;
ALTER TABLE news DROP COLUMN IF EXISTS views;
COMMIT;
*/

-- ============================================
-- DONE! 🎉
-- ============================================
-- Next steps:
-- 1. ✅ Migration completed
-- 2. 📦 Install Python backend files
-- 3. 🎨 Update UI components
-- 4. 🚀 Run application
-- ============================================
