## Project snapshot

Small learning repository containing short Python scripts used to demonstrate basic concepts:
- `mini_tender.py` — small interactive tender viewer (in-memory `tenders` list, menu loop).
- `basics.py` — simple calculator using `match` and interactive input.
- `dictionary.py` — examples of dicts and lookups over a `people` list.
- `loops.py` — simple loop demo and a very small interactive menu (shows `match` usage).

Python version: code uses `match/case` syntax -> requires Python 3.10 or newer. Prefer that interpreter in VS Code.

## High-level notes for an AI coding agent

- This is not a package or service — it's a set of standalone scripts. Changes should preserve their ability to run with `python <file>.py`.
- Many functions print results instead of returning them. Tests or refactors should add `return` values or wrap prints behind a small adapter.
- Input prompts and printed messages are used as the primary I/O; keep prompt text stable when making edits unless intentionally changing UX.

## Key file patterns & examples (search these files)

- `mini_tender.py` — `tenders` is a list of dicts. Each tender has keys: `title`, `province`, `organization`, `amount`, `deadline`.
  Example: { "title": "Tender 1", "province": "Bagmati", "organization": "Urban Dev Office", "amount": 50000, "deadline": "2024-2-2" }
  Note: menu loop uses `while True` + `match choice:`; currently only case "1" is implemented (ViewAllTenders). Expect to find unimplemented menu handlers.

- `basics.py` — interactive calculator. Uses `match op:` for operators and `input()` to collect operands. It imports itself conditionally which may re-run prompts — be careful when refactoring.

- `dictionary.py` — iterates `people` list and compares `peps["hobby"] == hobby`. Watch for logic indentation: the 'not found' message is printed inside the loop in current code (likely a bug).

## Dev workflow / run & debug

- Run a script directly (PowerShell):
  ```powershell
  python .\mini_tender.py
  ```
- Ensure VS Code Python interpreter is set to Python 3.10+ to avoid `match` syntax errors.
- For debugging: set breakpoints in the file and launch the file as a module/entry in VS Code. Since code is interactive, consider supplying input using the Debug Console or temporarily refactor prompts behind injectable I/O helpers.

## Integration & external deps

- There are no external dependencies or services. No CI, tests, or packaging detected.

## Editing guidance for PRs

- Preserve the shape of `tenders` objects (fields listed above) unless you update all code that reads them.
- Keep printed prompt strings stable unless UX change is intentional — other scripts or manual tests may rely on exact prompt wording.
- Small, safe refactors: add `if __name__ == "__main__"` guards, convert print-only functions to return values (and provide thin print wrappers), and add Python version check for `match`.

## Short list of follow-ups an agent can do (pick one):
- Implement missing menu cases in `mini_tender.py` (search/add/delete/exit).
- Fix the 'not found' printing bug in `dictionary.py` so the message prints once after the loop.
- Add `__main__` guards and simple unit-testable functions with a small `tests/` scaffold (optional).

If any part of this note is unclear or you'd like different examples or more detailed run/debug steps, tell me which area to expand.
