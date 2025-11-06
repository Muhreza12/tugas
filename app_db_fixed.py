# app_db_fixed.py — Railway PostgreSQL helpers with IMPROVED ERROR HANDLING
import os, sys, configparser, hashlib
from typing import Optional, Tuple, List
import psycopg2
from psycopg2 import OperationalError, DatabaseError

# ---------- Config ----------
def _app_dir() -> str:
    """Get application directory (works for both script and frozen exe)"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _load_database_url() -> Optional[str]:
    """Load DATABASE_URL from config.ini, environment, or .env file"""
    # 1) config.ini (with BOM handling)
    ini = os.path.join(_app_dir(), "config.ini")
    if os.path.exists(ini):
        try:
            cfg = configparser.ConfigParser()
            cfg.read(ini, encoding="utf-8-sig")
            if "server" in cfg and "DATABASE_URL" in cfg["server"]:
                url = cfg["server"]["DATABASE_URL"].strip()
                # Validate URL format
                if url and url.startswith("postgresql://"):
                    return url
                else:
                    print("⚠️ Invalid DATABASE_URL format in config.ini")
        except Exception as e:
            print(f"⚠️ Error reading config.ini: {e}")

    # 2) Environment variable
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("postgresql://"):
        return url

    # 3) .env file (optional)
    envp = os.path.join(_app_dir(), ".env")
    if os.path.exists(envp):
        try:
            with open(envp, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("DATABASE_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception as e:
            print(f"⚠️ Error reading .env: {e}")
    
    return None

DATABASE_URL: Optional[str] = _load_database_url()

# ---------- Core DB with Error Handling ----------
def connect() -> Tuple[Optional[psycopg2.extensions.connection], Optional[str]]:
    """
    Connect to PostgreSQL database with comprehensive error handling.
    Returns: (connection, db_type) or (None, None) on failure
    """
    if not DATABASE_URL:
        print("❌ DATABASE_URL tidak ditemukan!")
        print("   Pastikan file config.ini ada dan berisi DATABASE_URL yang valid.")
        print("   Atau set environment variable DATABASE_URL.")
        return None, None
    
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=10)
        return conn, "postgres"
    except OperationalError as e:
        print(f"❌ Database connection failed (Operational Error):")
        print(f"   {str(e)}")
        print("\n   Possible causes:")
        print("   - Internet connection issue")
        print("   - Wrong credentials in DATABASE_URL")
        print("   - Database server is down")
        print("   - Firewall blocking connection")
        return None, None
    except DatabaseError as e:
        print(f"❌ Database error: {str(e)}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error connecting to database: {str(e)}")
        return None, None

def setup_database() -> bool:
    """
    Setup database tables. Returns True if successful, False otherwise.
    """
    conn, _ = connect()
    if not conn:
        print("✖ Cannot setup database: Connection failed")
        return False
    
    try:
        cur = conn.cursor()

        # Tabel users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                role VARCHAR(50) DEFAULT 'user'
            );
        """)

        # Tabel presence
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
              id SERIAL PRIMARY KEY,
              username VARCHAR(100) NOT NULL,
              started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              last_seen  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              status     VARCHAR(16) NOT NULL DEFAULT 'online'
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_username ON user_sessions(username);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_last_seen ON user_sessions(last_seen);")

        # Tabel berita (khusus role 'penerbit')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
              id SERIAL PRIMARY KEY,
              title VARCHAR(200) NOT NULL,
              content TEXT NOT NULL,
              author VARCHAR(100) NOT NULL,
              status VARCHAR(20) NOT NULL DEFAULT 'draft',
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_author ON news(author);")

        conn.commit()
        conn.close()
        print("✅ Database setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database tables: {str(e)}")
        if conn:
            conn.close()
        return False

# ---------- Users with Error Handling ----------
def user_exists(username: str) -> bool:
    """Check if user exists in database. Returns False on error."""
    if not username:
        return False
        
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username=%s", (username,))
        r = cur.fetchone()
        conn.close()
        return bool(r)
    except Exception as e:
        print(f"❌ Error checking user existence: {str(e)}")
        return False

def create_user(username: str, password: str, role: str = "user") -> bool:
    """Create new user. Returns True if successful."""
    if not username or not password:
        print("❌ Username and password are required")
        return False
        
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s,%s,%s) "
            "ON CONFLICT (username) DO NOTHING",
            (username, hashed, role),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return False

