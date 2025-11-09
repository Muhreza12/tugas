# run_migration.py - Railway Migration Runner
"""
Script untuk run migration Phase 1 di Railway database
Ganti credentials sesuai dengan Railway credentials kamu
"""

import psycopg2
import sys

# ============================================
# CONFIGURATION - GANTI DENGAN DATA KAMU!
# ============================================

# Dari Railway Credentials tab:
DB_HOST = "containers-us-west-xxx.railway.app"  # Ganti dengan host kamu
DB_PORT = "5432"                                # Biasanya 5432
DB_NAME = "railway"                             # Biasanya "railway"
DB_USER = "postgres"                            # Biasanya "postgres"
DB_PASSWORD = "WuZnoaOPPcCPpsPQcpJZdiswoenTjoXE"  # Password kamu

# Atau pakai DATABASE_URL langsung (recommended):
# DATABASE_URL = "postgresql://postgres:WuZnoaOPPcCPpsPQcpJZdiswoenTjoXE@containers-us-west-xxx.railway.app:5432/railway"

# ============================================
# SCRIPT - JANGAN UBAH DIBAWAH INI
# ============================================

def run_migration():
    """Run the Phase 1 migration script"""
    
    print("=" * 60)
    print("🚀 CRYPTO INSIGHT - PHASE 1 MIGRATION")
    print("=" * 60)
    print()
    
    # Read migration file
    print("📖 Step 1: Reading migration file...")
    try:
        with open('migration_phase1.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        print("   ✅ Migration file loaded successfully")
        print(f"   📄 File size: {len(sql)} characters")
    except FileNotFoundError:
        print("   ❌ ERROR: File 'migration_phase1.sql' not found!")
        print("   💡 Make sure migration_phase1.sql is in the same folder")
        return False
    except Exception as e:
        print(f"   ❌ ERROR reading file: {e}")
        return False
    
    print()
    
    # Build connection string
    print("🔌 Step 2: Connecting to database...")
    try:
        # Try DATABASE_URL first if it's defined
        if 'DATABASE_URL' in globals():
            conn_string = DATABASE_URL
        else:
            conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        print(f"   🔗 Host: {DB_HOST}")
        print(f"   👤 User: {DB_USER}")
        print(f"   🗄️  Database: {DB_NAME}")
        
        conn = psycopg2.connect(conn_string, sslmode='require')
        print("   ✅ Connected successfully!")
    except psycopg2.OperationalError as e:
        print(f"   ❌ CONNECTION FAILED!")
        print(f"   💡 Error: {e}")
        print()
        print("   🔧 Troubleshooting:")
        print("   1. Check if host, port, username, password are correct")
        print("   2. Check if Railway database is running")
        print("   3. Check internet connection")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print()
    
    # Run migration
    print("⚙️  Step 3: Running migration script...")
    try:
        cur = conn.cursor()
        
        # Execute the migration
        print("   🔄 Executing SQL commands...")
        cur.execute(sql)
        
        # Commit changes
        print("   💾 Committing changes...")
        conn.commit()
        
        print("   ✅ Migration executed successfully!")
    except psycopg2.Error as e:
        print(f"   ❌ SQL ERROR!")
        print(f"   💡 Error: {e}")
        conn.rollback()
        conn.close()
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        conn.rollback()
        conn.close()
        return False
    
    print()
    
    # Verify tables created
    print("🔍 Step 4: Verifying migration...")
    try:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('article_likes', 'article_bookmarks', 'article_views')
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        if len(tables) == 3:
            print("   ✅ All tables created successfully:")
            for table in tables:
                print(f"      • {table[0]}")
        else:
            print(f"   ⚠️  Warning: Expected 3 tables, found {len(tables)}")
            for table in tables:
                print(f"      • {table[0]}")
        
        # Check columns added to news table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'news' 
            AND column_name IN ('views', 'like_count', 'bookmark_count')
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        
        if len(columns) == 3:
            print("   ✅ All columns added to news table:")
            for col in columns:
                print(f"      • {col[0]}")
        else:
            print(f"   ⚠️  Warning: Expected 3 columns, found {len(columns)}")
        
        # Get counts
        cur.execute("SELECT COUNT(*) FROM article_likes")
        likes_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM article_bookmarks")
        bookmarks_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM article_views")
        views_count = cur.fetchone()[0]
        
        print()
        print("   📊 Current data:")
        print(f"      • Likes: {likes_count}")
        print(f"      • Bookmarks: {bookmarks_count}")
        print(f"      • Views: {views_count}")
        
    except Exception as e:
        print(f"   ⚠️  Verification warning: {e}")
    
    # Close connection
    conn.close()
    
    print()
    print("=" * 60)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✅ Next steps:")
    print("   1. Copy Python files to project folder")
    print("   2. Run: python app_db_interactions.py")
    print("   3. Run: python main.py")
    print()
    
    return True


if __name__ == "__main__":
    print()
    success = run_migration()
    print()
    
    if success:
        print("🎊 All done! Your database is ready for Phase 1 features!")
        sys.exit(0)
    else:
        print("❌ Migration failed. Please check the errors above.")
        sys.exit(1)
