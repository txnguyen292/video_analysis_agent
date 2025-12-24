import asyncio
from video_agent.main import get_agent, load_config
from video_agent.usage import UsageTracker
import time

class AgentHelper:
    def __init__(self):
        self.config = load_config()
        self.model_id = self.config.get("model", "gemini-3-pro")
        self.agent = None

    def _ensure_agent(self):
        if self.agent is None:
            self.agent = get_agent(self.model_id)

    async def analyze_video(self, video_path: str, task_type: str, query: str = None):
        """
        Runs the agent task in a separate thread to keep UI responsive.
        task_type: 'summarize', 'ask', 'events', 'transcribe'
        """
        def _run():
            start_time = time.perf_counter()
            self._ensure_agent()
            # Upload
            print(f"Uploading {video_path}...")
            video_file = self.agent.client.upload_video(video_path)
            
            # Process
            response = None
            if task_type == 'summarize':
                response = self.agent.get_summary(video_file)
            elif task_type == 'ask':
                response = self.agent.ask_question(video_file, query)
            elif task_type == 'events':
                response = self.agent.detect_events(video_file)
            elif task_type == 'transcribe':
                response = self.agent.transcribe_and_diarize(video_file)
                
            elapsed = time.perf_counter() - start_time
            stats = UsageTracker.extract_usage(response, self.model_id)
            return response.text, stats, elapsed

        return await asyncio.to_thread(_run)
