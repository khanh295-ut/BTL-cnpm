from __future__ import annotations

import os
import sys
from pathlib import Path


def _relaunch_with_venv() -> None:
    workspace_root = Path(__file__).resolve().parent
    venv_python = workspace_root / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        return

    current_executable = Path(sys.executable).resolve()
    if current_executable != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve())])


if __name__ == "__main__":
    _relaunch_with_venv()

    import importlib

    uvicorn = importlib.import_module("uvicorn")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))

    uvicorn.run("backend.src.app:app", host=host, port=port, reload=True)