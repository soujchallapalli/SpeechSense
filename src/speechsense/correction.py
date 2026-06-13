"""Transcript correction using local Ollama."""

import requests

OLLAMA_MODEL = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"

CORRECTION_PROMPT = (
    "Correct this transcript. Fix spelling, punctuation, and capitalization "
    "to make it readable. Do not change the meaning or add new information. "
    "Return only the corrected sentence without explanation.\n\n"
    "Transcript: {text}"
)


def correct_with_ollama(
    text: str,
    model: str = OLLAMA_MODEL,
    url: str = OLLAMA_URL,
) -> str:
    """Send a transcript to a local Ollama model and return the corrected version."""
    prompt = CORRECTION_PROMPT.format(text=text)
    resp = requests.post(
        url,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    data: dict = resp.json()
    return str(data.get("response", "")).strip()


def correct_transcript(
    text: str,
    provider: str = "ollama",
    ollama_model: str = OLLAMA_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> str:
    """Correct a transcript using a local Ollama model.

    Args:
        text: The raw transcript text to correct.
        provider: The AI provider (only 'ollama' is supported).
        ollama_model: Ollama model name.
        ollama_url: Ollama server URL.

    Returns:
        The corrected transcript text.
    """
    if provider == "ollama":
        return correct_with_ollama(text, model=ollama_model, url=ollama_url)
    msg = f"Unknown provider: {provider!r}. Only 'ollama' is supported."
    raise ValueError(msg)