def verify_user(username: str, password: str) -> Optional[str]:
    """Verify user credentials. Returns role if valid, None otherwise."""
    if not username or not password:
        return None
        
    try:
        conn, _ = connect()
        if not conn:
            return None
        cur = conn.cursor()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, hashed))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"❌ Error verifying user: {str(e)}")
        return None

# ---------- Presence (online tracking) ----------
ONLINE_WINDOW_SECONDS = 45

def start_session(username: str) -> Optional[int]:
    """Start user session. Returns session_id or None on error."""
    if not username:
        return None
        
    try:
        conn, _ = connect()
        if not conn:
            return None
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user_sessions (username, status) VALUES (%s, 'online') RETURNING id;",
            (username,)
        )
        sid = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return sid
    except Exception as e:
        print(f"❌ Error starting session: {str(e)}")
        return None

def heartbeat(session_id: int) -> bool:
    """Update session heartbeat. Returns True if successful."""
    if not session_id:
        return False
        
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        cur.execute("UPDATE user_sessions SET last_seen = NOW() WHERE id = %s;", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Heartbeat failed: {str(e)}")
        return False

def end_session(session_id: int) -> bool:
    """End user session. Returns True if successful."""
    if not session_id:
        return False
        
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        cur.execute("UPDATE user_sessions SET status='offline', last_seen=NOW() WHERE id=%s;", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ End session failed: {str(e)}")
        return False

def latest_presence_per_user() -> List[tuple]:
    """
    Get latest presence for all users.
    Returns: [(username, role, is_online, last_seen_utc), ...]
    """
    try:
        conn, _ = connect()
        if not conn:
            return []
        cur = conn.cursor()
        cur.execute(f"""
            WITH latest AS (
                SELECT username, MAX(last_seen) AS ls
                FROM user_sessions
                GROUP BY username
            )
            SELECT l.username,
                   COALESCE(u.role, 'user') AS role,
                   EXISTS(
                     SELECT 1 FROM user_sessions s
                     WHERE s.username = l.username
                       AND s.last_seen = l.ls
                       AND s.status = 'online'
                       AND s.last_seen > NOW() - INTERVAL '{ONLINE_WINDOW_SECONDS} seconds'
                   ) AS is_online,
                   to_char(l.ls AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS UTC') AS last_seen_utc
            FROM latest l
            LEFT JOIN users u ON u.username = l.username
            ORDER BY l.username;
        """)
        rows = cur.fetchall()
        conn.close()
        return [(r[0], r[1], bool(r[2]), r[3]) for r in rows]
    except Exception as e:
        print(f"⚠️ Error fetching presence: {str(e)}")
        return []

# ---------- NEWS (untuk role 'penerbit') ----------
def create_news(author: str, title: str, content: str, publish: bool = True) -> bool:
    """Create news article. Returns True if successful."""
    if not author or not title or not content:
        return False
        
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        status = 'published' if publish else 'draft'
        cur.execute(
            "INSERT INTO news (title, content, author, status) VALUES (%s, %s, %s, %s);",
            (title, content, author, status)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating news: {str(e)}")
        return False

def list_my_news(author: str, limit: int = 50) -> List[tuple]:
    """Get news articles by author."""
    if not author:
        return []
        
    try:
        conn, _ = connect()
        if not conn:
            return []
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, status, to_char(created_at AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI UTC')
            FROM news
            WHERE author=%s
            ORDER BY created_at DESC
            LIMIT %s;
        """, (author, limit))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"⚠️ Error fetching news: {str(e)}")
        return []

def list_published_news(limit: int = 50) -> List[tuple]:
    """Get published news feed."""
    try:
        conn, _ = connect()
        if not conn:
            return []
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, author, to_char(created_at AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI UTC')
            FROM news
            WHERE status='published'
            ORDER BY created_at DESC
            LIMIT %s;
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"⚠️ Error fetching published news: {str(e)}")
        return []

# ---------- Health Check ----------
def health_check() -> bool:
    """Check if database connection is healthy."""
    try:
        conn, _ = connect()
        if not conn:
            return False
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        conn.close()
        return result is not None
    except:
        return False
