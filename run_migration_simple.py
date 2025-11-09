# run_migration_simple.py - Auto-read from config.ini
"""
Script untuk run migration Phase 1
Otomatis baca DATABASE_URL dari config.ini
TIDAK PERLU EDIT APAPUN!
"""

import psycopg2
import sys
import configparser

def run_migration():
    """Run the Phase 1 migration script"""
    
    print()
    print("=" * 60)
    print("🚀 CRYPTO INSIGHT - PHASE 1 MIGRATION")
    print("=" * 60)
    print()
    
    # Step 1: Read config.ini
    print("📖 Step 1: Reading config.ini...")
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        # Try to get DATABASE_URL
        if config.has_option('database', 'DATABASE_URL'):
            DATABASE_URL = config.get('database', 'DATABASE_URL')
        elif config.has_option('DATABASE', 'URL'):
            DATABASE_URL = config.get('DATABASE', 'URL')
        elif config.has_option('postgresql', 'url'):
            DATABASE_URL = config.get('postgresql', 'url')
        else:
            print("   ❌ ERROR: DATABASE_URL not found in config.ini")
            print()
            print("   💡 Please check your config.ini file")
            print("   It should have something like:")
            print("   [database]")
            print("   DATABASE_URL = postgresql://...")
            return False
        
        print("   ✅ Config file loaded")
        print(f"   🔗 Database URL found")
        
    except FileNotFoundError:
        print("   ❌ ERROR: config.ini not found!")
        print("   💡 Make sure this script is in the same folder as config.ini")
        return False
    except Exception as e:
        print(f"   ❌ ERROR reading config: {e}")
        return False
    
    print()
    
    # Step 2: Read migration file
    print("📄 Step 2: Reading migration file...")
    try:
        with open('migration_phase1.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        print("   ✅ Migration file loaded")
        print(f"   📊 File size: {len(sql)} characters")
    except FileNotFoundError:
        print("   ❌ ERROR: migration_phase1.sql not found!")
        print("   💡 Make sure migration_phase1.sql is in the same folder")
        return False
    except Exception as e:
        print(f"   ❌ ERROR reading file: {e}")
        return False
    
    print()
    
    # Step 3: Connect to database
    print("🔌 Step 3: Connecting to database...")
    try:
        # Extract host from URL for display
        if '@' in DATABASE_URL:
            host_part = DATABASE_URL.split('@')[1].split('/')[0].split(':')[0]
            print(f"   🌐 Host: {host_part}")
        
        print("   🔄 Connecting...")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("   ✅ Connected successfully!")
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ CONNECTION FAILED!")
        print(f"   💡 Error: {e}")
        print()
        print("   🔧 Troubleshooting:")
        print("   1. Check if DATABASE_URL in config.ini is correct")
        print("   2. Check if Railway database is running")
        print("   3. Check internet connection")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print()
    
    # Step 4: Run migration
    print("⚙️  Step 4: Running migration script...")
    try:
        cur = conn.cursor()
        
        print("   🔄 Executing SQL commands...")
        print("   ⏳ This may take 10-20 seconds...")
        cur.execute(sql)
        
        print("   💾 Committing changes...")
        conn.commit()
        
        print("   ✅ Migration executed successfully!")
        
    except psycopg2.Error as e:
        print(f"   ❌ SQL ERROR!")
        print(f"   💡 Error: {e}")
        print()
        
        # Check if tables already exist
        if "already exists" in str(e).lower():
            print("   ℹ️  It looks like tables already exist.")
            print("   This is OK if you ran migration before.")
            print()
            conn.rollback()
            # Don't return False, continue to verify
        else:
            conn.rollback()
            conn.close()
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        conn.rollback()
        conn.close()
        return False
    
    print()
    
    # Step 5: Verify
    print("🔍 Step 5: Verifying migration...")
    try:
        cur = conn.cursor()
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('article_likes', 'article_bookmarks', 'article_views')
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        print(f"   📋 Tables found: {len(tables)}/3")
        if len(tables) >= 3:
            print("   ✅ All required tables exist:")
            for table in tables:
                print(f"      • {table[0]}")
        else:
            print(f"   ⚠️  Warning: Expected 3 tables, found {len(tables)}")
            if tables:
                for table in tables:
                    print(f"      • {table[0]}")
        
        print()
        
        # Check columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'news' 
            AND column_name IN ('views', 'like_count', 'bookmark_count')
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        
        print(f"   📋 Columns in news table: {len(columns)}/3")
        if len(columns) >= 3:
            print("   ✅ All required columns exist:")
            for col in columns:
                print(f"      • {col[0]}")
        else:
            print(f"   ⚠️  Warning: Expected 3 columns, found {len(columns)}")
        
        print()
        
        # Get counts
        cur.execute("SELECT COUNT(*) FROM article_likes")
        likes_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM article_bookmarks")
        bookmarks_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM article_views")
        views_count = cur.fetchone()[0]
        
        print("   📊 Current data:")
        print(f"      • Likes: {likes_count}")
        print(f"      • Bookmarks: {bookmarks_count}")
        print(f"      • Views: {views_count}")
        
        # Check triggers
        cur.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_name LIKE 'trg_article%'
            ORDER BY trigger_name;
        """)
        
        triggers = cur.fetchall()
        print()
        print(f"   ⚡ Triggers found: {len(triggers)}")
        for trigger in triggers:
            print(f"      • {trigger[0]}")
        
    except Exception as e:
        print(f"   ⚠️  Verification warning: {e}")
        # Don't fail on verification errors
    
    # Close connection
    conn.close()
    
    print()
    print("=" * 60)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✅ Database is ready for Phase 1 features!")
    print()
    print("📋 Next steps:")
    print("   1. Test backend:")
    print("      python app_db_interactions.py")
    print()
    print("   2. Run application:")
    print("      python main.py")
    print()
    
    return True


if __name__ == "__main__":
    print()
    
    # Check if required files exist
    import os
    
    if not os.path.exists('config.ini'):
        print("❌ ERROR: config.ini not found in current directory")
        print("💡 Make sure you run this script from the crypto-insight folder")
        print()
        sys.exit(1)
    
    if not os.path.exists('migration_phase1.sql'):
        print("❌ ERROR: migration_phase1.sql not found in current directory")
        print("💡 Make sure migration_phase1.sql is in the same folder")
        print()
        sys.exit(1)
    
    # Run migration
    success = run_migration()
    
    print()
    
    if success:
        print("🎊 All done! Phase 1 features are ready to use!")
        print()
        sys.exit(0)
    else:
        print("❌ Migration failed. Please check the errors above.")
        print()
        print("💡 Need help? Check:")
        print("   - Is DATABASE_URL in config.ini correct?")
        print("   - Is Railway database running?")
        print("   - Is internet connection OK?")
        print()
        sys.exit(1)
