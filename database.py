import aiosqlite
import asyncio

DB_NAME = "anime.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                joined_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Animelar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS animes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                title TEXT,
                description TEXT,
                genre TEXT,
                photo_id TEXT,
                video_id TEXT,
                views INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Qidiruvlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT,
                search_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()
    print("✅ Database tayyor!")

# ═══ FOYDALANUVCHI FUNKSIYALARI ═══

async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("""
                INSERT OR IGNORE INTO users 
                (user_id, username, full_name) 
                VALUES (?, ?, ?)
            """, (user_id, username, full_name))
            await db.commit()
        except:
            pass

async def get_users_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# ═══ ANIME FUNKSIYALARI ═══

async def add_anime(code, title, description, genre, photo_id, video_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO animes 
            (code, title, description, genre, photo_id, video_id, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (code, title, description, genre, photo_id, video_id, status))
        await db.commit()

async def get_anime_by_code(code):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes WHERE code = ?", (code,))
        return await cursor.fetchone()

async def get_anime_by_title(title):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes WHERE title LIKE ?", (f"%{title}%",))
        return await cursor.fetchall()

async def get_animes_by_genre(genre):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes WHERE genre LIKE ?", (f"%{genre}%",))
        return await cursor.fetchall()

async def get_latest_animes(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes ORDER BY created_date DESC LIMIT ?", (limit,))
        return await cursor.fetchall()

async def get_top_animes(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes ORDER BY views DESC LIMIT ?", (limit,))
        return await cursor.fetchall()

async def get_ongoing_animes():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM animes WHERE status = 'ongoing'")
        return await cursor.fetchall()

async def update_anime_views(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE animes SET views = views + 1 WHERE code = ?", (code,))
        await db.commit()

async def delete_anime(code):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM animes WHERE code = ?", (code,))
        await db.commit()

async def update_anime(code, title, description, genre, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE animes 
            SET title=?, description=?, genre=?, status=?
            WHERE code=?
        """, (title, description, genre, status, code))
        await db.commit()

async def get_animes_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM animes")
        row = await cursor.fetchone()
        return row[0]

async def add_search(user_id, query):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO searches (user_id, query) VALUES (?, ?)",
            (user_id, query))
        await db.commit()

async def get_searches_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM searches")
        row = await cursor.fetchone()
        return row[0]