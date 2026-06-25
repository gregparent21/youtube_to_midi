import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from server.splitters import (
    check_available,
    run_audio_separator,
    run_demucs,
    run_spleeter,
)


def test_check_available_all_missing():
    with patch("shutil.which", return_value=None):
        result = check_available()
    assert result == {"demucs": False, "spleeter": False, "audio-separator": False}


def test_check_available_demucs_only():
    def _which(name):
        return "/usr/bin/demucs" if name == "demucs" else None

    with patch("shutil.which", side_effect=_which):
        result = check_available()
    assert result["demucs"] is True
    assert result["spleeter"] is False
    assert result["audio-separator"] is False


def test_run_demucs_success(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    stems_dir = tmp_path / "htdemucs" / "input"
    stems_dir.mkdir(parents=True)
    for stem in ["vocals", "drums", "bass", "other"]:
        (stems_dir / f"{stem}.wav").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        result = run_demucs(audio, tmp_path)

    assert set(result.keys()) == {"vocals", "drums", "bass", "other"}
    assert result["vocals"].name == "vocals.wav"


def test_run_demucs_failure(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr=b"demucs error")
        with pytest.raises(RuntimeError, match="demucs error"):
            run_demucs(audio, tmp_path)


def test_run_spleeter_success(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    out = tmp_path / "input"
    out.mkdir()
    for stem in ["vocals", "drums", "bass", "other"]:
        (out / f"{stem}.wav").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        result = run_spleeter(audio, tmp_path)

    assert "vocals" in result
    assert "drums" in result


def test_run_audio_separator_success(tmp_path):
    audio = tmp_path / "input.wav"
    audio.touch()
    (tmp_path / "input_(Vocals)_MDXNet.wav").touch()
    (tmp_path / "input_(No Vocals)_MDXNet.wav").touch()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        result = run_audio_separator(audio, tmp_path)

    assert "vocals" in result
    assert "other" in result
