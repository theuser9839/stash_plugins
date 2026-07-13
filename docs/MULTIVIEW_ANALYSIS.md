Here's a technical analysis of the Stash Multiview plugin architecture based on the provided code:

1. **Toolbar Button Injection**
- Implemented by the plugin via `injectFilterBtn()` function
- Creates a button with id 'mv-filter-add-btn' that appears in Stash's UI
- Insertion logic targets specific DOM locations (toolbar groups, filter buttons)
- Framework provides basic UI structure, plugin adds custom button

2. **"+ Overlay Rendering**
- Rendered by `injectFilterBtn()` which creates a button with PLUS_ICON_SVG
- Click handler triggers `addFilterSlot()` to modify the queue
- Visual state changes based on queue status (queued/unchecked)
- Plugin handles both UI rendering and interaction logic

3. **Page Navigation Detection**
- Framework provides 'stash:location' event system
- Plugin listens for navigation events via `PluginApi.Event.addEventListener`
- `onNavigate()` function updates UI state on page changes
- Plugin handles UI updates, framework manages navigation events

4. **Queue Storage**
- Hybrid storage: localStorage (fast cache) + Stash config (authoritative source)
- LocalStorage used for UI rendering (`getQueue()`)
- Stash config accessed via GraphQL mutations (`writeConfigQueue()`)
- Plugin manages synchronization between cache and config

5. **UI Mounting**
- Plugin injects elements at specific DOM locations:
  - Launcher appended to body
  - Buttons inserted into existing UI components
- Framework provides base UI structure (toolbar, scene cards)
- Plugin adds custom components (launcher, filter buttons)

6. **Framework vs Plugin Components**
- Framework provides:
  - Basic UI structure (toolbar, scene cards)
  - Navigation event system
  - DOM manipulation APIs
- Plugin implements:
  - Queue management logic
  - Custom UI components (launcher, filter buttons)
  - Business logic for multiview functionality

**Where ExternalGalleryViewer Would Differ:**
1. Would use Python-based backend for queue management instead of JavaScript
2. Would interact with Stash through different API endpoints
3. UI would be rendered server-side or through different frontend framework
4. Would need different event handling mechanism for navigation detection
5. Would require different storage mechanism (e.g., database instead of localStorage)
6. Would implement plugin registration through Python rather than JavaScript

The Multiview plugin demonstrates a typical Stash plugin architecture where the framework provides the base UI and event system, while the plugin adds custom functionality through DOM manipulation and event handling.


**injectFilterBtn**

injectFilterBtn() creates the #mv-filter-add-btn button and inserts it into the DOM.  

- **File that calls it:** multiView.js (invoked from injectPickingModeToggle() and onNavigate()).  

- **DOM nodes searched:**  
  1. `.filtered-list-toolbar .btn-group` (preferred container)  
  2. `button.filter-button` (fallback container)  
  3. `.mv-picking-toggle-btn` (last fallback)  
  4. Existing `#mv-filter-add-btn` element (to update if already present).  

- **CSS selectors it relies on:**  
  - `.filtered-list-toolbar .btn-group`  
  - `button.filter-button`  
  - `.mv-picking-toggle-btn`  

- **Survives page navigation:** A MutationObserver watches `document.body` for childList changes (subtree) and a `stash:location` event listener triggers `onNavigate()`, which re‑calls `injectFilterBtn()` after a short timeout, ensuring the button is re‑injected whenever the page changes.  

- **Stash events that trigger reinjection:** The `stash:location` event (registered via `PluginApi.Event.addEventListener('stash:location', onNavigate)`).



Here's how Multiview discovers and handles Scene cards:

1. **Scene Card Discovery**  
- Uses selector `.scene-card` to find all scene cards in the DOM  
- For each card, searches for `<a[href*="/scenes/"]>` to identify scene links  
- Extracts scene ID from href using regex `/\/scenes\/(\d+)/`  

2. **Overlay Injection**  
- Creates `<button class="mv-add-btn">` inside each `.scene-card`  
- Positions button absolutely within card (via `card.style.position = 'relative'`)  
- Uses `PLUS_ICON_SVG` as default icon  

3. **Duplicate Prevention**  
- Checks `isQueued(id)` before creating button  
- Only creates button if `!isQueued(id)`  
- Uses `dataset.sceneId` to track existing buttons  

4. **Click Event Attachment**  
- Adds event listener to each button via:  
  ```js
  btn.addEventListener('click', e => {
    e.preventDefault();
    toggleScene(id);
    // Update icon state
  });
  ```  

5. **Icon Update Logic**  
- After `toggleScene(id)`, updates button state:  
  ```js
  btn.innerHTML = isQueued(id) ? CHECK_SVG : PLUS_ICON_SVG;
  btn.classList.toggle('mv-queued', isQueued(id));
  ```  
- Uses `isQueued(id)` to determine current state  

The system ensures all scene cards are processed by observing DOM mutations and re-scanning on page navigation.

