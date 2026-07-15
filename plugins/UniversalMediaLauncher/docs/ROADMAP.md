# 🗺️ Project Roadmap | Universal Media Launcher

A high-level view of the main milestones achieved from the absolute beginning to the final production release.

---

### 📦 v1.0.0 — The Image Queue (Gallery Viewer)
*Main Focus: Build the core selection tool and launch local folders.*
- [x] Injected golden selection buttons onto Stash image gallery cards.
- [x] Saved selected card data securely inside browser memory.
- [x] Created zero-byte folder links inside Windows Temp to prevent duplicating files.
- [x] Swapped out problematic wrapper libraries for a direct database query helper.
- [x] Successfully launched Windows Explorer displaying the compiled gallery queue.

### 📦 v1.1.0 — The Video Queue (Scenes Support)
*Main Focus: Expand the plugin into a dual-queue automation system.*
- [x] Added complete support for tracking and queueing video file cards ("Scenes").
- [x] Built the dual floating golden pill toolbar panel in the corner of the screen.
- [x] Implemented dynamic count badges that change color when items are added.
- [x] Consolidated all script files into a clean `frontend/` and `backend/` folder layout.

### 📦 v1.2.0 — Caching & UI Realignment
*Main Focus: Polish interface bugs, fix page transitions, and optimize speed.*
- [x] Locked the main toggle picker button inside the navbar next to the zoom slider.
- [x] Eliminated duplicate ghost buttons from spawning during page tab switches.
- [x] Implemented a 50ms script debouncer to stop duplicate database reads.
- [x] Added cross-tab synchronization to update toggle configurations live without a page refresh.
- [x] Replaced the generic card icons with the official Lucide Rocket logo.

### 📦 v1.3.0 — Cross-Platform & Headless Hardening
*Main Focus: Outsmart server bugs and ensure flawless execution on both Windows and Linux.*
- [x] Built an argument fallback parser to stop Stash from breaking on headless task calls.
- [x] Added dynamic network port agnosticism to support customized server ports automatically.
- [x] Verified filesystem rules inside Linux (WSL) using native symbolic links (`os.symlink`).
- [x] Implemented `shutil.which` so users can just type `mpv` globally on Linux instead of full absolute paths.
- [x] Silenced player terminal text loops and driver warnings using `os.devnull` redirects.

### 🚀 v1.4.0 — Production Freeze (Release Ready)
*Main Focus: Clean, secure, and silent distribution.*
- [x] Changed the backend logging threshold to `ERROR` for quiet, fast execution.
- [x] Silenced browser console developer tracking logs.
- [x] Used history filters to erase all old logs, cache files, and private developer paths from past commits.
