import sys
import json
import os
import urllib.request

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import launcher

def fetch_stash_authoritative_queue():
    """Queries Stash's native configuration database directly from the backend stream"""
    gql_query = '{ configuration { plugins } }'
    req_payload = {"query": gql_query}
    
    # Target your local host instance port layout
    url = "http://localhost:9999/graphql"
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(url, data=json.dumps(req_payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            # Dig into Stash's central plugin database storage node block
            # This extracts the exact string array synchronized from main.js!
            plugins_config = res_json.get("data", {}).get("configuration", {}).get("plugins", {})
            
            # Stash stores it inside your configured multiView config storage slots
            raw_queue_string = plugins_config.get("multiView", {}).get("queue", "[]")
            
            # Re-parse the local database string back into a clean python list array
            parsed_list = json.loads(raw_queue_string)
            if isinstance(parsed_list, list):
                return [str(x) for x in parsed_list if str(x).isdigit()]
    except Exception as err:
        sys.stderr.write(f"ExternalGalleryViewer: Database fetch bypass error: {str(err)}\n")
        
    return []

def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except Exception:
        input_data = {}

    task_name = input_data.get("task")
    if not task_name or task_name == "None":
        task_name = "Launch External Player"
    
    sys.stderr.write(f"ExternalGalleryViewer: Running routing loop verification for task: '{task_name}'\n")

    # CORE ADJUSTMENT: Pull the authoritative array straight from the database 
    # instead of listening to Stash's empty stdin variables!
    args_payload = fetch_stash_authoritative_queue()

    # Print out the verified unpacked results array inside Stash server logs panel
    sys.stderr.write(f"ExternalGalleryViewer: Extracted array payload items: {args_payload}\n")

    response = {"status": "error", "output": f"Unknown task: '{task_name}'"}

    if task_name == "Launch External Player":
        try:
            response = launcher.open_viewer(args_payload, input_data)
        except Exception as run_err:
            response = {"status": "error", "output": f"Launcher execution crashed: {str(run_err)}"}

    print(json.dumps(response))

if __name__ == "__main__":
    main()
