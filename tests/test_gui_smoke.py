"""
Lightweight smoke tests to ensure GUI buttons are wired and callable.
These tests mock QApplication and long-running workers to avoid real scans.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.mark.skipif('PyQt5' not in sys.modules and False, reason="PyQt5 may be unavailable in CI")
def test_smoke_gui_buttons_wired():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

    with patch('PyQt5.QtWidgets.QApplication'):
        from gui.main.enhanced_gui import EnhancedProjectScannerGUI

        gui = EnhancedProjectScannerGUI()

        # Mock long-running workers
        gui.start_portfolio_analysis = Mock()
        gui.start_quality_analysis = Mock()
        gui.start_general_analysis = Mock()
        gui.generate_report = Mock()

        # Dashboard quick actions
        gui.handle_quick_scan_project()
        gui.start_general_analysis.assert_called()
        gui.handle_quick_portfolio_analysis()
        gui.start_portfolio_analysis.assert_called()
        gui.handle_quick_quality_check()
        gui.start_quality_analysis.assert_called()
        gui.handle_quick_generate_report()
        gui.generate_report.assert_called()

        # GitHub tab buttons
        gui.github_username_input.setText('dummy')
        gui.scan_public_cb.setChecked(True)
        gui.scan_private_cb.setChecked(False)
        gui.deep_analysis_cb.setChecked(False)
        with patch.object(gui, 'scan_github_portfolio', wraps=gui.scan_github_portfolio):
            with patch('gui.main.enhanced_gui.GitHubScanWorker') as MockWorker:
                instance = Mock()
                MockWorker.return_value = instance
                gui.scan_github_portfolio()
                assert MockWorker.called
                assert instance.start.called

        # Analysis tab start button route
        gui.analysis_type_combo.setCurrentText('Quality Assessment')
        with patch.object(gui, 'start_quality_analysis', wraps=gui.start_quality_analysis) as sq:
            gui.start_analysis()
            assert sq.called


