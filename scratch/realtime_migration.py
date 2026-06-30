import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'web', '.env.local'))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found!")
    exit(1)

async def run_migration():
    print("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    
    # 1. Add tables to Supabase Realtime publication
    print("Adding tables to supabase_realtime publication...")
    await conn.execute("""
        -- Create publication if it doesn't exist (Supabase creates it by default, but just in case)
        CREATE PUBLICATION supabase_realtime IF NOT EXISTS;
        
        -- Add tables to the publication
        ALTER PUBLICATION supabase_realtime ADD TABLE digests_cache;
        ALTER PUBLICATION supabase_realtime ADD TABLE admin_commands;
    """)
    
    # 2. Create Postgres Notify Trigger for Python Bot
    print("Creating NOTIFY trigger for admin_commands...")
    await conn.execute("""
        CREATE OR REPLACE FUNCTION notify_admin_command()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.status = 'pending' THEN
                PERFORM pg_notify('admin_commands_channel', row_to_json(NEW)::text);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS admin_commands_notify_trigger ON admin_commands;
        
        CREATE TRIGGER admin_commands_notify_trigger
        AFTER INSERT ON admin_commands
        FOR EACH ROW
        EXECUTE FUNCTION notify_admin_command();
    """)
    
    print("Migration complete!")
    await conn.close()

asyncio.run(run_migration())
