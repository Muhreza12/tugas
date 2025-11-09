# app_db_interactions.py — User-Penerbit Interaction Backend
"""
Complete backend functions untuk Phase 1 features:
- Like/Unlike articles
- View tracking
- Bookmark/Unbookmark articles
- Get user interaction data
- Get article statistics

Author: Claude + Reza
Version: 1.0 - Phase 1 Complete
"""

from app_db_fixed import connect
from typing import Optional, List, Tuple, Dict
import psycopg2

# ============================================
# LIKE FUNCTIONS
# ============================================

def like_article(article_id: int, username: str) -> bool:
    """
    User likes an article.
    Returns True if successful, False if already liked or error.
    """
    try:
        conn, _ = connect()
        if not conn:
            print("❌ Database connection failed")
            return False
        
        cur = conn.cursor()
        
        # Insert like (will fail if already liked due to UNIQUE constraint)
        cur.execute("""
            INSERT INTO article_likes (article_id, username)
            VALUES (%s, %s)
            ON CONFLICT (article_id, username) DO NOTHING
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        success = result is not None
        if success:
            print(f"✅ {username} liked article {article_id}")
        else:
            print(f"ℹ️ {username} already liked article {article_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error liking article: {e}")
        return False


def unlike_article(article_id: int, username: str) -> bool:
    """
    User unlikes an article.
    Returns True if successful, False if not liked or error.
    """
    try:
        conn, _ = connect()
        if not conn:
            print("❌ Database connection failed")
            return False
        
        cur = conn.cursor()
        
        # Delete like
        cur.execute("""
            DELETE FROM article_likes
            WHERE article_id = %s AND username = %s
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        success = result is not None
        if success:
            print(f"✅ {username} unliked article {article_id}")
        else:
            print(f"ℹ️ {username} hasn't liked article {article_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error unliking article: {e}")
        return False


def is_article_liked(article_id: int, username: str) -> bool:
    """
    Check if user has liked an article.
    Returns True if liked, False otherwise.
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
    Get total likes for an article.
    Returns like count.
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
    Get list of articles liked by user.
    Returns: [(article_id, title, author, like_count, liked_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                n.id,
                n.title,
                n.author,
                n.like_count,
                to_char(al.liked_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as liked_at
            FROM article_likes al
            JOIN news n ON al.article_id = n.id
            WHERE al.username = %s
            AND n.status = 'published'
            ORDER BY al.liked_at DESC
            LIMIT %s;
        """, (username, limit))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting liked articles: {e}")
        return []


def get_article_likers(article_id: int, limit: int = 50) -> List[Tuple]:
    """
    Get list of users who liked an article.
    Returns: [(username, liked_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                username,
                to_char(liked_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as liked_at
            FROM article_likes
            WHERE article_id = %s
            ORDER BY liked_at DESC
            LIMIT %s;
        """, (article_id, limit))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting article likers: {e}")
        return []


# ============================================
# VIEW TRACKING
# ============================================

