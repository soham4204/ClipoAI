import asyncio
import json
import urllib.request
import urllib.error
import urllib.parse
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

# Import our backend components
import sys
import os
sys.path.append('/app')

from app.database import async_session_factory
from app.models import Video, Transcript, User

base_url = 'http://localhost:8080/api'
login_data = urllib.parse.urlencode({
    'username': 'admin@clipo.ai',
    'password': 'admin123'
}).encode('ascii')

fake_transcript_text = """
Hey everyone, today I'm going to tell you the craziest secret about how the algorithm actually works on TikTok and YouTube Shorts!
Most people think it's about getting likes, but it's not. The number one metric, the absolute king of all metrics, is retention graph flattening.
If you can keep people watching past the 3-second mark, your video will get pushed to ten times more people. 
And the trick to do that? Use an open loop in the first second. Ask a question but don't answer it until the end of the video!
Try this on your next post and watch your views explode. Drop a comment if you've seen this work for you!
"""

fake_words_json = [
    {"word": "Hey", "start": 0.0, "end": 0.5},
    {"word": "everyone", "start": 0.5, "end": 1.0},
    {"word": "today", "start": 1.0, "end": 1.5},
    {"word": "I'm", "start": 1.5, "end": 1.8},
    {"word": "going", "start": 1.8, "end": 2.0},
    {"word": "to", "start": 2.0, "end": 2.2},
    {"word": "tell", "start": 2.2, "end": 2.5},
    {"word": "you", "start": 2.5, "end": 2.7},
    {"word": "the", "start": 2.7, "end": 3.0},
    {"word": "craziest", "start": 3.0, "end": 3.5},
    {"word": "secret", "start": 3.5, "end": 4.0},
    {"word": "about", "start": 4.0, "end": 4.2},
    {"word": "how", "start": 4.2, "end": 4.5},
    {"word": "the", "start": 4.5, "end": 4.7},
    {"word": "algorithm", "start": 4.7, "end": 5.2},
    {"word": "actually", "start": 5.2, "end": 5.7},
    {"word": "works", "start": 5.7, "end": 6.0},
    
    {"word": "Most", "start": 6.5, "end": 7.0},
    {"word": "people", "start": 7.0, "end": 7.5},
    {"word": "think", "start": 7.5, "end": 7.8},
    {"word": "it's", "start": 7.8, "end": 8.0},
    {"word": "about", "start": 8.0, "end": 8.2},
    {"word": "getting", "start": 8.2, "end": 8.5},
    {"word": "likes", "start": 8.5, "end": 9.0},
    {"word": "but", "start": 9.0, "end": 9.2},
    {"word": "it's", "start": 9.2, "end": 9.5},
    {"word": "not", "start": 9.5, "end": 10.0},
    
    {"word": "The", "start": 10.5, "end": 10.7},
    {"word": "number", "start": 10.7, "end": 11.0},
    {"word": "one", "start": 11.0, "end": 11.2},
    {"word": "metric", "start": 11.2, "end": 11.7},
    {"word": "is", "start": 11.7, "end": 12.0},
    {"word": "retention", "start": 12.0, "end": 12.5},
    
    {"word": "Try", "start": 30.0, "end": 30.5},
    {"word": "this", "start": 30.5, "end": 31.0},
    {"word": "and", "start": 31.0, "end": 31.5},
    {"word": "watch", "start": 31.5, "end": 32.0},
    {"word": "your", "start": 32.0, "end": 32.2},
    {"word": "views", "start": 32.2, "end": 32.7},
    {"word": "explode", "start": 32.7, "end": 33.5},
]

async def inject_fake_data():
    async with async_session_factory() as session:
        # Get admin user
        from sqlalchemy.future import select
        result = await session.execute(select(User).where(User.email == "admin@clipo.ai"))
        user = result.scalars().first()
        
        # Create fake video
        video = Video(
            id=uuid4(),
            user_id=user.id,
            title="Fake Viral Video",
            source_type="local",
            status="completed"
        )
        session.add(video)
        
        # Create fake transcript
        transcript = Transcript(
            video_id=video.id,
            text=fake_transcript_text,
            words_json=fake_words_json,
            language="en"
        )
        session.add(transcript)
        await session.commit()
        return video.id

async def main():
    print('--- ClipoAI Backend Analysis Test ---')
    
    # 0. Inject data
    video_id = await inject_fake_data()
    print(f'[0] Injected fake video and transcript (Video ID: {video_id})')
    
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

    # 2. Trigger Analysis
    print('[2] Triggering analysis...')
    try:
        req = urllib.request.Request(f'{base_url}/analysis/{video_id}', method='POST')
        req.add_header('Authorization', f'Bearer {access_token}')
        with urllib.request.urlopen(req) as response:
            job_data = json.loads(response.read())
            print(f'[2] Analysis Triggered: {response.getcode()} OK -> Job ID: {job_data.get("job_id")}')
    except urllib.error.HTTPError as e:
        print(f'[2] Analysis Trigger Failed: HTTP {e.code}')
        print(e.read().decode())
        return
    except Exception as e:
        print(f'[2] Analysis Trigger Failed: {e}')
        return
        
    print('[3] Waiting 15 seconds for Gemini analysis job to complete...')
    await asyncio.sleep(15)
    
    # 4. Check Clips
    async with async_session_factory() as session:
        from sqlalchemy.future import select
        from app.models import Clip
        result = await session.execute(select(Clip).where(Clip.video_id == video_id))
        clips = result.scalars().all()
        
        print(f'[4] Found {len(clips)} generated clips in database:')
        for i, clip in enumerate(clips):
            print(f"  Clip {i+1}: {clip.title}")
            print(f"    Score: {clip.viral_score}")
            print(f"    Time: {clip.start_time_sec}s - {clip.end_time_sec}s")
    
if __name__ == '__main__':
    asyncio.run(main())
