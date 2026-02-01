"""Video analysis sub-agent for the ADK assistant."""

from __future__ import annotations

from personal_assistant import config
from personal_assistant.client import GeminiVideoClient
from personal_assistant_adk.utils import ChatError
from google.adk.agents import LlmAgent


def _get_video_model() -> str:
    """Resolve the Gemini video model id for the video sub-agent.

    Returns:
        Model id string used by the Gemini video client.

    Example:
        >>> _get_video_model()  # doctest: +SKIP
        'gemini-3-flash-preview'
    """

    return (
        config.get_env("ADK_VIDEO_MODEL", "gemini-3-flash-preview")
        or "gemini-3-flash-preview"
    )


def _get_video_client() -> GeminiVideoClient:
    """Build a Gemini video client for ADK tools.

    Returns:
        GeminiVideoClient configured with the video model.

    Example:
        >>> client = _get_video_client()  # doctest: +SKIP
        >>> client.model_id
        'gemini-3-flash-preview'
    """

    return GeminiVideoClient(model_id=_get_video_model())


def analyze_video(video_path: str, question: str) -> str:
    """Answer a question about a user-provided video file.

    Args:
        video_path: Path to the local video file.
        question: Question or instruction about the video content.

    Returns:
        The assistant's response text.

    Raises:
        ChatError: If the video cannot be processed or the API fails.

    Example:
        >>> analyze_video("/tmp/video.mp4", "Summarize the video")  # doctest: +SKIP
        'Summary text...'
    """

    if not video_path:
        raise ValueError("video_path is required")
    if not question:
        raise ValueError("question is required")

    try:
        client = _get_video_client()
        video_file = client.upload_video(video_path)
        response = client.analyze_video(video_file, question)
    except Exception as exc:  # noqa: BLE001 - surface as ChatError for UI
        raise ChatError("Video analysis failed. Please try again.") from exc

    return getattr(response, "text", "") or ""


def build_video_agent() -> LlmAgent:
    """Build the video sub-agent used by the personal assistant.

    Returns:
        LlmAgent configured to call the Gemini video tool.

    Example:
        >>> agent = build_video_agent()
        >>> agent.name
        'video_assistant'
    """

    return LlmAgent(
        name="video_assistant",
        description="Specialist for answering questions about user-supplied videos.",
        instruction=(
            "You are a video analysis specialist. "
            "When given a video file path, call analyze_video with the path and the user's question. "
            "Return the tool output verbatim."
        ),
        tools=[analyze_video],
    )
