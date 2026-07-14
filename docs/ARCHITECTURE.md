# 🏛️ Architecture & System Design | Universal Media Launcher

This document maps out the internal architectural design, data execution pipelines, and cross-platform mechanics of the **Universal Media Launcher** plugin for Stash.

## 🗺️ Architectural Ecosystem Overview

Universal Media Launcher operates as a zero-dependency, framework-agnostic system extension split into three structural architectural layers:

## 🌐 1. Frontend Layer Architecture (`frontend/`)

The user interface components hook directly into Stash's modern Single Page Application (SPA) DOM state loops without requiring heavy compilation steps.

### A. Dynamic Injection & Lifecycle Syncing
* **Target Handlers**: The engine attaches to `PluginApi.Event.addEventListener('stash:location', onNavigate)`.
* **State Debouncing**: Because Stash fires multiple sequential layout rendering ticks during view navigation transitions, a **50ms Debouncer Timer** stabilizes database reads inside `syncFromStashConfig()`, forcing rapid layout triggers to consolidate into a single clean network query.
* **Cross-Tab Synchronization**: Leverages the browser window’s native `'storage'` event listener. When a configuration variable is toggled on a separate browser setting tab panel, the storage bus instantly broadcasts a signal, forcing active picker windows to sync live without layout lag.

### B. Aesthetic Interaction Blueprint
* **Pill Tray Entry**: An absolute CSS keyframe scale slide (`scale(0.92)` -> `scale(1)`) combined with a custom `cubic-bezier(0.16, 1, 0.3, 1)` easing layout creates a lightweight, hardware-accelerated "bloom" entry interface.
* **Visual Counter Badges**: State trackers append/remove a `.zero` class modifier flag. Empty states remain dark (`#232323`), while populated lists automatically bloom into a golden rimmed (`rgba(214,175,55,0.3)`), high-contrast active dashboard card.


## 🔌 2. Inter-Process Communication & Hardening (`backend/main.py`)

The connection bridge between the Go-based Stash server core and the local Python execution subsystem is handled using standard stream pipelines (`stdin`/`stdout`).

### A. The Headless Argument Task `None` Fallback Solution
When triggering a backend plugin automation task from a headless frontend component without providing an ID argument array, Stash’s core schema manager strips the top-level string identifiers, passing them down the pipeline as **`task: "None"`**.

To outsmart this routing limitation, `main.py` uses a **Payload-Driven Task Reconstruction Strategy**:
1. It intercepts the raw `sys.stdin.read()` input block.
2. It parses the inner dictionary contents.
3. If `task` is empty or `"None"`, but an explicit string argument key (such as `"action": "wipe"`, `"scenes"`, or `"galleries"`) is extracted, the Python router **manually overrides the error and reconstructs the target mapping**:

```python
if (not task_name or task_name == "None") and action_value == "wipe":
    task_name = "Wipe Virtual Folders"
elif "scenes" in str(raw_args):
    task_name = "Launch Video Player"
```

### B. Network Port Agnosticism & Authentication Handshaking
To prevent network drops when developers run alternative port sandbox environments (e.g., port `9988` or `9998` under WSL environments), the backend pulls runtime data loops from the **`server_connection`** parameter array passed inside the stdin payload stream. 

This enables the runtime engine to dynamically update its target endpoints (`STASH_PORT`) and automatically attach the active security session authorization tokens (`SessionCookie`) straight onto outgoing `urllib.request` headers, preventing permission blocks.


## 🗂️ 3. Cross-Platform Execution Framework (`backend/launcher.py`)

The system core features dynamic filesystem hooks to ensure flawless, zero-dependency behavior across both Windows architecture and native POSIX Linux kernel distributions.

### A. Virtual Directory Assembly (Image Viewer Engine)
Instead of copying files and wasting disk space, the layout engine generates virtual junction matrices inside temporary file locations (`tempfile.gettempdir()/StashVirtualGalleries`).
* **On Windows**: It spawns an elevated command wrapper executing `mklink /j` directory junctions.
* **On Linux**: It calls the native `os.symlink(target_is_directory=True)` module hook.

### B. Dynamic Environment Binary Lookup
To resolve players without forcing rigid configuration paths, the execution layer utilizes **`shutil.which(PLAYER_PATH)`**. 
* On Windows, it handles local absolute files (`C:\Program Files\...\mpv.exe`) while scanning `PATHEXT` profiles to track command utilities.
* On Linux, it seamlessly checks the machine's global system path variables (`/usr/bin/mpv`) enabling users to type just `mpv` or `vlc` natively.

### C. Standard Error & Ticker Decoupling (`os.devnull`)
Multimedia applications like MPV continuously stream active loop timelines (`AV: 00:00:21`) and hardware driver warning strings (`vulkan/OpenGL DRI3 device failed`) onto the console screen. 

Because Stash flags anything captured on the `stderr` pipe as a red critical error badge, the launcher completely decouples the output streams from Stash by routing them straight into the system's null storage trash bin:

```python
with open(os.devnull, 'wb') as devnull:
    subprocess.Popen(
        execution_args,
        stdout=devnull,
        stderr=devnull,
        close_fds=True
    )
```

## 🛡️ 4. Data Security, Logging, & Production Freezing

1. **Production Silencing**: Universal Media Launcher utilizes a production log barrier threshold set to **`logging.ERROR`**. It remains completely silent on disk, saving drive lifespan and keeping lines clean unless a critical application crash happens.
2. **Local Encapsulation**: Active tracing writes to an isolated local text log file sitting in the parent plugin folder tree (`UniversalMediaLauncher.log`). It stays completely out of Stash's server interface dashboard logs, protecting system metrics.
3. **Repository Cleanliness**: The project ships with a strict `.gitignore` bluep