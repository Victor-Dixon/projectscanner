"""Allow ``python -m projectscanner``."""

from projectscanner.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
