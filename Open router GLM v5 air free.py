from google.colab import files
import requests
import json
import os
from IPython.display import display, Markdown

# API configuration
API_KEY = ""
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Function to upload files
def upload_files():
    print("Please upload markdown files (.md, .markdown):")
    uploaded = files.upload()
    return uploaded

# Function to read file contents
def read_files(uploaded_files):
    file_contents = ""
    for filename, content in uploaded_files.items():
        file_contents += f"\n\n--- File: {filename} ---\n"
        # Convert bytes to string if necessary
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        file_contents += content
    return file_contents

# Function to process with API
def process_with_api(prompt, file_contents):
    # Prepare the full prompt
    full_prompt = f"Please {prompt} based on the following content:\n\n{file_contents}"
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        "stream": True
    }
    
    # Make the API call
    response = requests.post(API_URL, headers=headers, data=json.dumps(data), stream=True)
    
    # Process and display the streaming response
    if response.status_code == 200:
        print("\nProcessing Results:")
        response_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # Remove 'data: ' prefix
                    if line == '[DONE]':
                        break
                    try:
                        chunk = json.loads(line)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            response_text += content
                            # Print character by character to simulate streaming
                            print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        print("\nProcessing completed!")
        return response_text
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Main workflow
def main():
    # Step 1: Upload files
    uploaded_files = upload_files()
    
    if not uploaded_files:
        print("No files uploaded. Exiting.")
        return
    
    # Step 2: Read file contents
    file_contents = read_files(uploaded_files)
    print("\nFiles uploaded successfully!")
    
    # Step 3: Get prompt from user
    prompt = input("\nWhat would you like to do with these files? ")
    
    if not prompt:
        print("No prompt provided. Exiting.")
        return
    
    # Step 4: Process with API
    response = process_with_api(prompt, file_contents)
    
    # Step 5: Display the response as markdown
    if response:
        display(Markdown(response))

# Run the main workflow
if __name__ == "__main__":
    main()
