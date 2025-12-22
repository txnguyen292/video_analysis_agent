from loguru import logger
from google import genai
from google.genai import types
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

class GeminiVideoClient:
    def __init__(self, api_key: str = None, model_id: str = "gemini-3-pro-preview"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment or passed as argument")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_id

    def upload_video(self, video_path: str, console=None):
        """Uploads a video to Gemini's Files API."""
        # Sanitize filename for display_name to avoid encoding issues in API headers
        # Some API headers or SDK internals may not handle Unicode display names correctly.
        display_name = re.sub(r'[^\x00-\x7F]+', '_', os.path.basename(video_path))
        
        import shutil
        import tempfile
        
        # Create a temporary file with a safe ASCII name
        # We use a suffix to preserve the file extension for MIME type detection
        suffix = os.path.splitext(video_path)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            safe_path = tmp_file.name
        
        try:
            # Copy the original content to the safe path
            logger.info(f"Copying video to temporary safe path: {safe_path}")
            shutil.copy2(video_path, safe_path)
            
            logger.info(f"Uploading video from safe path: {safe_path}")
            # Upload using the safe path, but keep the sanitized display name
            video_file = self.client.files.upload(
                file=safe_path,
                config={'display_name': display_name}
            )
        finally:
            # Clean up the temporary file
            if os.path.exists(safe_path):
                os.remove(safe_path)
        
        if console:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("[cyan]Gemini is processing video...", total=None)
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = self.client.files.get(name=video_file.name)
        else:
            while video_file.state.name == "PROCESSING":
                logger.info("Waiting for video to be processed...")
                time.sleep(2)
                video_file = self.client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(f"Video processing failed: {video_file.name}")

        logger.info(f"Video uploaded successfully: {video_file.uri}")
        return video_file

    def analyze_video(self, video_file, prompt: str):
        """Sends a prompt with video context to Gemini."""
        logger.info(f"Analyzing video with prompt: {prompt}")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[video_file, prompt],
        )
        return response
