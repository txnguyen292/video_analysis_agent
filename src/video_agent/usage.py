from dataclasses import dataclass


@dataclass
class UsageStats:
    prompt_token_count: int = 0
    candidates_token_count: int = 0
    total_token_count: int = 0
    estimated_cost: float = 0.0
    currency: str = "USD"


class UsageTracker:
    # Pricing per 1 million tokens
    PRICING = {
        "gemini-3-pro-preview": {
            "input": 2.00,
            "output": 12.00,
        },
        "gemini-1.5-pro": {
            "input": 1.25,
            "output": 5.00,
        },
        "gemini-1.5-flash": {
            "input": 0.075,
            "output": 0.30,
        },
        # Fallback/Aliases
        "gemini-3-pro": {
            "input": 2.00,
            "output": 12.00,
        },
        "gemini-3-flash": {  # Placeholder for 3-flash if it exists/is used
            "input": 0.075,
            "output": 0.30,
        },
    }

    @staticmethod
    def calculate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        # Normalize model_id to lower case
        model_id = model_id.lower()

        # Simple flexible matching logic
        pricing = None
        for key in UsageTracker.PRICING:
            if key in model_id:
                pricing = UsageTracker.PRICING[key]
                break

        if not pricing:
            # Default to a safe fallback or 0 if unknown
            # Assuming 1.5 Pro pricing if unknown as a reasonable estimate
            pricing = UsageTracker.PRICING["gemini-1.5-pro"]

        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    @staticmethod
    def extract_usage(response, model_id: str) -> UsageStats:
        """
        Extracts usage metadata from a Gemini API response object.
        """
        usage_metadata = getattr(response, "usage_metadata", None)

        if not usage_metadata:
            return UsageStats()

        prompt_tokens = usage_metadata.prompt_token_count or 0
        candidates_tokens = usage_metadata.candidates_token_count or 0
        total_tokens = usage_metadata.total_token_count or 0

        cost = UsageTracker.calculate_cost(model_id, prompt_tokens, candidates_tokens)

        return UsageStats(
            prompt_token_count=prompt_tokens,
            candidates_token_count=candidates_tokens,
            total_token_count=total_tokens,
            estimated_cost=cost,
        )
