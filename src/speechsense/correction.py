"""Transcript correction using AI providers (Gemini or Ollama)."""

import os

import requests

GEMINI_MODEL = "gemini-2.5-flash"
OLLAMA_MODEL = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"

CORRECTION_PROMPT = (
    "Correct this transcript. Fix spelling, punctuation, and capitalization "
    "to make it readable. Do not change the meaning or add new information. "
    "Return only the corrected sentence without explanation.\n\n"
    "Transcript: {text}"
)


def correct_with_gemini(
    text: str,
    api_key: str | None = None,
    model: str = GEMINI_MODEL,
) -> str:
    """Send a transcript to Gemini and return the corrected version."""
    from google import genai

    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        msg = "GEMINI_API_KEY is not set"
        raise ValueError(msg)

    client = genai.Client(api_key=key)
    prompt = CORRECTION_PROMPT.format(text=text)
    response = client.models.generate_content(model=model, contents=prompt)
    corrected = response.text or ""
    return corrected.strip()


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
    provider: str = "gemini",
    gemini_api_key: str | None = None,
    gemini_model: str = GEMINI_MODEL,
    ollama_model: str = OLLAMA_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> str:
    """Correct a transcript using the specified AI provider.

    Args:
        text: The raw transcript text to correct.
        provider: Either 'gemini' or 'ollama'.
        gemini_api_key: Gemini API key (defaults to GEMINI_API_KEY env var).
        gemini_model: Gemini model name.
        ollama_model: Ollama model name.
        ollama_url: Ollama server URL.

    Returns:
        The corrected transcript text.
    """
    if provider == "gemini":
        return correct_with_gemini(text, api_key=gemini_api_key, model=gemini_model)
    if provider == "ollama":
        return correct_with_ollama(text, model=ollama_model, url=ollama_url)
    msg = f"Unknown provider: {provider!r}. Use 'gemini' or 'ollama'."
    raise ValueError(msg)