def track_article_view(article_id: int, username: Optional[str] = None, ip_address: str = "0.0.0.0") -> bool:
    """
    Track an article view.
    Returns True if successful.
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
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error tracking view: {e}")
        return False


def get_article_views(article_id: int) -> int:
    """
    Get total views for an article.
    Returns view count.
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
    Get trending articles based on views in last N days.
    Returns: [(article_id, title, author, views, likes, bookmarks, created_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute(f"""
            SELECT 
                n.id,
                n.title,
                n.author,
                n.views,
                n.like_count,
                n.bookmark_count,
                to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at
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


def get_popular_articles(limit: int = 10) -> List[Tuple]:
    """
    Get all-time popular articles by views.
    Returns: [(article_id, title, author, views, likes, bookmarks, created_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                n.id,
                n.title,
                n.author,
                n.views,
                n.like_count,
                n.bookmark_count,
                to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at
            FROM news n
            WHERE n.status = 'published'
            ORDER BY n.views DESC, n.like_count DESC
            LIMIT %s;
        """, (limit,))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting popular articles: {e}")
        return []


def get_most_liked_articles(limit: int = 10) -> List[Tuple]:
    """
    Get most liked articles.
    Returns: [(article_id, title, author, views, likes, bookmarks, created_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                n.id,
                n.title,
                n.author,
                n.views,
                n.like_count,
                n.bookmark_count,
                to_char(n.created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at
            FROM news n
            WHERE n.status = 'published'
            ORDER BY n.like_count DESC, n.views DESC
            LIMIT %s;
        """, (limit,))
        
        rows = cur.fetchall()
        conn.close()
        return rows
        
    except Exception as e:
        print(f"❌ Error getting most liked articles: {e}")
        return []


# ============================================
# BOOKMARK FUNCTIONS
# ============================================

def bookmark_article(article_id: int, username: str) -> bool:
    """
    User bookmarks an article.
    Returns True if successful, False if already bookmarked or error.
    """
    try:
        conn, _ = connect()
        if not conn:
            print("❌ Database connection failed")
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
        conn.commit()
        conn.close()
        
        success = result is not None
        if success:
            print(f"✅ {username} bookmarked article {article_id}")
        else:
            print(f"ℹ️ {username} already bookmarked article {article_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error bookmarking article: {e}")
        return False


def unbookmark_article(article_id: int, username: str) -> bool:
    """
    User removes bookmark from an article.
    Returns True if successful, False if not bookmarked or error.
    """
    try:
        conn, _ = connect()
        if not conn:
            print("❌ Database connection failed")
            return False
        
        cur = conn.cursor()
        
        # Delete bookmark
        cur.execute("""
            DELETE FROM article_bookmarks
            WHERE article_id = %s AND username = %s
            RETURNING id;
        """, (article_id, username))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        success = result is not None
        if success:
            print(f"✅ {username} unbookmarked article {article_id}")
        else:
            print(f"ℹ️ {username} hasn't bookmarked article {article_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error unbookmarking article: {e}")
        return False


def is_article_bookmarked(article_id: int, username: str) -> bool:
    """
    Check if user has bookmarked an article.
    Returns True if bookmarked, False otherwise.
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


def get_article_bookmarks_count(article_id: int) -> int:
    """
    Get total bookmarks for an article.
    Returns bookmark count.
    """
    try:
        conn, _ = connect()
        if not conn:
            return 0
        
        cur = conn.cursor()
        cur.execute("""
            SELECT bookmark_count FROM news WHERE id = %s;
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        return result[0] if result else 0
        
    except Exception as e:
        print(f"❌ Error getting bookmarks count: {e}")
        return 0


def get_user_bookmarked_articles(username: str, limit: int = 50) -> List[Tuple]:
    """
    Get list of articles bookmarked by user.
    Returns: [(article_id, title, author, bookmark_count, bookmarked_at), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                n.id,
                n.title,
                n.author,
                n.bookmark_count,
                to_char(ab.bookmarked_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as bookmarked_at
            FROM article_bookmarks ab
            JOIN news n ON ab.article_id = n.id
            WHERE ab.username = %s
            AND n.status = 'published'
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
# STATISTICS & ANALYTICS
# ============================================

def get_article_stats(article_id: int) -> Dict[str, int]:
    """
    Get all statistics for an article.
    Returns: {'views': int, 'likes': int, 'bookmarks': int}
    """
    try:
        conn, _ = connect()
        if not conn:
            return {'views': 0, 'likes': 0, 'bookmarks': 0}
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                COALESCE(views, 0) as views,
                COALESCE(like_count, 0) as likes,
                COALESCE(bookmark_count, 0) as bookmarks
            FROM news 
            WHERE id = %s;
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                'views': result[0],
                'likes': result[1],
                'bookmarks': result[2]
            }
        return {'views': 0, 'likes': 0, 'bookmarks': 0}
        
    except Exception as e:
        print(f"❌ Error getting article stats: {e}")
        return {'views': 0, 'likes': 0, 'bookmarks': 0}


def get_user_interaction_summary(username: str) -> Dict[str, int]:
    """
    Get summary of user's interactions.
    Returns: {'liked': int, 'bookmarked': int}
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


def get_penerbit_stats(author: str) -> Dict[str, int]:
    """
    Get statistics for a penerbit (author).
    Returns: {
        'total_articles': int,
        'total_views': int,
        'total_likes': int,
        'total_bookmarks': int,
        'avg_views': float,
        'avg_likes': float
    }
    """
    try:
        conn, _ = connect()
        if not conn:
            return {
                'total_articles': 0,
                'total_views': 0,
                'total_likes': 0,
                'total_bookmarks': 0,
                'avg_views': 0.0,
                'avg_likes': 0.0
            }
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                COUNT(*) as total_articles,
                COALESCE(SUM(views), 0) as total_views,
                COALESCE(SUM(like_count), 0) as total_likes,
                COALESCE(SUM(bookmark_count), 0) as total_bookmarks,
                COALESCE(AVG(views), 0) as avg_views,
                COALESCE(AVG(like_count), 0) as avg_likes
            FROM news
            WHERE author = %s AND status = 'published';
        """, (author,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                'total_articles': result[0],
                'total_views': result[1],
                'total_likes': result[2],
                'total_bookmarks': result[3],
                'avg_views': round(float(result[4]), 1),
                'avg_likes': round(float(result[5]), 1)
            }
        
        return {
            'total_articles': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_bookmarks': 0,
            'avg_views': 0.0,
            'avg_likes': 0.0
        }
        
    except Exception as e:
        print(f"❌ Error getting penerbit stats: {e}")
        return {
            'total_articles': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_bookmarks': 0,
            'avg_views': 0.0,
            'avg_likes': 0.0
        }


def get_engagement_rate(article_id: int) -> float:
    """
    Calculate engagement rate for an article.
    Engagement Rate = (Likes + Bookmarks) / Views * 100
    Returns: float (percentage)
    """
    stats = get_article_stats(article_id)
    
    if stats['views'] == 0:
        return 0.0
    
    engagement = stats['likes'] + stats['bookmarks']
    rate = (engagement / stats['views']) * 100
    return round(rate, 2)


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_article_full_info(article_id: int, username: Optional[str] = None) -> Optional[Dict]:
    """
    Get complete article information including stats and user interaction status.
    Returns: {
        'id': int,
        'title': str,
        'content': str,
        'author': str,
        'created_at': str,
        'views': int,
        'likes': int,
        'bookmarks': int,
        'is_liked': bool (if username provided),
        'is_bookmarked': bool (if username provided),
        'engagement_rate': float
    }
    """
    try:
        conn, _ = connect()
        if not conn:
            return None
        
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                id,
                title,
                content,
                author,
                to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI UTC') as created_at,
                COALESCE(views, 0) as views,
                COALESCE(like_count, 0) as likes,
                COALESCE(bookmark_count, 0) as bookmarks
            FROM news
            WHERE id = %s AND status = 'published';
        """, (article_id,))
        
        result = cur.fetchone()
        conn.close()
        
        if not result:
            return None
        
        article_info = {
            'id': result[0],
            'title': result[1],
            'content': result[2],
            'author': result[3],
            'created_at': result[4],
            'views': result[5],
            'likes': result[6],
            'bookmarks': result[7],
            'engagement_rate': get_engagement_rate(article_id)
        }
        
        # Add user interaction status if username provided
        if username:
            article_info['is_liked'] = is_article_liked(article_id, username)
            article_info['is_bookmarked'] = is_article_bookmarked(article_id, username)
        
        return article_info
        
    except Exception as e:
        print(f"❌ Error getting article info: {e}")
        return None


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("🧪 Testing app_db_interactions.py...\n")
    
    test_user = "testuser"
    test_article = 1
    
    print("=" * 50)
    print("LIKE FUNCTIONS TEST")
    print("=" * 50)
    
    print(f"\n1. Like article {test_article}...")
    success = like_article(test_article, test_user)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print(f"\n2. Check if liked...")
    is_liked = is_article_liked(test_article, test_user)
    print(f"   Is liked: {'✅ Yes' if is_liked else '❌ No'}")
    
    print(f"\n3. Get likes count...")
    count = get_article_likes_count(test_article)
    print(f"   Total likes: {count}")
    
    print(f"\n4. Unlike article...")
    success = unlike_article(test_article, test_user)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n" + "=" * 50)
    print("BOOKMARK FUNCTIONS TEST")
    print("=" * 50)
    
    print(f"\n5. Bookmark article {test_article}...")
    success = bookmark_article(test_article, test_user)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print(f"\n6. Check if bookmarked...")
    is_bookmarked = is_article_bookmarked(test_article, test_user)
    print(f"   Is bookmarked: {'✅ Yes' if is_bookmarked else '❌ No'}")
    
    print(f"\n7. Get bookmarks count...")
    count = get_article_bookmarks_count(test_article)
    print(f"   Total bookmarks: {count}")
    
    print("\n" + "=" * 50)
    print("VIEW TRACKING TEST")
    print("=" * 50)
    
    print(f"\n8. Track view for article {test_article}...")
    success = track_article_view(test_article, test_user)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print(f"\n9. Get views count...")
    views = get_article_views(test_article)
    print(f"   Total views: {views}")
    
    print("\n" + "=" * 50)
    print("STATISTICS TEST")
    print("=" * 50)
    
    print(f"\n10. Get article stats...")
    stats = get_article_stats(test_article)
    print(f"   Stats: {stats}")
    
    print(f"\n11. Get user summary...")
    summary = get_user_interaction_summary(test_user)
    print(f"   Summary: {summary}")
    
    print(f"\n12. Get trending articles...")
    trending = get_trending_articles(limit=5)
    print(f"   Found {len(trending)} trending articles")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 50)
