from __future__ import annotations

import pathlib
import re

IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+pip\._vendor(?P<rest>(?:\.[A-Za-z0-9_]+)*)"
)
VENDORED_RE = re.compile(r'vendored\("([^"]+)"\)')


def test_all_pip_vendor_imports_are_listed_in_vendored() -> None:
    root = pathlib.Path(__file__).resolve().parents[2]

    # 1) collect imports from src/pip/** excluding src/pip/_vendor/**
    imports: set[str] = set()
    for path in (root / "src" / "pip").rglob("*.py"):
        if "src/pip/_vendor/" in str(path).replace("\\", "/"):
            continue

        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = IMPORT_RE.match(line)
            if not m:
                continue
            rest = m.group("rest").lstrip(".")
            if not rest:
                # "import pip._vendor" is fine; nothing to vendored() here.
                continue
            imports.add(rest)

    # 2) collect vendored("...") entries
    init_py = root / "src" / "pip" / "_vendor" / "__init__.py"
    vendored = set(VENDORED_RE.findall(init_py.read_text(encoding="utf-8")))

    # 3) enforce: every import has a vendored("...") entry
    missing = sorted(imports - vendored)
    assert missing == [], "Missing vendored() entries for:\n  - " + "\n  - ".join(
        missing
    )
