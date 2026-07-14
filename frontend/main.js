(function() {
    'use strict';

    // =========================================================================
    // AUTHORITATIVE PERSISTENT DUAL STORAGE KEYS
    // =========================================================================
    const KEY_GALLERIES = 'ExternalGalleryViewer_galleries_queue';
    const KEY_SCENES    = 'ExternalGalleryViewer_scenes_queue';
    const KEY_PICKING   = 'ExternalGalleryViewer_picking_mode';
    const MAX_QUEUE     = 50;

    // Premium UI Vector Icons Matching Option 1 & A Clean Video Camera Roll
    const ICON_GALLERIES = `<svg xmlns="http://w3.org" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3H3v2M21 3h-2v2M5 21H3v-2M21 21h-2v-2"></path><rect x="6" y="6" width="12" height="12" rx="1"></rect><circle cx="9.5" cy="9.5" r="1"></circle><path d="m6 16 3-3 3 3"></path><path d="m11 15 2.5-2.5 4.5 4.5"></path></svg>`;
    const ICON_SCENES    = `<svg xmlns="http://w3.org" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>`;
    const PLUS_ICON_SVG  = `<svg xmlns="http://w3.org" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 12H18M12 6V18"/></svg>`;
    const CHECK_SVG      = `<svg xmlns="http://w3.org" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12L10 17L19 8"/></svg>`;

    // --- Core Storage Helper Mappings ---
    function resolveStorageKey(type) {
        return type === 'scenes' ? KEY_SCENES : KEY_GALLERIES;
    }

    function getQueue(type) {
        try {
            return JSON.parse(localStorage.getItem(resolveStorageKey(type))) || [];
        } catch (e) {
            return [];
        }
    }


    function setQueue(type, arr) {
        // 1. Commit instantly to your browser window's local tracking state
        const storageKey = type === 'scenes' ? 'ExternalGalleryViewer_scenes_queue' : 'ExternalGalleryViewer_galleries_queue';
        localStorage.setItem(storageKey, JSON.stringify(arr));
        
        // 2. Redraw the count numbers on your screen instantly
        updateAllButtons();
        updateLauncher();

        // 3. HARD-LOCK TO STASH SQLITE DB: Ensures Python can read the values on click!
        if (typeof PluginApi !== 'undefined' && PluginApi.GQL && PluginApi.GQL.configurePlugin) {
            // Determines whether to populate 'galleries_queue' or 'scenes_queue' inside the YML fields
            const dbField = type === 'scenes' ? 'scenes_queue' : 'galleries_queue';
            
            PluginApi.GQL.configurePlugin({
                plugin_id: "ExternalGalleryViewer",
                settings: {
                    [dbField]: JSON.stringify(arr)
                }
            }).catch(err => console.error("ExternalGalleryViewer: Persistent database commit failed:", err));
        }
    }


    function getPickingMode() {
        return localStorage.getItem(KEY_PICKING) === 'true';
    }

    function setPickingMode(val) {
        localStorage.setItem(KEY_PICKING, val ? 'true' : 'false');
        document.body.classList.toggle('mv-picking-mode', val);
        updatePickingToggleButtons();
        updateLauncher();
        if (val) injectCardButtons();
    }

    // =========================================================================
    // AUTHORITATIVE BACKEND STASH DATABASE SYNCHRONIZATION (GraphQL)
    // =========================================================================
    function syncToStashConfig(type, queueArr) {
        if (typeof PluginApi === 'undefined' || !PluginApi.GQL || !PluginApi.GQL.configurePlugin) return;
        
        // Maps the setting value to the exact configuration name key registered in your YML
        const settingField = type === 'scenes' ? 'scenes_queue' : 'galleries_queue';
        
        PluginApi.GQL.configurePlugin({
            plugin_id: "ExternalGalleryViewer",
            settings: {
                [settingField]: JSON.stringify(queueArr)
            }
        }).catch(err => console.error("ExternalGalleryViewer: Persistent database commit failed:", err));
    }

    function syncFromStashConfig() {
        if (typeof PluginApi === 'undefined' || !PluginApi.GQL || !PluginApi.GQL.getConfiguration) return;
        
        PluginApi.GQL.getConfiguration().then(res => {
            const pluginSettings = res?.data?.configuration?.plugins?.ExternalGalleryViewer || {};
            
            try {
                if (pluginSettings.galleries_queue) {
                    localStorage.setItem(KEY_GALLERIES, pluginSettings.galleries_queue);
                }
                if (pluginSettings.scenes_queue) {
                    localStorage.setItem(KEY_SCENES, pluginSettings.scenes_queue);
                }
            } catch (e) {}

            updateAllButtons();
            updateLauncher();
        });
    }

    // =========================================================================
    // DYNAMIC INTERFACE COMPONENT BUILDERS (DOM Injection)
    // =========================================================================
    function injectCardButtons() {
        if (!getPickingMode()) return;

        document.querySelectorAll('.gallery-card, .scene-card').forEach(card => {
            if (card.querySelector('.mv-add-btn')) return;

            const link = card.querySelector('a[href*="/galleries/"], a[href*="/scenes/"]');
            if (!link) return;

            const href = link.getAttribute('href');
            let type = null;
            let id = null;

            if (href.includes('/galleries/')) {
                type = 'galleries';
                const match = href.match(/\/galleries\/(\d+)/);
                if (match) id = match[1];
            } else if (href.includes('/scenes/')) {
                type = 'scenes';
                const match = href.match(/\/scenes\/(\d+)/);
                if (match) id = match[1];
            }

            if (!type || !id) return;

            const currentQueue = getQueue(type);
            const isQueued = currentQueue.includes(id);

            const btn = document.createElement('button');
            btn.className = 'mv-add-btn' + (isQueued ? ' mv-queued' : '');
            btn.dataset.type = type;
            btn.dataset.itemId = id;
            btn.title = `Append ${type === 'scenes' ? 'Scene' : 'Gallery'} to player pipeline`;
            btn.innerHTML = isQueued ? CHECK_SVG : PLUS_ICON_SVG;

            btn.addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();

                const q = getQueue(type);
                const isItemInQueue = q.includes(id);

                if (!isItemInQueue && q.length >= MAX_QUEUE) {
                    alert(`Maximum ${MAX_QUEUE} items allowed inside your ${type} playlist!`);
                    return;
                }

                const updatedQueue = isItemInQueue ? q.filter(x => x !== id) : [...q, id];
                setQueue(type, updatedQueue);
            });

            card.style.position = 'relative';
            card.appendChild(btn);
        });
    }

    function updateButtonState(btn, type, id) {
        const isQueued = getQueue(type).includes(id);
        btn.innerHTML = isQueued ? CHECK_SVG : PLUS_ICON_SVG;
        btn.classList.toggle('mv-queued', isQueued);
    }

    function updateAllButtons() {
        document.querySelectorAll('.mv-add-btn').forEach(btn => {
            const type = btn.dataset.type;
            const id = btn.dataset.itemId;
            if (type && id) updateButtonState(btn, type, id);
        });
    }

    // =========================================================================
    // FLOATING LAUNCHER CORE VIEWPORT PANEL
    // =========================================================================
    function updateLauncher() {
        let el = document.getElementById('mv-launcher');

        if (!getPickingMode()) {
            if (el) el.remove();
            return;
        }

        if (!el) {
            el = document.createElement('div');
            el.id = 'mv-launcher';
            el.innerHTML = `
                <div class="mv-launcher-section">
                    <button id="mv-open-galleries-btn" title="Launch Galleries via External Viewer" class="mv-launch-trigger-btn">${ICON_GALLERIES}</button>
                    <span id="mv-galleries-count" class="mv-launcher-count">0</span>
                    <button id="mv-clear-galleries" title="Clear Gallery Queue" class="mv-clear-trigger-btn">&times;</button>
                </div>
                <div class="mv-launcher-divider"></div>
                <div class="mv-launcher-section">
                    <button id="mv-open-scenes-btn" title="Launch Scenes via External Player" class="mv-launch-trigger-btn">${ICON_SCENES}</button>
                    <span id="mv-scenes-count" class="mv-launcher-count">0</span>
                    <button id="mv-clear-scenes" title="Clear Scene Queue" class="mv-clear-trigger-btn">&times;</button>
                </div>
                <button id="mv-close-launcher-btn" title="Exit Picking Mode" class="mv-close-system-btn">&#x2715;</button>
            `;
            document.body.appendChild(el);

            // Bind Launcher Operational Click Handlers Instantly
            document.getElementById('mv-open-galleries-btn').addEventListener('click', () => dispatchBackendTask('galleries'));
            document.getElementById('mv-clear-galleries').addEventListener('click', () => setQueue('galleries', []));

            document.getElementById('mv-open-scenes-btn').addEventListener('click', () => dispatchBackendTask('scenes'));
            document.getElementById('mv-clear-scenes').addEventListener('click', () => setQueue('scenes', []));

            document.getElementById('mv-close-launcher-btn').addEventListener('click', () => setPickingMode(false));
        }

        // Real-time counter metrics string injection out of localStorage caches
        document.getElementById('mv-galleries-count').textContent = getQueue('galleries').length;
        document.getElementById('mv-scenes-count').textContent = getQueue('scenes').length;
    }

    // =========================================================================
    // GRAPHQL PROCESS EXECUTION DISPATCH HANDLER (FIXED TASK ROUTING)
    // =========================================================================
    async function dispatchBackendTask(type) {
        const currentQueue = getQueue(type);
        if (!currentQueue.length) {
            alert(`Your ${type} queue playlist is currently empty! Add items first.`);
            return;
        }

        const targetPluginId = "ExternalGalleryViewer";
        
        // CRITICAL RE-ALIGNMENT: Matches the explicit task name fields registered inside your YML
        const targetTaskName = type === 'scenes' ? "Launch Scene Player" : "Launch External Player";
        const flatPayloadString = currentQueue.join(',');
        
        console.log(`ExternalGalleryViewer: Sending execution task payload: "${targetTaskName}" with items: ${flatPayloadString}`);

        // Explicitly binds 'task_name' down both the query header and the args map wrapper
        const query = `
            mutation runTask {
                runPluginTask(
                    plugin_id: "${targetPluginId}", 
                    task_name: "${targetTaskName}", 
                    args: [{ key: "${type}", value: { str: "${flatPayloadString}" } }]
                )
            }
        `;

        try {
            const response = await fetch('/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            console.log(`ExternalGalleryViewer: ${type} task execution accepted:`, data);
        } catch (error) {
            console.error(`ExternalGalleryViewer: Failed to clear execution pipe for ${type}:`, error);
        }
    }


    // =========================================================================
    // PICKING CONTROLS INTEGRATION & NAVIGATION WATCHERS
    // =========================================================================
    function updatePickingToggleButtons() {
        const active = getPickingMode();
        document.querySelectorAll('.mv-picking-toggle-btn').forEach(btn => {
            btn.classList.toggle('active', active);
        });
    }

    function togglePickingMode() {
        setPickingMode(!getPickingMode());
    }

    function injectPickingControls() {
        // Top Toolbar Integration Hook
        const navRight = document.querySelector('.navbar-right, .nav-tabs');
        if (navRight && !document.getElementById('mv-picking-nav-btn')) {
            const container = document.createElement('div');
            container.id = 'mv-picking-nav-btn';
            container.className = 'nav-item';
            container.innerHTML = `<button class="btn btn-secondary mv-picking-toggle-btn" title="Toggle ExternalGalleryViewer Picker">${ICON_GALLERIES}</button>`;
            
            container.querySelector('button').addEventListener('click', togglePickingMode);
            navRight.prepend(container);
        }

        // Standalone Floating Fallback Button for isolated navigation grids
        const pagination = document.querySelector('.pagination-container, .col-sm');
        if (!pagination && !document.getElementById('mv-picking-standalone')) {
            const btn = document.createElement('button');
            btn.id = 'mv-picking-standalone';
            btn.className = 'btn btn-secondary mv-picking-toggle-btn';
            btn.title = 'Toggle ExternalGalleryViewer Picker';
            btn.innerHTML = ICON_GALLERIES;
            btn.addEventListener('click', togglePickingMode);
            document.body.appendChild(btn);
        } else if (pagination) {
            const standalone = document.getElementById('mv-picking-standalone');
            if (standalone) standalone.remove();
        }

        updatePickingToggleButtons();
    }

    function onNavigate() {
        document.querySelectorAll('[data-egv-processed]').forEach(el => el.removeAttribute('data-egv-processed'));
        document.querySelectorAll('.mv-add-btn').forEach(el => el.remove());

        setTimeout(() => {
            injectPickingControls();
            injectCardButtons();
            updateLauncher();
            if (getPickingMode()) document.body.classList.add('mv-picking-mode');
        }, 300);
    }

    // Cross-tab Synchronization Layer Hook Loop
    window.addEventListener('storage', e => {
        if (e.key === KEY_GALLERIES || e.key === KEY_SCENES || e.key === KEY_PICKING) {
            if (e.key === KEY_PICKING) {
                const active = localStorage.getItem(KEY_PICKING) === 'true';
                document.body.classList.toggle('mv-picking-mode', active);
                if (!active) {
                    const el = document.getElementById('mv-launcher');
                    if (el) el.remove();
                }
            }
            updateAllButtons();
            updateLauncher();
            updatePickingToggleButtons();
            if (getPickingMode()) injectCardButtons();
        }
    });

    // Native DOM Mutation Listener targeting lazily-loaded grids items extensions
    const observer = new MutationObserver((mutations) => {
        let addedCards = false;
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                if (node.nodeType !== 1) continue;
                if (node.nodeType === 1 && (node.classList?.contains('gallery-card') || node.classList?.contains('scene-card'))) {
                    injectCardButtons();
                    addedCards = true;
                } else if (node.querySelectorAll) {
                    if (node.querySelectorAll('.gallery-card, .scene-card').length > 0) {
                        injectCardButtons();
                        addedCards = true;
                    }
                }
            }
        }
        if (addedCards) updateAllButtons();
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Initial Bootstrap Execution Sequence
    if (typeof PluginApi !== 'undefined' && PluginApi?.Event?.addEventListener) {
        PluginApi.Event.addEventListener('stash:location', onNavigate);
    }

    syncFromStashConfig();
    onNavigate();

/*     if (typeof PluginApi !== 'undefined' && PluginApi.register && PluginApi.register.pluginSetting) {
        PluginApi.register.pluginSetting({
            plugin_id: "ExternalGalleryViewer",
            setting_name: "viewer_path",
            type: "string",
            label: "External Viewer Application Path",
            description: "Provide the absolute system path to your image viewer application executable binary (e.g., C:\\Program Files\\FastStone Image Viewer\\FSViewer.exe). Default is 'explorer'.",
            default_value: "explorer"
        });
        console.log("ExternalGalleryViewer: Native UI plugin path input setting panel registered successfully.");
    } */
    
})();

