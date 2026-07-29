import asyncio
import asyncpg

async def fix_permissions():
    passwords_to_try = ["Twe2?0op", "postgres", "password", "admin", ""]
    
    for pwd in passwords_to_try:
        try:
            print(f"Trying password: '{pwd}'")
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user="postgres",
                password=pwd,
                database="postgres"
            )
            print("SUCCESS! Connected as postgres!")
            
            await conn.execute("GRANT ALL ON SCHEMA public TO tsirina")
            await conn.execute("GRANT ALL PRIVILEGES ON DATABASE ice_cream_db TO tsirina")
            await conn.execute("ALTER USER tsirina WITH SUPERUSER")
            print("Permissions granted successfully!")
            
            await conn.close()
            return True
            
        except Exception as e:
            print(f"Failed with password: '{pwd}'")
    
    print("Could not connect as postgres with any password.")
    return False

asyncio.run(fix_permissions())
