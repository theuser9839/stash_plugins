import sys
import json
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import launcher

def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"ExternalGalleryViewer: Failed to parse stdin JSON: {str(e)}\n")
        input_data = {}

    # =========================================================================
    # ROBUST TASK DETECTION: Checks Stash's default key AND inline fallback key
    # =========================================================================
    task_name = input_data.get("task")
    if not task_name or task_name == "None":
        task_name = input_data.get("task_name")

    # Final fail-safe: Check what key name was transmitted inside the args payload
    if not task_name or task_name == "None":
        raw_args = input_data.get("args", [])
        raw_args_string = json.dumps(raw_args)
        if '"scenes"' in raw_args_string:
            task_name = "Launch Scene Player"
        else:
            task_name = "Launch External Player"
    # =========================================================================

    sys.stderr.write(f"ExternalGalleryViewer: Verified active task routing target -> '{task_name}'\n")

    raw_args = input_data.get("args", [])
    args_payload = []
    
    # Universal regex string scanner to extract the ID numbers flawlessly
    raw_args_string = json.dumps(raw_args)
    matches = re.findall(r'\b\d+(?:,\d+)*\b', raw_args_string)
    if matches:
        longest_match = max(matches, key=len)
        args_payload = [x.strip() for x in longest_match.split(',') if x.strip().isdigit()]

    sys.stderr.write(f"ExternalGalleryViewer: Extracted item array: {args_payload}\n")

    # =========================================================================
    # SYSTEM ROUTING FORK: Clean task separation based strictly on name
    # =========================================================================
    response = {"status": "error", "output": f"Unknown or unhandled task: '{task_name}'"}

    if task_name == "Launch External Player":
        try:
            response = launcher.open_viewer(args_payload, input_data)
        except Exception as run_err:
            response = {"status": "error", "output": f"Gallery launcher crashed: {str(run_err)}"}
            
    elif task_name == "Launch Scene Player":
        try:
            response = launcher.open_scene_player(args_payload, input_data)
        except Exception as run_err:
            response = {"status": "error", "output": f"Scene launcher crashed: {str(run_err)}"}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
