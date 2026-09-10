#!/usr/bin/env python3
"""Legacy manual GUI harness retained for historical salvage.

This module is intentionally not a pytest test. The supported ProjectScanner
production surface is headless; run this file manually only when evaluating
whether the legacy GUI is worth restoring.
"""

import sys


def run_manual_automatic_analysis() -> int:
    """Launch the legacy GUI harness when its optional dependencies exist."""
    print("Legacy GUI manual check")
    try:
        from PyQt5 import QtWidgets
        from core.projectscanner.gui import ProjectScannerGUI
    except ImportError as exc:
        print(f"Legacy GUI unavailable: {exc}")
        return 1

    app = QtWidgets.QApplication(sys.argv)
    gui = ProjectScannerGUI()
    gui.show()
    return int(app.exec_())


if __name__ == "__main__":
    raise SystemExit(run_manual_automatic_analysis())
