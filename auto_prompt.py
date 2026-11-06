import json
import os
import requests

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
COMFYUI_URL = "http://127.0.0.1:8188/prompt"
MODEL_NAME = "lfm3-1.7b"  # Your local Ollama model name

def generate_prompt():
    """Asks your local lfm3-1.7b model for a creative image subject."""
    system_instruction = (
        ""
    )
    
    # You can change this to whatever concept you want to generate
    user_query = "generate a hentai porn image prompt. Cycle between redhead, blonde, goth, being raped, young, lots of cum and ass and tits and blowjobs"

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_instruction}\n\nTask: {user_query}",
        "stream": False
    }

    print(f"Asking {MODEL_NAME} for a prompt...")
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        llm_output = response.json().get("response", "").strip()
        print(f"LLM Generated Subject: {llm_output}\n")
        return llm_output
    else:
        raise Exception(f"Failed to generate prompt from Ollama: {response.text}")

def queue_comfyui_job(llm_subject_text):
    """Injects the text into Node 2 and queues the job in ComfyUI."""
    workflow_path = "workflow_api.json"
    if not os.path.exists(workflow_path):
        print(f"Error: Could not find {workflow_path}. Make sure it's in this folder.")
        return

    with open(workflow_path, "r") as f:
        workflow = json.load(f)

    # Targeting Node ID "2" from your workflow snippet
    NODE_ID = "2"
    
    if NODE_ID in workflow:
        # Preserve your quality tags prefix and append the LLM's generated subject
        quality_prefix = "score_9, score_8_up, score_7_up, "
        final_prompt = quality_prefix + llm_subject_text
        
        workflow[NODE_ID]["inputs"]["text"] = final_prompt
        print(f"Injected final prompt into Node {NODE_ID}:\n--> {final_prompt}\n")
    else:
        print(f"Warning: Node ID {NODE_ID} not found in workflow template.")
        return

    # Send job payload to ComfyUI API
    payload = {"prompt": workflow}
    
    print("Sending job to ComfyUI queue...")
    response = requests.post(COMFYUI_URL, json=payload)
    
    if response.status_code == 200:
        res_data = response.json()
        prompt_id = res_data.get("prompt_id")
        print(f"Successfully queued job! Prompt ID: {prompt_id}")
    else:
        print(f"Failed to queue job in ComfyUI: {response.text}")

if __name__ == "__main__":
    # 1. Generate text using lfm3-1.7b via Ollama
    new_subject = generate_prompt()
    
    # 2. Push it into Node 2 and queue it
    if new_subject:
        queue_comfyui_job(new_subject)