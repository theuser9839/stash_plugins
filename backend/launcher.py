import os
import sys
import shutil
import subprocess
import tempfile
import json
import urllib.request
from stashapi.stashapp import StashInterface

# =========================================================================
# CONFIGURATION TARGETS
# =========================================================================
VIRTUAL_BASE_DIR = os.path.join(tempfile.gettempdir(), "StashVirtualGalleries")

def fetch_stash_custom_viewer_setting():
    """Queries Stash's native plugin settings tree to pull the custom path dynamically"""
    gql_query = '{ configuration { plugins } }'
    req_payload = {"query": gql_query}
    
    url = "http://localhost:9999/graphql"
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(req_payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            plugins_config = res_json.get("data", {}).get("configuration", {}).get("plugins", {})
            
            # Extract the setting out of your ExternalGalleryViewer configuration map
            viewer_config = plugins_config.get("ExternalGalleryViewer", {})
            viewer_path = viewer_config.get("viewer_path", "explorer")
            
            return viewer_path.strip() if viewer_path else "explorer"
    except Exception as err:
        sys.stderr.write(f"ExternalGalleryViewer: Setting fetch lookup failed, falling back to explorer: {str(err)}\n")
        
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
            # WINDOWS: Uses directory junctions to bypass local user access limitations
            subprocess.run(['cmd', '/c', 'mklink', '/j', virtual_target_path, source_real_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # LINUX / MACOS standard symbol linking fallback
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
        sys.stderr.write(f"ExternalGalleryViewer: Raw GraphQL Fetch Error: {str(e)}\n")
        return {}

def open_viewer(gallery_ids, input_data):
    """Core Entrypoint: Resolves gallery paths from database and spawns Windows Explorer."""
    if not gallery_ids:
        return {"status": "success", "output": "Queue payload package was empty."}

    clear_previous_virtual_session()
    links_created_count = 0

    gql_query = """
    query FindGallery($id: ID!) {
        findGallery(id: $id) {
            id
            title
            files {
                path
            }
            folder {
                path
            }
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

            sys.stderr.write(f"ExternalGalleryViewer: Mapping ID {gallery_id} -> Path: {real_folder_path} (Name: {gallery_title})\n")

            if real_folder_path and os.path.exists(real_folder_path):
                if create_shortcut_link(real_folder_path, index, gallery_title):
                    links_created_count += 1
            else:
                sys.stderr.write(f"ExternalGalleryViewer: Path does not exist or is inaccessible: {real_folder_path}\n")

        except Exception as err:
            sys.stderr.write(f"Error compiling properties for ID {gallery_id}: {str(err)}\n")

    if links_created_count == 0:
        return {"status": "error", "output": "No items successfully mapped to disk folders."}

    # =========================================================================
    # DYNAMIC VIEWER PATH EVALUATION
    # =========================================================================
    VIEWER_PATH = fetch_stash_custom_viewer_setting()
    sys.stderr.write(f"ExternalGalleryViewer: Activating viewer target path: '{VIEWER_PATH}'\n")

    try:
        if os.name == 'nt':
            if VIEWER_PATH and VIEWER_PATH != "explorer" and os.path.exists(VIEWER_PATH):
                subprocess.Popen([VIEWER_PATH, VIRTUAL_BASE_DIR])
                sys.stderr.write(f"ExternalGalleryViewer: Launched custom viewer: {VIEWER_PATH}\n")
            else:
                if VIEWER_PATH and VIEWER_PATH != "explorer":
                    sys.stderr.write(f"Warning: Target path not found on disk: {VIEWER_PATH}. Falling back to Explorer.\n")
                subprocess.Popen(f'explorer.exe "{VIRTUAL_BASE_DIR}"', shell=True)
        else:
            subprocess.Popen([VIEWER_PATH, VIRTUAL_BASE_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                         
        return {
            "status": "success", 
            "output": f"Virtual folder populated with {links_created_count} items and launched."
        }
    except Exception as launch_err:
        return {"status": "error", "output": f"Failed to execute path viewer: {str(launch_err)}"}
