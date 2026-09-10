"""Legacy manual GUI harness retained for historical salvage.

This module is intentionally not a pytest test. The supported ProjectScanner
production surface is headless; run this file manually only when evaluating
whether the legacy GUI is worth restoring.
"""

import importlib
import sys


def run_manual_automatic_analysis() -> int:
    """Launch the legacy GUI harness when its optional dependencies exist."""
    print("Legacy GUI manual check")
    try:
        qt_widgets = importlib.import_module("PyQt5.QtWidgets")
        gui_module = importlib.import_module("core.projectscanner.gui")
    except ImportError as exc:
        print(f"Legacy GUI unavailable: {exc}")
        return 1

    app = qt_widgets.QApplication(sys.argv)
    gui = gui_module.ProjectScannerGUI()
    gui.show()
    return int(app.exec_())


if __name__ == "__main__":
    raise SystemExit(run_manual_automatic_analysis())
