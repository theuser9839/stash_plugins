import os
import sys
import shutil
import subprocess
import tempfile
import json
import urllib.request

# =========================================================================
# CONFIGURATION TARGETS
# =========================================================================
# DYNAMIC PATH COUPLING: Python live-fetches these paths directly from your Stash settings!
VIRTUAL_BASE_DIR = os.path.join(tempfile.gettempdir(), "StashVirtualGalleries")

def fetch_stash_custom_setting(setting_key):
    """Queries Stash's native plugin settings tree to pull user paths dynamically"""
    gql_query = '{ configuration { plugins } }'
    req_payload = {"query": gql_query}
    
    url = "http://localhost:9999/graphql"
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(req_payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            plugins_config = res_json.get("data", {}).get("configuration", {}).get("plugins", {})
            
            viewer_config = plugins_config.get("UniversalMediaLauncher", {})
            return viewer_config.get(setting_key, "explorer").strip()
    except Exception as err:
        sys.stderr.write(f"UniversalMediaLauncher: Setting fetch lookup failed for {setting_key}: {str(err)}\n")
        
    return "explorer"

def clear_previous_virtual_session():
    """Wipes out any old shortcuts from your last launch to keep the queue fresh."""
    if os.path.exists(VIRTUAL_BASE_DIR):
        try:
            shutil.rmtree(VIRTUAL_BASE_DIR)
        except Exception as e:
            sys.stderr.write(f"Warning: Could not clear old virtual structure: {str(e)}\n")
    os.makedirs(VIRTUAL_BASE_DIR, exist_ok=True)

def create_shortcut_link(source_real_path, index, gallery_title):
    """Creates a virtual directory junction, renaming sequentially to preserve queue order."""
    clean_title = "".join([c for c in gallery_title if c.isalnum() or c in (' ', '_', '-')]).strip()
    folder_name = f"{index:02d}_{clean_title or 'Gallery'}"
    virtual_target_path = os.path.join(VIRTUAL_BASE_DIR, folder_name)

    try:
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'mklink', '/j', virtual_target_path, source_real_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.symlink(source_real_path, virtual_target_path, target_is_directory=True)
        return True
    except Exception as e:
        sys.stderr.write(f"Failed to bind link shortcut for path {source_real_path}: {str(e)}\n")
        return False

def query_stash_raw_graphql(query, variables=None):
    """Direct, framework-agnostic helper to read properties straight from Stash's native DB"""
    req_payload = {"query": query}
    if variables:
        req_payload["variables"] = variables
        
    url = "http://localhost:9999/graphql"
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(req_payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        sys.stderr.write(f"UniversalMediaLauncher: Raw GraphQL Fetch Error: {str(e)}\n")
        return {}

# =========================================================================
# PIPELINE A: GALLERIES FORK (UNCHANGED)
# =========================================================================
def open_viewer(gallery_ids, input_data):
    """Resolves gallery paths from database and spawns your Image Viewer application."""
    if not gallery_ids:
        return {"status": "success", "output": "Queue payload package was empty."}

    clear_previous_virtual_session()
    links_created_count = 0

    gql_query = """
    query FindGallery($id: ID!) {
        findGallery(id: $id) {
            id
            title
            files { path }
            folder { path }
        }
    }
    """

    for index, gallery_id in enumerate(gallery_ids, start=1):
        try:
            res_json = query_stash_raw_graphql(gql_query, {"id": str(gallery_id)})
            gallery_node = res_json.get("data", {}).get("findGallery") or {}

            real_folder_path = None
            gallery_title = gallery_node.get("title") or f"Gallery_{gallery_id}"

            if gallery_node:
                if gallery_node.get("folder") and gallery_node["folder"].get("path"):
                    real_folder_path = gallery_node["folder"]["path"]
                elif gallery_node.get("files") and isinstance(gallery_node["files"], list) and len(gallery_node["files"]) > 0:
                    first_file = gallery_node["files"][0]
                    if first_file.get("path"):
                        real_folder_path = os.path.dirname(first_file["path"])

            if real_folder_path:
                folder_basename = os.path.basename(real_folder_path.rstrip(os.sep))
                gallery_title = folder_basename if folder_basename else f"Gallery_{gallery_id}"

            if real_folder_path and os.path.exists(real_folder_path):
                if create_shortcut_link(real_folder_path, index, gallery_title):
                    links_created_count += 1
        except Exception as err:
            sys.stderr.write(f"Error compiling properties for gallery ID {gallery_id}: {str(err)}\n")

    if links_created_count == 0:
        return {"status": "error", "output": "No gallery items successfully mapped to disk folders."}

    VIEWER_PATH = fetch_stash_custom_setting("viewer_path")
    try:
        if os.name == 'nt' and VIEWER_PATH and VIEWER_PATH != "explorer" and os.path.exists(VIEWER_PATH):
            subprocess.Popen([VIEWER_PATH, VIRTUAL_BASE_DIR])
            sys.stderr.write(f"[DEBUG] [UniversalMediaLauncher] Image viewer process initiated.\n")
        else:
            subprocess.Popen(f'explorer.exe "{VIRTUAL_BASE_DIR}"', shell=True)
        return {"status": "success", "output": "Galleries folder launched."}
    except Exception as e:
        return {"status": "error", "output": f"Failed to execute image viewer: {str(e)}"}

# =========================================================================
# PIPELINE B: SCENES FORK (NEW VIDEO APPLICATION LAUNCHER)
# =========================================================================
def open_scene_player(scene_ids, input_data):
    """Resolves absolute video file paths from database and passes them straight to your media player."""
    if not scene_ids:
        return {"status": "success", "output": "Scene playlist queue payload package was empty."}

    # Fetch your active chosen video player string setting live from the DB on execution tick
    PLAYER_PATH = fetch_stash_custom_setting("player_path")

    if not PLAYER_PATH or PLAYER_PATH == "explorer":
        return {"status": "error", "output": "Please configure your External Video Player Application Path in Stash settings first!"}

    # Target the 'files' schema sub-node to extract absolute video tracks locations
    gql_query = """
    query FindScene($id: ID!) {
        findScene(id: $id) {
            id
            title
            files {
                path
            }
        }
    }
    """

    video_files_to_play = []

    for scene_id in scene_ids:
        try:
            res_json = query_stash_raw_graphql(gql_query, {"id": str(scene_id)})
            scene_node = res_json.get("data", {}).get("findScene") or {}

            if scene_node and scene_node.get("files"):
                # Scenes store their files in an array list wrapper
                for file_node in scene_node["files"]:
                    file_path = file_node.get("path")
                    if file_path and os.path.exists(file_path):
                        video_files_to_play.append(file_path)
                        break # Grab the primary file item and step onto the next scene ID
        except Exception as err:
            sys.stderr.write(f"Error resolving file track for scene ID {scene_id}: {str(err)}\n")

    if not video_files_to_play:
        return {"status": "error", "output": "No video paths successfully found or accessible on local drives."}

    # Execute your favorite media player (MPV, MPC-HC, VLC) passing the entire file track collection at once!
    try:
        if os.path.exists(PLAYER_PATH):
            # Passes the list of file strings directly into the executable process asynchronously
            execution_args = [PLAYER_PATH] + video_files_to_play
            subprocess.Popen(execution_args)
            sys.stderr.write(f"[DEBUG] [UniversalMediaLauncher] Successfully spawned video player process container targeting {len(video_files_to_play)} tracks.\n")
            return {"status": "success", "output": f"Launched video player with {len(video_files_to_play)} items."}
        else:
            sys.stderr.write(f"Error: Configured video player application binary not found on disk: {PLAYER_PATH}\n")
            return {"status": "error", "output": f"Video player path not found on disk: {PLAYER_PATH}"}
    except Exception as launch_err:
        return {"status": "error", "output": f"Video application initialization crashed: {str(launch_err)}"}
