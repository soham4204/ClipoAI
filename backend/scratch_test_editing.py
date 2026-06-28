import asyncio
import os
import json
import urllib.request
import urllib.error
import urllib.parse
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
import sys
sys.path.append('/app')

from app.database import async_session_factory
from app.models import Video, Clip, User
from app.services.storage import storage_service

base_url = 'http://localhost:8080/api'
login_data = urllib.parse.urlencode({
    'username': 'admin@clipo.ai',
    'password': 'admin123'
}).encode('ascii')

async def setup_test_data():
    async with async_session_factory() as session:
        # Get admin user
        from sqlalchemy.future import select
        result = await session.execute(select(User).where(User.email == "admin@clipo.ai"))
        user = result.scalars().first()
        
        # 1. Upload the generated /tmp/sample.mp4 to MinIO
        video_id = uuid4()
        storage_path = f"raw-videos/{video_id}.mp4"
        
        print(f"Uploading /tmp/sample.mp4 to raw-videos/{storage_path}")
        try:
            storage_service.client.fput_object(
                bucket_name="clipoai-videos",
                object_name=storage_path,
                file_path="/tmp/sample.mp4",
                content_type="video/mp4"
            )
        except Exception as e:
            print(f"Failed to upload: {e}")
            return None, None
            
        # 2. Insert Video record
        video = Video(
            id=video_id,
            user_id=user.id,
            title="Synthetic Test Video",
            source_type="local",
            storage_path=f"clipoai-videos/{storage_path}", # Using bucket/object format
            status="completed"
        )
        session.add(video)
        
        # 3. Insert Clip record (from 2.0 to 6.0 seconds)
        clip = Clip(
            id=uuid4(),
            video_id=video.id,
            title="Best Part of Synthetic Video",
            start_time_sec=2.0,
            end_time_sec=6.0,
            viral_score=95,
            status="generated" # actually pre-generation status
        )
        session.add(clip)
        
        await session.commit()
        return video.id, clip.id

async def main():
    print('--- ClipoAI Backend Video Editing Test ---')
    
    # 0. Setup
    video_id, clip_id = await setup_test_data()
    if not clip_id:
        return
        
    print(f'[0] Injected fake video and clip (Video ID: {video_id}, Clip ID: {clip_id})')
    
    # 1. Login
    access_token = None
    try:
        req = urllib.request.Request(f'{base_url}/auth/login/access-token', data=login_data, method='POST')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            access_token = data.get('access_token')
            print(f'[1] Auth Login: 200 OK -> Token generated')
    except Exception as e:
        print(f'[1] Auth Login Failed: {e}')
        return

    # 2. Trigger Clip Generation
    print('[2] Triggering clip generation...')
    try:
        req = urllib.request.Request(f'{base_url}/clips/{clip_id}/generate', method='POST')
        req.add_header('Authorization', f'Bearer {access_token}')
        with urllib.request.urlopen(req) as response:
            job_data = json.loads(response.read())
            print(f'[2] Clip Generation Triggered: {response.getcode()} OK -> Job ID: {job_data.get("job_id")}')
    except urllib.error.HTTPError as e:
        print(f'[2] Generation Trigger Failed: HTTP {e.code}')
        print(e.read().decode())
        return
    except Exception as e:
        print(f'[2] Generation Trigger Failed: {e}')
        return
        
    print('[3] Waiting 10 seconds for background FFmpeg job to complete...')
    await asyncio.sleep(10)
    
    # 4. Check Clips
    async with async_session_factory() as session:
        clip = await session.get(Clip, clip_id)
        
        print(f'[4] Clip status in database: {clip.status}')
        print(f'    Storage Path: {clip.storage_path}')
        
        if clip.storage_path:
            # Try to stat the object in MinIO to confirm it exists
            bucket, obj = clip.storage_path.split('/', 1)
            try:
                stat = storage_service.client.stat_object(bucket, obj)
                print(f"    Verified in MinIO! Size: {stat.size} bytes")
            except Exception as e:
                print(f"    Object not found in MinIO: {e}")
    
if __name__ == '__main__':
    asyncio.run(main())
