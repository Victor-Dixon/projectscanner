import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scanners.github_library_scanner import GitHubLibraryScanner

def test_generate_library_summary_counts_files(tmp_path):
    scanner = GitHubLibraryScanner("dummy", output_dir=tmp_path)
    scanner.library = {
        "repo1": {
            "name": "Repo1",
            "url": "https://example.com/repo1",
            "owner": "dummy",
            "language": "Python",
            "private": False,
            "analysis": {"file1.py": {}, "file2.py": {}},
        },
        "repo2": {
            "name": "Repo2",
            "url": "https://example.com/repo2",
            "owner": "dummy",
            "language": "JavaScript",
            "private": True,
            "analysis": {"index.js": {}},
        },
    }

    summary = scanner.generate_library_summary()
    assert summary["total_files_scanned"] == 3
    repo_counts = {r["id"]: r["files_scanned"] for r in summary["repositories"]}
    assert repo_counts["repo1"] == 2
    assert repo_counts["repo2"] == 1
    assert summary["public_repositories"] == 1
    assert summary["private_repositories"] == 1
