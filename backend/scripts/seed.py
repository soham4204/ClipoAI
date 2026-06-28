"""
Seed Database with Initial Data.
"""
import asyncio
import os
import sys

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import async_session_factory
from app.models import Clip, Job, User, Video
from app.core.security import get_password_hash


async def seed() -> None:
    """Insert initial seed data."""
    async with async_session_factory() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == "admin@clipo.ai"))
        existing_user = result.scalars().first()

        if existing_user:
            print("Database already seeded.")
            return

        print("Seeding database...")
        
        # 1. Create Admin User
        admin_user = User(
            email="admin@clipo.ai",
            hashed_password=get_password_hash("admin123"),
            role="admin",
        )
        session.add(admin_user)
        await session.flush()  # To get admin_user.id

        # 2. Create sample video
        sample_video = Video(
            user_id=admin_user.id,
            title="Introduction to LangGraph",
            source_type="youtube",
            source_url="https://youtube.com/watch?v=sample",
            status="completed",
        )
        session.add(sample_video)
        await session.flush()

        # 3. Create sample clip
        sample_clip = Clip(
            video_id=sample_video.id,
            title="What is LangGraph?",
            start_time_sec=10.5,
            end_time_sec=45.2,
            viral_score=0.92,
            status="generated",
        )
        session.add(sample_clip)

        # 4. Create sample job
        sample_job = Job(
            video_id=sample_video.id,
            type="transcription",
            status="completed",
        )
        session.add(sample_job)

        # Commit all changes
        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
