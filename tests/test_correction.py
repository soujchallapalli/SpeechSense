from unittest.mock import patch

import pandas as pd
import pytest
from speechsense.correction import correct_transcript, correct_with_gemini, correct_with_ollama
from speechsense.correction_pipeline import apply_correction, build_arg_parser, load_csv


class TestCorrectWithGemini:
    def test_success(self) -> None:
        mock_response = type("Response", (), {"text": "  Hello team, today we discuss.  "})()

        with patch("google.genai.Client") as mock_client:
            instance = mock_client.return_value
            instance.models.generate_content.return_value = mock_response

            result = correct_with_gemini("helo team today we discuss", api_key="fake-key")

        assert result == "Hello team, today we discuss."

    def test_missing_api_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
            correct_with_gemini("hello", api_key=None)


class TestCorrectWithOllama:
    def test_success(self) -> None:
        mock_json = {"response": "  Can we target students first?  "}

        with patch("speechsense.correction.requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_json
            mock_post.return_value.raise_for_status.return_value = None

            result = correct_with_ollama("can we target students first")

        assert result == "Can we target students first?"

    def test_request_failure(self) -> None:
        with patch("speechsense.correction.requests.post") as mock_post:
            mock_post.return_value.raise_for_status.side_effect = Exception("Connection refused")

            with pytest.raises(Exception, match="Connection refused"):
                correct_with_ollama("hello")


class TestCorrectTranscript:
    def test_gemini_provider(self) -> None:
        with patch("speechsense.correction.correct_with_gemini") as mock_fn:
            mock_fn.return_value = "Corrected."
            result = correct_transcript("raw", provider="gemini")
        assert result == "Corrected."

    def test_ollama_provider(self) -> None:
        with patch("speechsense.correction.correct_with_ollama") as mock_fn:
            mock_fn.return_value = "Corrected."
            result = correct_transcript("raw", provider="ollama")
        assert result == "Corrected."

    def test_unknown_provider(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            correct_transcript("raw", provider="invalid")


class TestCorrectionPipeline:
    def test_load_csv_valid(self, tmp_path: pytest.TempPathFactory) -> None:
        csv_path = tmp_path / "input.csv"
        csv_path.write_text(
            "timestamp,name,raw_text_vosk,time_taken_sec\n" "2026-04-28T10:00:05,Stelios,helo team,6.2\n"
        )
        df = load_csv(str(csv_path))
        assert list(df.columns) == ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]
        assert len(df) == 1

    def test_load_csv_missing_columns(self, tmp_path: pytest.TempPathFactory) -> None:
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text("name,raw_text_vosk\nStelios,hello\n")
        with pytest.raises(ValueError, match="missing required columns"):
            load_csv(str(csv_path))

    def test_load_csv_empty(self, tmp_path: pytest.TempPathFactory) -> None:
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("timestamp,name,raw_text_vosk,time_taken_sec\n")
        df = load_csv(str(csv_path))
        assert len(df) == 0

    def test_apply_correction_adds_text_column(self) -> None:
        df = pd.DataFrame({
            "timestamp": ["2026-04-28T10:00:05"],
            "name": ["Stelios"],
            "raw_text_vosk": ["helo team"],
            "time_taken_sec": [6.2],
        })
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.return_value = "Hello team."
            result = apply_correction(df, provider="gemini")
        assert "text" in result.columns
        assert result["text"].iloc[0] == "Hello team."

    def test_apply_correction_failure_uses_empty_string(self) -> None:
        df = pd.DataFrame({
            "timestamp": ["2026-04-28T10:00:05"],
            "name": ["Stelios"],
            "raw_text_vosk": ["helo team"],
            "time_taken_sec": [6.2],
        })
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.side_effect = Exception("API error")
            result = apply_correction(df, provider="gemini")
        assert result["text"].iloc[0] == ""

    def test_apply_correction_preserves_other_columns(self) -> None:
        df = pd.DataFrame({
            "timestamp": ["2026-04-28T10:00:05"],
            "name": ["Stelios"],
            "raw_text_vosk": ["helo team"],
            "time_taken_sec": [6.2],
        })
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.return_value = "Hello team."
            result = apply_correction(df, provider="gemini")
        assert result["timestamp"].iloc[0] == "2026-04-28T10:00:05"
        assert result["name"].iloc[0] == "Stelios"
        assert result["raw_text_vosk"].iloc[0] == "helo team"
        assert result["time_taken_sec"].iloc[0] == 6.2

    def test_arg_parser_default_provider(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.csv"])
        assert args.input == "in.csv"
        assert args.output == "out.csv"
        assert args.provider == "gemini"

    def test_arg_parser_ollama_provider(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--provider", "ollama"])
        assert args.provider == "ollama"

    def test_arg_parser_invalid_provider(self) -> None:
        parser = build_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--provider", "invalid"])
