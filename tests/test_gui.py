"""
Tests for the enhanced GUI functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

try:  # pragma: no cover - GUI deps may be missing
    import PyQt5  # noqa: F401
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from core.projectscanner.gui import ScanWorker, ProjectScannerGUI
except Exception:  # pragma: no cover
    pytest.skip("PyQt5 not available", allow_module_level=True)

from scanners.github_library_scanner import clone_repository


class TestScanWorker:
    """Test the ScanWorker class."""
    
    def test_scan_worker_initialization(self):
        """Test that ScanWorker can be initialized."""
        project_path = Path("test_project")
        worker = ScanWorker(project_path)
        assert worker.project_path == project_path
        assert worker.output_dir == project_path

    def test_scan_worker_with_custom_output_dir(self):
        """Test ScanWorker with custom output directory."""
        project_path = Path("test_project")
        output_dir = Path("test_output")
        worker = ScanWorker(project_path, output_dir)
        assert worker.project_path == project_path
        assert worker.output_dir == output_dir


class TestCloneRepository:
    """Test the repository cloning helper."""
    
    @patch('scanners.github_library_scanner.subprocess.run')
    def test_clone_repository_success(self, mock_run):
        """Test successful repository cloning."""
        mock_run.return_value = Mock(returncode=0)
        
        temp_dir = Path("/tmp/test")
        repo_url = "https://github.com/testuser/testrepo"
        
        result = clone_repository(repo_url, temp_dir)
        
        expected_path = temp_dir / "testrepo"
        assert result == expected_path
        mock_run.assert_called_once()

    @patch('scanners.github_library_scanner.subprocess.run')
    def test_clone_repository_failure(self, mock_run):
        """Test repository cloning failure."""
        mock_run.side_effect = Exception("Git not found")
        
        temp_dir = Path("/tmp/test")
        repo_url = "https://github.com/testuser/testrepo"
        
        with pytest.raises(Exception, match="Failed to clone repository"):
            clone_repository(repo_url, temp_dir)


class TestProjectScannerGUI:
    """Test the ProjectScannerGUI class."""
    
    @patch('PyQt5.QtWidgets.QApplication')
    def test_gui_initialization(self, mock_app):
        """Test that the GUI can be initialized."""
        # Mock QApplication to avoid GUI initialization issues in tests
        mock_app.instance.return_value = Mock()
        
        # This should not raise any exceptions
        gui = ProjectScannerGUI()
        assert gui is not None
        assert hasattr(gui, 'library_data')
        assert isinstance(gui.library_data, dict)

    def test_library_operations(self):
        """Test library loading and saving operations."""
        gui = ProjectScannerGUI()
        
        # Test library loading (should not fail even if file doesn't exist)
        gui.load_library()
        assert isinstance(gui.library_data, dict)
        
        # Test library saving (should not fail)
        gui.library_data = {"test": "data"}
        gui.save_library()

    def test_populate_tree_item(self):
        """Test tree item population."""
        gui = ProjectScannerGUI()
        
        # Create a mock tree item
        parent = Mock()
        
        # Test with dictionary
        test_data = {"key1": "value1", "key2": {"nested": "value"}}
        gui.populate_tree_item(parent, test_data)
        
        # Test with list
        test_list = ["item1", "item2"]
        gui.populate_tree_item(parent, test_list)
        
        # Test with string
        gui.populate_tree_item(parent, "simple string")
        
        # Should not raise any exceptions
        assert True 