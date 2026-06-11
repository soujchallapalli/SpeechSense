from unittest.mock import patch

import pytest
from speechsense.correction import correct_transcript, correct_with_gemini, correct_with_ollama
from speechsense.correction_pipeline import (
    build_arg_parser,
    correct_row,
    load_csv,
    process_pipeline,
    save_csv,
)


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
        fieldnames, rows = load_csv(str(csv_path))
        assert fieldnames == ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]
        assert len(rows) == 1
        assert rows[0]["name"] == "Stelios"

    def test_load_csv_missing_columns(self, tmp_path: pytest.TempPathFactory) -> None:
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text("name,raw_text_vosk\nStelios,hello\n")
        with pytest.raises(ValueError, match="missing required columns"):
            load_csv(str(csv_path))

    def test_load_csv_empty_data(self, tmp_path: pytest.TempPathFactory) -> None:
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("timestamp,name,raw_text_vosk,time_taken_sec\n")
        fieldnames, rows = load_csv(str(csv_path))
        assert fieldnames == ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]
        assert len(rows) == 0

    def test_correct_row_adds_text(self) -> None:
        row = {
            "timestamp": "2026-04-28T10:00:05",
            "name": "Stelios",
            "raw_text_vosk": "helo team",
            "time_taken_sec": "6.2",
        }
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.return_value = "Hello team."
            result = correct_row(row, provider="gemini")
        assert result["text"] == "Hello team."
        assert result["name"] == "Stelios"

    def test_correct_row_failure_uses_empty_string(self) -> None:
        row = {
            "timestamp": "2026-04-28T10:00:05",
            "name": "Stelios",
            "raw_text_vosk": "helo team",
            "time_taken_sec": "6.2",
        }
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.side_effect = Exception("API error")
            result = correct_row(row, provider="gemini")
        assert result["text"] == ""

    def test_correct_row_returns_copy(self) -> None:
        row = {
            "timestamp": "2026-04-28T10:00:05",
            "name": "Stelios",
            "raw_text_vosk": "helo team",
            "time_taken_sec": "6.2",
        }
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.return_value = "Hello team."
            result = correct_row(row, provider="gemini")
        assert result is not row
        assert "text" not in row

    def test_save_csv(self, tmp_path: pytest.TempPathFactory) -> None:
        fieldnames = ["timestamp", "name", "raw_text_vosk", "time_taken_sec"]
        rows = [
            {
                "timestamp": "2026-04-28T10:00:05",
                "name": "Stelios",
                "raw_text_vosk": "helo team",
                "time_taken_sec": "6.2",
                "text": "Hello team.",
            },
        ]
        out = tmp_path / "out.csv"
        save_csv(fieldnames, rows, str(out))
        content = out.read_text()
        assert "timestamp,name,raw_text_vosk,time_taken_sec,text" in content
        assert "Hello team." in content

    def test_process_pipeline(self, tmp_path: pytest.TempPathFactory) -> None:
        inp = tmp_path / "in.csv"
        inp.write_text("timestamp,name,raw_text_vosk,time_taken_sec\n" "2026-04-28T10:00:05,Stelios,helo team,6.2\n")
        out = tmp_path / "out.csv"
        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.return_value = "Hello team."
            process_pipeline(str(inp), str(out), provider="gemini", max_workers=1)
        assert out.exists()
        content = out.read_text()
        assert "Hello team." in content

    def test_process_pipeline_parallel(self, tmp_path: pytest.TempPathFactory) -> None:
        inp = tmp_path / "in.csv"
        inp.write_text(
            "timestamp,name,raw_text_vosk,time_taken_sec\n"
            "t1,A,first transcript,1.0\n"
            "t2,B,second transcript,2.0\n"
            "t3,C,third transcript,3.0\n"
        )
        out = tmp_path / "out.csv"

        side_effects = iter(["First.", "Second.", "Third."])

        with patch("speechsense.correction_pipeline.correct_transcript") as mock_fn:
            mock_fn.side_effect = lambda *a, **kw: next(side_effects)
            process_pipeline(str(inp), str(out), provider="gemini", max_workers=3)

        lines = out.read_text().strip().splitlines()
        assert len(lines) == 4
        assert "First." in lines[1]
        assert "Second." in lines[2]
        assert "Third." in lines[3]
        assert mock_fn.call_count == 3

    def test_arg_parser_defaults(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.csv"])
        assert args.input == "in.csv"
        assert args.output == "out.csv"
        assert args.provider == "gemini"
        assert args.workers == 4
        assert args.gemini_api_key is None
        assert args.ollama_model == "gemma3"

    def test_arg_parser_ollama_provider(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--provider", "ollama"])
        assert args.provider == "ollama"

    def test_arg_parser_custom_workers(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--workers", "8"])
        assert args.workers == 8

    def test_arg_parser_gemini_flags(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args([
            "--input",
            "in.csv",
            "--output",
            "out.csv",
            "--gemini-api-key",
            "mykey",
            "--gemini-model",
            "gemini-2.0-pro",
        ])
        assert args.gemini_api_key == "mykey"
        assert args.gemini_model == "gemini-2.0-pro"

    def test_arg_parser_ollama_flags(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args([
            "--input",
            "in.csv",
            "--output",
            "out.csv",
            "--ollama-model",
            "llama3",
            "--ollama-url",
            "http://localhost:11435",
        ])
        assert args.ollama_model == "llama3"
        assert args.ollama_url == "http://localhost:11435"

    def test_arg_parser_invalid_provider(self) -> None:
        parser = build_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--provider", "invalid"])
