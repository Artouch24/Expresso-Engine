from pathlib import Path

from poker_tracker.cli.commands import main

FIXTURE = Path(__file__).parents[1] / "fixtures/winamax"


def test_cli_workflow(tmp_path, capsys):
    db = tmp_path / "test.sqlite3"
    assert main(["--database", str(db), "init"]) == 0
    assert "Initialized" in capsys.readouterr().out
    assert main(["--database", str(db), "doctor"]) == 0
    assert "[OK] Schema current" in capsys.readouterr().out
    assert main(["--database", str(db), "import", str(FIXTURE)]) == 0
    assert "Hands inserted:       2" in capsys.readouterr().out
    assert main(["--database", str(db), "stats"]) == 0
    output = capsys.readouterr().out
    assert "Tournaments: 1" in output
    assert "ROI: 200.00%" in output
    assert "Hands: 2" in output
    assert "3-handed: 1; heads-up: 1" in output
