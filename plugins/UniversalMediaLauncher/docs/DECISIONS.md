# 🧠 Architecture Decisions Record | Universal Media Launcher

This document chronicles the critical architectural decisions made during the development of the Universal Media Launcher, detailing the context, technical rationale, trade-offs, and retrospectives for each major pivot point.

---

## 1. Dropping `stashapi` for Direct GraphQL Queries

### Context
Initially, the backend python script relied on the community-standard `stashapi` wrapper library to fetch data from the Stash server core. 

### Decision
Completely strip out the external library and implement a direct, lightweight HTTP transport query helper (`query_stash_raw_graphql`) using Python’s built-in `urllib.request`.

### Rationale & Consequences
*   **The Bug**: `stashapi` was returning unpredictable nested dictionary configurations depending on how Stash categorized the library directory, causing folder path extractions to periodically fail and evaluate as a blank `None`.
*   **Dependency Freedom**: It eliminated `ModuleNotFoundError` crashes on clean user setups. The plugin can now be unzipped and run instantly without demanding a `pip install`.
*   **Performance Boost**: Cutting out the wrapper layer removed unneeded data parsing overhead, speeding up response times.

### Retrospective
Direct control over the payload schema is always superior for highly localized automation plugins. By writing our own query function, we gained absolute predictability over exactly how IDs, file structures, and basenames are mapped.

---

## 2. Using Base-Name Backtracking Fallbacks for Image Folders

### Context
Stash doesn't always populate an explicit `folder { path }` variable for image galleries in the database if the metadata configuration was scanned under specific library parameters.

### Decision
Engineered a backtracking path resolution mechanism. If the core folder attribute comes back blank, the python script automatically dives down into the gallery's underlying individual files array, extracts the physical file path of the first image entry, and executes `os.path.dirname()` to rebuild the true base path directory cleanly.

### Rationale & Consequences
*   **Bulletproof Mapping**: Bypassed metadata parsing limitations, ensuring that the image queue never fails to resolve, even if the database entry lacks standard structural attributes.
*   **Basename Matching**: Enabled the plugin to cleanly extract the real folder name (`os.path.basename`) to name the zero-byte virtual disk shortcuts properly.

### Retrospective
Never trust that a database entry will always have every field perfectly populated. Designing defensive, multi-tier data fallbacks prevents runtime script crashes and guarantees a smooth user experience.

---

## 3. Resolving the Headless Task Name `None` Bug via Argument Fallbacks

### Context
When a backend plugin task is called via an inline GraphQL mutation (`runPluginTask`) from an interface utility without providing any active argument IDs (such as clicking the `✕` cross button to trigger the cleanup script), Stash's native Go core completely strips the `task` and `task_name` string fields, passing them down the standard input stream as an empty or literal `None` string.

### Decision
Implemented a **Payload-Driven Task Reconstruction Strategy** at the absolute top of the processing loop inside `backend/main.py`.

### Rationale & Consequences
*   **The Fix**: Instead of relying strictly on Stash's broken `task` property string, Python now inspects the parameters array inside the `args` payload. If the task is blank or `None`, but the argument handshake contains `"action": "wipe"`, Python explicitly overrides the data and reconstructs the task name back to `"Wipe Virtual Folders"` dynamically:
    ```python
    if (not task_name or task_name == "None") and action_value == "wipe":
        task_name = "Wipe Virtual Folders"
    ```
*   **Seamless Routing**: This closed the communication gap completely, allowing background utilities to run perfectly without generating empty array warnings or red badged log exceptions inside Stash.

### Retrospective
When an upstream server engine behaves unpredictably, don't waste time trying to fix the upstream system. Build smart, parameter-driven intercept maps directly inside your backend to normalize the inbound stream safely.

---

## 4. Introducing the Frontend 50ms Debounce Layer

### Context
Stash’s Single Page Application (SPA) routing framework triggers multiple rapid view render cycles whenever a user navigates between different tabs (e.g., jumping from Galleries to Scenes). 

### Decision
Wrapped the core database configuration sync loop (`syncFromStashConfig`) inside a lightweight **50-millisecond JavaScript Debounce Timer Gate**.

### Rationale & Consequences
*   **Zero Resource Bloat**: If Stash fires multiple sequential navigation hooks within a few milliseconds, the debounce timer automatically kills the previous pending execution and restarts the timer clock.
*   **Server Optimization**: This squashed a sneaky bug where the plugin double-fired back-to-back GraphQL database queries on every tab change, optimizing network speeds and cutting unnecessary data read operations.

### Retrospective
Single-page application web architectures are inherently noisy with their rendering triggers. Debouncing is the industry-standard way to ensure your scripts run cleanly and execute precisely once after layout changes settle down.

---

## 5. Swapping `os.path.exists` for `shutil.which` for Media Players

### Context
The initial player launcher code checked absolute file path coordinates on disk using `os.path.exists(PLAYER_PATH)`. 

### Decision
Swapped out the traditional local checker for Python's built-in **`shutil.which()`** module loop.

### Rationale & Consequences
*   **Cross-Platform Harmony**: On Windows, users prefer typing absolute file paths (`C:\Program Files\...\mpv.exe`), which `shutil.which` resolves natively. On Linux/WSL, binaries live inside global system variables (`/usr/bin/mpv`). `shutil.which` automatically searches the global system environment paths across all operating systems.
*   **Simpler Settings Configuration**: This allowed users to type just the raw word `mpv` or `vlc` directly into their Stash settings box on Linux, making the configuration incredibly seamless.

### Retrospective
Using standard, multi-platform library wrappers like `shutil.which` saves you from writing hundreds of lines of messy, hardcoded platform-specific string matching hacks.

---

## 6. Complete Output Descriptors Redirection to `os.devnull`

### Context
When launching a standalone multimedia application like MPV inside a console context (especially inside a minimal Linux/WSL environment), the player continuously streams heavy timeline progress counters (`AV: 00:00:21`) and missing hardware acceleration graphics warnings (`vulkan/OpenGL DRI3 failed`) onto the screen. Stash captures absolutely everything from the active sub-process pipe and forcefully stamps it inside its web interface as a critical red text badge.

### Decision
Modified the `subprocess.Popen` configuration matrix inside `backend/launcher.py` to completely route the `stdout` and `stderr` descriptors into the operating system's null trash bin (`os.devnull`).

```python
with open(os.devnull, 'wb') as devnull:
    subprocess.Popen(execution_args, stdout=devnull, stderr=devnull, close_fds=True)
```

### Rationale & Consequences
*   **Suppressed Warnings**: Hardware acceleration log warnings and real-time progress tickers are instantly dropped by the host OS kernel.
*   **Silent Background Running**: The media player launches instantly, the video playlist tracks stream smoothly back-to-back, and **the Stash log screen remains 100% empty, quiet, and pristine.**

### Retrospective
When spawning external GUI software applications from a backend server loop, always detach and ground the child process output streams unless you are actively troubleshooting. This keeps your dashboard free of misleading error warnings.
