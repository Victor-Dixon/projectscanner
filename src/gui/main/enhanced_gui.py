"""
Legacy compatibility shim for the old enhanced GUI surface.

The historical project exposed ``gui.main.enhanced_gui`` and several launchers
and smoke tests still import that path. The original heavy Qt implementation is
no longer present in this repository, so this module provides a lightweight
surface that preserves the callable entrypoints and button wiring exercised by
tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _TextInput:
    value: str = ""

    def setText(self, value: str) -> None:
        self.value = value

    def text(self) -> str:
        return self.value


@dataclass
class _Checkbox:
    checked: bool = False

    def setChecked(self, value: bool) -> None:
        self.checked = bool(value)

    def isChecked(self) -> bool:
        return self.checked


@dataclass
class _ComboBox:
    value: str = "General Analysis"

    def setCurrentText(self, value: str) -> None:
        self.value = value

    def currentText(self) -> str:
        return self.value


class GitHubScanWorker:
    """Minimal worker stub used by legacy smoke tests and launchers."""

    def __init__(
        self,
        username: str,
        include_public: bool = True,
        include_private: bool = False,
        deep_analysis: bool = False,
    ) -> None:
        self.username = username
        self.include_public = include_public
        self.include_private = include_private
        self.deep_analysis = deep_analysis

    def start(self) -> None:
        """Preserve the old async-style interface without side effects."""
        return None


class EnhancedProjectScannerGUI:
    """Small compatibility object that preserves the old GUI method surface."""

    def __init__(self) -> None:
        self.github_username_input = _TextInput()
        self.scan_public_cb = _Checkbox(True)
        self.scan_private_cb = _Checkbox(False)
        self.deep_analysis_cb = _Checkbox(False)
        self.analysis_type_combo = _ComboBox()
        self.last_worker: GitHubScanWorker | None = None

    def start_portfolio_analysis(self) -> None:
        return None

    def start_quality_analysis(self) -> None:
        return None

    def start_general_analysis(self) -> None:
        return None

    def generate_report(self) -> None:
        return None

    def handle_quick_scan_project(self) -> None:
        self.start_general_analysis()

    def handle_quick_portfolio_analysis(self) -> None:
        self.start_portfolio_analysis()

    def handle_quick_quality_check(self) -> None:
        self.start_quality_analysis()

    def handle_quick_generate_report(self) -> None:
        self.generate_report()

    def scan_github_portfolio(self) -> GitHubScanWorker:
        worker = GitHubScanWorker(
            username=self.github_username_input.text(),
            include_public=self.scan_public_cb.isChecked(),
            include_private=self.scan_private_cb.isChecked(),
            deep_analysis=self.deep_analysis_cb.isChecked(),
        )
        self.last_worker = worker
        worker.start()
        return worker

    def start_analysis(self) -> None:
        selected = self.analysis_type_combo.currentText()
        if selected == "Quality Assessment":
            self.start_quality_analysis()
        elif selected == "Portfolio Analysis":
            self.start_portfolio_analysis()
        else:
            self.start_general_analysis()


def launch_gui() -> EnhancedProjectScannerGUI:
    """Return the compatibility GUI object for legacy callers."""
    return EnhancedProjectScannerGUI()


def main() -> int:
    launch_gui()
    return 0
