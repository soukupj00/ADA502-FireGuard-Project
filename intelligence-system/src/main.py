# intelligence-system/src/main.py
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import your FRCM logic here
# from frcm.fireriskmodel import compute_risk ...

DATABASE_URL = os.getenv("DATABASE_URL")


async def run_worker():
    print("Intelligence System started...")

    # 1. Setup DB Connection
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    while True:
        try:
            print("Fetching weather data from Open APIs...")
            # TODO: Add logic to fetch from MET.no using httpx

            print("Calculating Fire Risk...")
            # TODO: Run frcm logic

            print("Saving to Database...")
            async with AsyncSessionLocal() as session:
                # TODO: Insert results into DB
                # await session.commit()
                pass

            print("Cycle complete. Sleeping for 1 hour...")
            await asyncio.sleep(3600)  # Sleep for 1 hour

        except Exception as e:
            print(f"Error in worker cycle: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute


if __name__ == "__main__":
    asyncio.run(run_worker())