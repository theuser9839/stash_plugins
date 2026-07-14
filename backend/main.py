import sys
import json
import os
import re
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(os.path.dirname(PLUGIN_DIR), "UniversalMediaLauncher.log")

logging.basicConfig(
    filename=str(LOG_FILE_PATH), 
    level=logging.ERROR,  # Captures DEBUG, INFO, WARNING, and ERROR metrics
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UniversalMediaLauncher')

try:
    import launcher
except Exception as import_err:
    sys.stderr.write(f"[UniversalMediaLauncher] [CRITICAL] Failed to load launcher.py sub-module: {str(import_err)}\n")

def main():
    try:
        raw_input = sys.stdin.read()
        logger.info(f"RAW STDIN PAYLOAD RECEIVED FROM STASH:\n{raw_input.strip()}")
        input_data = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"[UniversalMediaLauncher] [ERROR] Failed to read or parse standard input: {str(e)}\n")
        input_data = {}

    # Read the active task name parameter from every potential Stash query slot
    task_name = input_data.get("task")
    if not task_name or task_name == "None":
        task_name = input_data.get("task_name")

    raw_args = input_data.get("args", {})
    args_payload = []
    comma_string = ""
    action_value = ""

    # =========================================================================
    # INTEL_PARSING: Unpacks strings, lists, or dictionary values automatically
    # =========================================================================
    if isinstance(raw_args, dict):
        if "scenes" in raw_args:
            val = raw_args["scenes"]
            comma_string = val if isinstance(val, list) and len(val) > 0 else str(val)
        elif "galleries" in raw_args:
            val = raw_args["galleries"]
            comma_string = val if isinstance(val, list) and len(val) > 0 else str(val)
        elif "action" in raw_args:
            val = raw_args["action"]
            action_value = val if isinstance(val, list) and len(val) > 0 else str(val)

    elif isinstance(raw_args, list):
        for item in raw_args:
            if isinstance(item, dict) and "key" in item:
                key_name = item.get("key")
                val_container = item.get("value", {})
                
                if isinstance(val_container, dict) and "str" in val_container:
                    val_str = str(val_container["str"])
                    if key_name == "scenes":
                        comma_string = val_str
                    elif key_name == "galleries":
                        comma_string = val_str
                    elif key_name == "action":
                        action_value = val_str

    # Turn the comma text block back into an active Python list array: "45,44" -> ['45', '44']
    if comma_string:
        args_payload = [x.strip() for x in comma_string.split(',') if x.strip().isdigit()]

    # =========================================================================
    # TASK RECONSTRUCTION: Deduce target task name based on extracted keys
    # =========================================================================
    if not task_name or task_name == "None" or task_name is None:
        if action_value == "wipe":
            task_name = "Wipe Virtual Folders"
        elif "scenes" in str(raw_args):
            task_name = "Launch Video Player"
        elif "galleries" in str(raw_args):
            task_name = "Launch Image Viewer"

    logger.info(f"Calculated Task Result: '{task_name}' | Parsed Action Handshake: '{action_value or 'None'}' | Parsed IDs Payload: {args_payload}")

    response = {"status": "error", "output": f"Unhandled task parameter: '{task_name}'"}

    # =========================================================================
    # SYSTEM ROUTING FORK
    # =========================================================================
    if task_name == "Wipe Virtual Folders":
        try:
            launcher.clear_previous_virtual_session()
            response = {"status": "success", "output": "Temporary virtual directories cleared successfully."}
        except Exception as e:
            sys.stderr.write(f"[UniversalMediaLauncher] [CRITICAL] Cleanup execution crashed: {str(e)}\n")
            response = {"status": "error", "output": str(e)}

    elif task_name == "Launch Image Viewer":
        try:
            response = launcher.open_viewer(args_payload, input_data)
        except Exception as e:
            sys.stderr.write(f"[UniversalMediaLauncher] [CRITICAL] Gallery launcher crashed: {str(e)}\n")
            response = {"status": "error", "output": str(e)}
            
    elif task_name == "Launch Video Player":
        try:
            response = launcher.open_scene_player(args_payload, input_data)
        except Exception as e:
            sys.stderr.write(f"[UniversalMediaLauncher] [CRITICAL] Video player launcher crashed: {str(e)}\n")
            response = {"status": "error", "output": str(e)}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
