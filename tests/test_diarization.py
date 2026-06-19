from speechsense.speech_to_text import diarization


def test_assign_picks_max_overlap():
    segs = [{"start": 1.0, "end": 4.0, "text": "x"}]
    turns = [
        {"start": 0.0, "end": 2.0, "speaker": "SPK0"},
        {"start": 2.0, "end": 4.0, "speaker": "SPK1"},
    ]
    assert diarization.assign_speakers(segs, turns)[0]["speaker"] == "SPK1"


def test_assign_no_overlap_yields_unknown():
    segs = [{"start": 10.0, "end": 12.0, "text": "x"}]
    turns = [{"start": 0.0, "end": 5.0, "speaker": "SPK0"}]
    assert diarization.assign_speakers(segs, turns)[0]["speaker"] == "UNKNOWN"


def test_assign_boundary_touch_is_unknown():
    segs = [{"start": 2.0, "end": 4.0, "text": "x"}]
    turns = [{"start": 0.0, "end": 2.0, "speaker": "S0"}]
    assert diarization.assign_speakers(segs, turns)[0]["speaker"] == "UNKNOWN"


def test_assign_preserves_text_and_times():
    segs = [{"start": 0.0, "end": 2.0, "text": "keep me"}]
    turns = [{"start": 0.0, "end": 2.0, "speaker": "S0"}]
    out = diarization.assign_speakers(segs, turns)[0]
    assert out["text"] == "keep me" and out["start"] == 0.0 and out["end"] == 2.0


def test_assign_empty_segments_returns_empty():
    assert diarization.assign_speakers([], [{"start": 0, "end": 1, "speaker": "S"}]) == []


def test_merge_combines_same_speaker():
    segs = [
        {"speaker": "A", "start": 0.0, "end": 1.0, "text": "hello"},
        {"speaker": "A", "start": 1.0, "end": 2.0, "text": "world"},
    ]
    assert diarization.merge_consecutive_speakers(segs) == [
        {"speaker": "A", "start": 0.0, "end": 2.0, "text": "hello world"}
    ]


def test_merge_keeps_different_speakers_separate():
    segs = [
        {"speaker": "A", "start": 0.0, "end": 1.0, "text": "a"},
        {"speaker": "B", "start": 1.0, "end": 2.0, "text": "b"},
    ]
    out = diarization.merge_consecutive_speakers(segs)
    assert [s["speaker"] for s in out] == ["A", "B"]


def test_merge_alternating_pattern():
    segs = [
        {"speaker": "A", "start": 0.0, "end": 1.0, "text": "1"},
        {"speaker": "B", "start": 1.0, "end": 2.0, "text": "2"},
        {"speaker": "A", "start": 2.0, "end": 3.0, "text": "3"},
    ]
    out = diarization.merge_consecutive_speakers(segs)
    assert [s["speaker"] for s in out] == ["A", "B", "A"]


def test_merge_empty():
    assert diarization.merge_consecutive_speakers([]) == []


def test_merge_does_not_mutate_input():
    segs = [
        {"speaker": "A", "start": 0.0, "end": 1.0, "text": "a"},
        {"speaker": "A", "start": 1.0, "end": 2.0, "text": "b"},
    ]
    diarization.merge_consecutive_speakers(segs)
    assert segs[0]["text"] == "a"
