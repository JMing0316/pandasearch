"""Quick diagnostic script to test asyncpg connection and env loading."""
import asyncio
import os

async def diagnose():
    # 1. Show current working directory and .env existence
    print(f"CWD: {os.getcwd()}")
    env_path = os.path.join(os.getcwd(), ".env")
    print(f".env exists: {os.path.exists(env_path)}")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            print(".env contents:")
            for line in f:
                if line.strip() and not line.startswith("#"):
                    print(f"  {line.strip()}")

    # 2. Load Settings and show DATABASE_URL
    from pandasearch.config import Settings
    settings = Settings()
    raw_dsn = settings.DATABASE_URL
    print(f"\nRaw DATABASE_URL from Settings: {raw_dsn}")

    # 3. Normalize DSN for asyncpg
    dsn = raw_dsn.replace("postgresql+asyncpg://", "postgresql://", 1)
    print(f"Normalized DSN for asyncpg: {dsn}")

    # 4. Try direct connect first (no pool)
    import asyncpg
    print("\n--- Testing asyncpg.connect (single connection) ---")
    try:
        conn = await asyncpg.connect(dsn=dsn, ssl=False)
        result = await conn.fetch("SELECT 1 AS test")
        print(f"SUCCESS: {result}")
        await conn.close()
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

    # 5. Try create_pool
    print("\n--- Testing asyncpg.create_pool ---")
    try:
        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=2,
            command_timeout=60,
            ssl=False,
        )
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT 2 AS pool_test")
            print(f"SUCCESS: {result}")
        await pool.close()
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
