# Universal Media Launcher (UML) for Stash

Universal Media Launcher is an advanced, premium user interface extension for Stash. It provides a highly interactive, golden-themed layout overlay allowing you to queue up multiple Gallery Folders and Scene Videos into independent playlist channels and launch them directly into your favorite native desktop applications.

Bypass the browser's video encoding boundaries and image rendering lags completely by routing your Stash media straight to your local operating system players.

## 🖼️ Features
- **Dual Independent Queues**: Separately stack up to 50 Gallery folders and 50 Video scenes simultaneously.
- **Dynamic DOM Injection**: Golden action badges automatically overlay on top of Stash thumbnail cards.
- **Multi-Platform Ready**: Smooth process branching across both Windows and Linux environments.
- **Zero-Dependency Core**: Lightweight architecture engineered using native GraphQL execution tunnels.
- **Clean Logging Profile**: Operational statuses route silently through Stash's native `[DEBUG]` filter keys.

## 📦 Repository Structure
For a clean installation, ensure your Stash plugins folder structure matches this layout:
```text
.stash/plugins/UniversalMediaLauncher/
├── UniversalMediaLauncher.yml
├── frontend/
│   ├── main.js
│   └── main.css
└── backend/
    ├── main.py
    └── launcher.py
```

## 🛠️ Out-of-the-Box Configuration Blueprints

Universal Media Launcher features native system fallbacks. To change your viewing applications, navigate to **Settings ➡️ Plugins ➡️ Universal Media Launcher** inside Stash and adjust the path strings.

### 🪟 Windows Setup Examples

#### 1. Default Built-in Applications (No extra software needed)
- **External Image Viewer Application Path**: `explorer` *(Default placeholder. Automatically resolves your queue in sequential `01_Name` directory folders and opens the native Microsoft Photos App).*
- **External Video Player Application Path**: `C:\Windows\System32\wmplayer.exe` *(Bypasses the UWP sandbox to play your scene selections back-to-back in Windows Media Player).*

#### 2. Specialized Media Players (High Performance)
- **External Image Viewer Application Path**: `C:\Program Files (x86)\FastStone Image Viewer\FSViewer.exe`
- **External Video Player Application Path**: `C:\Program Files\MPV\mpv.exe` *(or VLC / MPC-HC absolute paths)*

### 🐧 Linux Setup Examples
- **External Image Viewer Application Path**: `viewnior` *(or `feh` / `gwenview`)*
- **External Video Player Application Path**: `mpv` *(or `vlc` / `xdg-open` for system default file managers)*

## 🚀 Usage Walkthrough
1. Go to your Stash Plugins menu page and hit **Reload Plugins**.
2. Complete a browser cache flush inside your browser using **`Ctrl` + `F5`**.
3. Locate the **Universal Media Launcher** picker toggle icon (Stacked Viewport Frame) on your top navbar row and click it to activate **Picking Mode**.
4. Golden `+` badges will render on card thumbnails. Click them to stack items onto your playlist.
5. Click the floating dashboard icons on the bottom right of your screen to launch or clear your queues instantly!


# Tested Image Viewers
## Windows
### FastStone Viewer ✔️
### IrfanView ✔️
### ❌

## Linux

# Tested Video Players

## Windows
### mpv ✔️
### Media player classic ✔️
### vlc ✔️
### wmplayer ✔️

## Linux
###❌

## TODO
[x] Change log level before pushing to a repo also remove js console logging
[x] Add Clean up task for virtual folders
[x] toggle button is bleeding to the scene view and it covers a part of the video player.
[x] add a standard logging to a text file like the renamer plugin does.
[x] Lock your clean logging file engine into your Python workspace scripts.
[x] Polish frontend/main.css to add that premium fade-in and scale hover animation layer to the golden launcher widget so it slides open like high-end desktop software.