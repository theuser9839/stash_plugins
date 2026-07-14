# 🚀 Universal Media Launcher (UML) for Stash

A Stash plugin  that allows to queue up multiple Gallery Folders and Scene Videos into independent playlist channels and launch them directly into your favorite native desktop applications.

Bypass the browser's video encoding boundaries and image rendering lags completely by routing your Stash media straight to your local operating system players.

## Main Motivation

### Galleries
I prefer browsing galleries with a directory list sidebar and keyboard fast navigation, stash is great for organizing, tagging and finding your content but its gallery viewer is lacking for me. This plugin merges the best of both worlds, you can quickly browse through your galleries in stash and add them to a playlist them have your favorite desktop application open them.

To achieve this i used a simple solution to create virtual folders on Windows and symlinks on Linux, which take virtually no space in your drive and let you browse the galleries that you chose.
Personally i recommend a image viewer like FastStone for windows or Geeqie for linux, that allow you to browse those virtual folder nicely, but you can use whatever you prefer.

### Videos
Stash video player is pretty good, with issues only arising when it needs to transcode some video because of browser's unsupported codecs. In this case you can also use this plugin to queue your videos and have them play in a desktop player that you like.
Another benefit is being in total control of your playlist queue.
You may also enjoy the controls and experience that some desktop players offer.

## Instalation

### Option 1 — Automatic (recommended)

    In Stash go to Settings → Plugins → Add Source and enter:
    https://theuser9839.github.io/plugins/main/index.yml
    Find Universal Media Launcher in the plugin browser and click Install

### Option 2 — Manual

    Download this repository (Code → Download ZIP) and extract it
    Place the UniversalMediaLauncher folder inside Stash plugins directory.

## How to Use: Its very easy!
1. Go to your Stash Settings -> Plugins.
2. Find Universal Media Launcher and configure the application paths.
3. Navigate to a Stash page with scenes or galleries, such as Galleries or Scenes, or into a specific Performer/Studio.
4. Locate the **Universal Media Launcher** picker toggle icon (🚀 it's a rocket!) on the right of the stash toolbar before the zoom slider.
5. Click the rocket to activate picking mode, it will render `+` badges to card thumbnails and a widget on the bottom right.
6. Click the '+' on the scenes or galleries you want to save into the playlists.
7. Scenes and galleries have different playlists. You will see the widget updating each playlist count.
8. Click the floating widget icons on the bottom right of your screen to launch the desired queue in your selected app.
9. At any time you can unticked a ticked item for it to be removed from the playlist. Or you can clear the entire playlist with X icons-
10. Closing the widget or toggling picking mode off will clean the virtual directories if you configured that way in the plugin settings.

## Screenshots
This is the Galleries tab of stash view the plugin toggle picker activated and 3 galleries already selected.

![UniversalMediaLauncherPreview](/frontend/assets/UniversalMediaLauncher_screenshot.png)

Now an example of what happens when you open the galleries with a desktop app, FastStone in this case:

![FastStone_viewer_sample_screenshot](/frontend/assets/fastStone_viewer_sample_screenshot.png)


## Disclaimer

I created this plugin using AI, i never coded a python or javascript project before.
I took heavy inspiration in the Stash Multiview plugin by ordureconnoisseur:

     https://github.com/ordureconnoisseur/plugins/tree/main/plugins/multiView

And by heavy inspirantion i mean literally copied it's UI code then had AI worked over that to make the changes i needed. Multiview picker its amazing and looks good.
If you find any bugs, please report them, if you want some more features request them and i will consider them, though i rather keep this minimal.

## Repository Structure
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

## Default Configurations

Universal Media Launcher features native system fallbacks. To change your viewing applications, navigate to **Settings -> Plugins -> Universal Media Launcher** inside Stash and adjust the path strings.

### Windows Setup Examples
#### 1. Default Built-in Applications (No extra software needed)
- **External Image Viewer Application Path**: `explorer` *(Default placeholder. Automatically resolves your queue in sequential `01_Name` directory folders and opens the native Microsoft Photos App).*
- **External Video Player Application Path**: `C:\Windows\System32\wmplayer.exe` *(Bypasses the UWP sandbox to play your scene selections back-to-back in Windows Media Player).*

#### 2. Specialized Media Players 
- **External Image Viewer Application Path**: `C:\Program Files (x86)\FastStone Image Viewer\FSViewer.exe`
- **External Video Player Application Path**: `C:\Program Files\MPV\mpv.exe` *(or VLC / MPC-HC absolute paths)*

### Linux Setup Examples
- **External Image Viewer Application Path**: `viewnior` *(or `feh` / `gwenview`)*
- **External Video Player Application Path**: `mpv` *(or `vlc` / `xdg-open` for system default file managers)*


## Tested Image Viewers

This is just an initial list of what i have tested so far, but most of desktop applications should work. You can let me know if of your tests results and i will update the list eventually.

### Windows
FastStone Viewer ✔️
IrfanView ✔️
XnView MP ✔️

## Tested Video Players

### Windows
MPV ✔️
Media Player Classic ✔️
VLC ✔️
Wmplayer ✔️

### Linux
MPV ✔️

## Roadmap
Maybe add a Playlist Drawer eventually, for users who want to know to the exact contents of the queue at any given time and edit previously added items when not using the same search filters anymore. Probably only if people use the plugin and want it.
