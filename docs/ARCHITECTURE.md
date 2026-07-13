# Architecture

+------------------------------------------------+
|                Stash Web UI                     |
|                                                |
|  JS Plugin                                     |
|  ------------------------------------------    |
|  Toolbar Button                               |
|  Overlay + buttons                            |
|  Drawer                                       |
|  Playlist                                     |
|                                                |
+----------------------|-------------------------+
                       |
                       | GraphQL / Plugin API
                       |
+----------------------v-------------------------+
|             Python Plugin Backend              |
|------------------------------------------------|
| GraphQL queries                               |
| Gallery processing                            |
| Temp directory                                |
| Junctions / Symlinks                          |
| Launch external viewer                        |
+------------------------------------------------+

## Project Principles

- Simplicity over cleverness.
- Keep UI and backend independent.
- Platform-specific code stays isolated.
- Configuration should be explicit.
- Never copy image files.
- Keep temporary data disposable.
- Every feature should be testable in isolation.
- Every commit must leave the plugin in a working state.
- Feature contracts

## Goals

- Launch galleries in an external image viewer.
- Keep the viewer configurable.
- Support Windows and Linux.
- Avoid copying image files.

---

## Components

Frontend
- Toolbar button
- Gallery overlays
- Playlist drawer

Backend
- GraphQL
- Filesystem
- Viewer launcher

Filesystem
- Temporary workspace
- Junctions
- Symlinks

Configuration
- Viewer executable
- Viewer arguments

---
UIManager

↓

Toolbar

GalleryOverlay

PlaylistDock

PlaylistDrawer

-----

Playlist

☑ Keep drawer pinned open

☑ Auto-open after first selection

☑ Remember drawer state

☑ Show badge count

☑ Animate on add

## Data Flow

Gallery Selection

↓

Playlist

↓

Temporary Directory

↓

Launch Viewer

↓

Cleanup

--- folder structure

ExternalGalleryViewer/
│
├── plugin.yml
├── README.md
├── LICENSE
│
├── frontend/
│   ├── main.js
│   ├── main.css
│   ├── toolbar.js
│   ├── galleryOverlay.js
│   ├── playlistDock.js
│   ├── playlistDrawer.js
│   └── playlistManager.js
│
├── backend/
│   ├── main.py
│   ├── launcher.py
│   ├── filesystem.py
│   ├── config.py
│   └── api.py
│
├── docs/
└── tests/