from postgreslite import PostgresLite


# Create database (or use existing one)
db = PostgresLite("database.db").connect()

# Create tables
print(db.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY
    );
"""))

print(db.execute("""
    CREATE TABLE IF NOT EXISTS Templates (
        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT NOT NULL
    );
"""))

print(db.execute("""
    CREATE TABLE IF NOT EXISTS Basic (
        -- DB information
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        guild_id TEXT,
        
        -- Basic information
        character_name TEXT NOT NULL,
        age TEXT,
        gender TEXT,
        species TEXT,
        description TEXT,
        
        -- Embed details
        picture_url TEXT,
        color TEXT,
        
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    );
"""))

# Suggestions
print(db.execute("""
    CREATE TABLE IF NOT EXISTS suggestion(
        id INTEGER PRIMARY KEY,
        user_id BIGINT,
        guild_id BIGINT,
        suggestion TEXT,
        votes INTEGER DEFAULT 0
    )
"""))

print("Initial database setup complete!")

# Create table for DnD characters
print(db.execute("""
    CREATE TABLE IF NOT EXISTS DnDCharacters (
        -- DB information
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        guild_id TEXT,
        
        -- Basic information
        character_name TEXT NOT NULL,
        age TEXT,
        gender TEXT,
        species TEXT,
        description TEXT,
        
        -- Class information
        lvl TEXT,
        class TEXT,
        subclass TEXT,
        weapon TEXT,
        alignment TEXT,
        
        -- Ability Scores
        strength TEXT,
        dexterity TEXT,
        constitution TEXT,
        intelligence TEXT,
        wisdom TEXT,
        charisma TEXT,
        
        -- Ability Modifiers
        str_mod TEXT,
        dex_mod TEXT,
        con_mod TEXT,
        int_mod TEXT,
        wis_mod TEXT,
        cha_mod TEXT,

        -- Embed details
        picture_url TEXT,
        color TEXT,    

        FOREIGN KEY (user_id) REFERENCES Users(user_id)

    )
"""))

db.execute("INSERT OR IGNORE INTO Templates (template_name) VALUES ('Basic');")
db.execute("INSERT OR IGNORE INTO Templates (template_name) VALUES ('DnDCharacters');")
print("Additional Templates added!")
