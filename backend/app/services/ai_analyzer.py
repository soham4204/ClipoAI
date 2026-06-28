import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

class ClipRecommendation(BaseModel):
    title: str = Field(description="A catchy, viral-style title for the clip")
    start_time_sec: float = Field(description="Start time of the clip in seconds")
    end_time_sec: float = Field(description="End time of the clip in seconds")
    viral_score: float = Field(description="Viral potential score from 1 to 100")
    reason: str = Field(description="Explanation of why this clip is highly engaging or viral")

class AnalyzerResponse(BaseModel):
    clips: list[ClipRecommendation]

class AIAnalyzerService:
    def __init__(self):
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY is not set. AI analysis will fail.")
        else:
            genai.configure(api_key=settings.gemini_api_key)
        
        # Using the latest 3.5 flash model as requested
        self.model = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            system_instruction=(
                "You are an elite short-form content strategist and viral producer. "
                "Your job is to analyze video transcripts and identify the absolute best segments "
                "(15 to 60 seconds long) that would go extremely viral on TikTok, YouTube Shorts, and Instagram Reels. "
                "Look for strong hooks, curiosity gaps, emotional peaks, humor, and high information density. "
                "Return exactly the structured JSON requested, containing the best clip recommendations."
            )
        )

    def format_transcript_with_timestamps(self, words_json: List[Dict[str, Any]]) -> str:
        """
        Groups words into 10-second chunks to give the LLM accurate timestamp context.
        """
        if not words_json:
            return ""
            
        chunks = []
        current_chunk_words = []
        current_chunk_start = 0.0
        
        for word_data in words_json:
            word = word_data.get("word", "").strip()
            start = word_data.get("start", 0.0)
            end = word_data.get("end", 0.0)
            
            if not current_chunk_words:
                current_chunk_start = start
                
            current_chunk_words.append(word)
            
            # Chunk every 10 seconds or at the very end
            if end - current_chunk_start >= 10.0 or word_data == words_json[-1]:
                chunk_text = " ".join(current_chunk_words)
                chunks.append(f"[{current_chunk_start:.2f}s -> {end:.2f}s] {chunk_text}")
                current_chunk_words = []
                
        return "\n".join(chunks)

    def analyze_transcript(self, transcript_text: str, words_json: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Analyzes the transcript and returns a list of clip recommendations.
        """
        logger.info("Starting AI content analysis via Gemini...")
        
        if not transcript_text or len(transcript_text.strip()) < 50:
             logger.warning("Transcript is too short or empty for analysis.")
             return []

        # Use words_json to provide timestamped text if available
        if words_json:
            formatted_text = self.format_transcript_with_timestamps(words_json)
        else:
            formatted_text = transcript_text

        prompt = f"Analyze the following timestamped video transcript. Identify up to 3 most viral segments. Use the timestamps provided in the brackets to accurately determine start and end times.\n\nTranscript:\n{formatted_text}"
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AnalyzerResponse
                )
            )
            
            result_json = json.loads(response.text)
            clips = result_json.get("clips", [])
            logger.info(f"Gemini analysis complete. Found {len(clips)} potential clips.")
            return clips
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {e}")
            raise
