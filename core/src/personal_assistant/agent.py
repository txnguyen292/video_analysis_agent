from typing import Any

from personal_assistant.client import GeminiVideoClient


class VideoAgent:
    def __init__(self, client: GeminiVideoClient) -> None:
        self.client = client

    def get_summary(self, video_file: Any) -> Any:
        """Generates a high-level summary of the video content."""
        prompt = "Provide a concise but comprehensive summary of this video. Highlight the key events and their timestamps."
        return self.client.analyze_video(video_file, prompt)

    def ask_question(self, video_file: Any, question: str) -> Any:
        """Answers a specific question about the video content."""
        prompt = (
            f"Based on this video, please answer the following question: {question}"
        )
        return self.client.analyze_video(video_file, prompt)

    def detect_events(self, video_file: Any) -> Any:
        """Detects specific events or anomalies in the video."""
        prompt = "Identify and list all significant events or actions in this video with their corresponding timestamps. Format the output as a bulleted list."
        return self.client.analyze_video(video_file, prompt)

    def transcribe_and_diarize(self, video_file: Any) -> Any:
        """Generates a diarized transcript of the video."""
        prompt = (
            "Transcribe the audio from this video. "
            "Identify different speakers and label them accordingly. "
            "Format the output strictly as followed: '[timestamp] Speaker: <content>'. "
            "For example: '[00:15] Speaker 1: Hello world.'"
        )
        return self.client.analyze_video(video_file, prompt)
