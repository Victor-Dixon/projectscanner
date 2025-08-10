# Project Scanner – Task List

## Status legend
- [ ] Open
- [x] Done

## Objectives
- Unify scanners into one engine with presets (quick, standard, full)
- Integrate the unified scanner into the GUI (progress, cancel, options)
- Make `main.py` the canonical entry; keep a simple quick-scan path
- Improve docs and quick start for Windows/Linux/macOS
- Add tests and CI for scanner correctness and performance
- Prepare packaging/release artifacts

## Milestones
- [ ] Scanner unification (core engine + presets)
- [ ] GUI integration (analysis tab + options)
- [ ] CLI/docs polish and quick start
- [ ] v0.1 Beta release

## Tasks
- [ ] Implement `src/core/scanner/unified_scanner.py` with options:
  - export_context, split_by (directory|language|none), max_files_per_chunk
  - split_tests, generate_init, single vs merged outputs
- [ ] Refactor wrappers to use unified engine:
  - `scripts/scanners/quick_scanner.py`
  - `scripts/scanners/standard_scanner.py`
  - `scripts/scanners/full_scanner.py`
- [ ] Extend `main.py --scan` flags to mirror unified engine options; keep `--quick-scan`
- [ ] Wire GUI “Scan Project” to unified scanner in a background worker (progress/cancel)
- [ ] Add GUI toggles for export/splitting/init generation; show output location on completion
- [ ] Add unit tests (ignore rules, cache, move detection, merging, context export)
- [ ] Add CI workflow (lint + tests on PRs)
- [ ] Update README: install, `python main.py --gui`, `--quick-scan`, full scan examples
- [ ] Add Windows `.bat` and POSIX `.sh` convenience launchers (optional)
- [ ] Draft release notes for v0.1

## Next steps
- Implement the unified scanner and refactor wrappers
- Hook the GUI Analysis tab to the quick preset; add advanced options
- Extend `main.py --scan` with flags and update README examples
- Write core unit tests and enable CI

## Links
- GitHub repository: https://github.com/Dadudekc/projectscanner


