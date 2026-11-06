import json
import requests

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
COMFYUI_URL = "http://127.0.0.1:8188/prompt"
MODEL_NAME = "llama3.2:1b"  # Your tiny model

# 1. Ask the tiny model to generate a creative image prompt
def generate_prompt():
    system_instruction = (
        "You are an expert stable diffusion prompt engineer. "
        "Write a vivid, highly detailed visual prompt for an image generation model. "
        "Return ONLY the raw prompt text, no pleasantries, quotes, or markdown."
    )
    
    user_query = "Generate a prompt for a futuristic cybernetic samurai in a neon-drenched alleyway."

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_instruction}\n\nTask: {user_query}",
        "stream": False
    }

    print(f"Asking {MODEL_NAME} for a prompt...")
    response = requests.post(OLLAMA_URL, json=payload)
    
    if response.status_code == 200:
        prompt_text = response.json().get("response", "").strip()
        print(f"Generated Prompt: {prompt_text}\n")
        return prompt_text
    else:
        raise Exception(f"Failed to generate prompt from Ollama: {response.text}")

# 2. Inject prompt into ComfyUI workflow and queue it
def queue_comfyui_job(prompt_text):
    # Load your exported ComfyUI API workflow template
    workflow_path = "workflow_api.json"
    if not os.path.exists(workflow_path):
        print(f"Error: Could not find {workflow_path}")
        return

    with open(workflow_path, "r") as f:
        workflow = json.load(f)

    # MODIFY THIS: Change "6" to match your specific CLIP Text Encode node ID from step 2
    PROMPT_NODE_ID = "6"
    
    if PROMPT_NODE_ID in workflow:
        workflow[PROMPT_NODE_ID]["inputs"]["text"] = prompt_text
    else:
        print(f"Warning: Node ID {PROMPT_NODE_ID} not found in workflow template.")

    # Send job to ComfyUI queue
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
    import os
    # 1. Generate text using the 1.2B/tiny model
    new_prompt = generate_prompt()
    
    # 2. Push it straight into ComfyUI
    if new_prompt:
        queue_comfyui_job(new_prompt)