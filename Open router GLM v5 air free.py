
from google.colab import files
import requests
import json
from IPython.display import HTML, display, Markdown

# API configuration
API_KEY = ""
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Function to create a scrollable output container
def display_scrollable_output(content, height='400px'):
    """Display content in a scrollable container"""
    scrollable_html = f"""
    <div style="
        max-height: {height};
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
        background-color: #f9f9f9;
    ">
        {content}
    </div>
    """
    display(HTML(scrollable_html))

# Function to process with API
def process_with_api(prompt, file_contents=None):
    """Process with API and return the response"""
    # Prepare the full prompt
    if file_contents:
        full_prompt = f"Please {prompt} based on the following content:\n\n{file_contents}"
    else:
        full_prompt = f"Please {prompt}"
    
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
    
    # Process and return the streaming response
    if response.status_code == 200:
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
                    except json.JSONDecodeError:
                        pass
        return response_text
    else:
        return f"Error: {response.status_code}\n{response.text}"

# Main workflow
def main():
    print("=== GLM-4.5-Air File Processor ===")
    print("1. Upload markdown files (optional)")
    print("   - Click 'Choose Files' to upload files, or")
    print("   - Click 'Cancel' to skip uploading files")
    
    # Step 1: Upload files
    uploaded = files.upload()
    
    # Step 2: Get prompt from user
    prompt = input("\n2. Enter your instructions: ")
    
    # Step 3: Read file contents (if any)
    file_contents = None
    if uploaded:
        file_contents = "\n\n--- Uploaded Files Content ---\n"
        for filename, content in uploaded.items():
            file_contents += f"\n--- File: {filename} ---\n"
            # Convert bytes to string if necessary
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            file_contents += content
    
    # Step 4: Process with API
    print("\n3. Processing your request...")
    response = process_with_api(prompt, file_contents)
    
    # Step 5: Display the response in a scrollable container
    print("\n4. Results:")
    display_scrollable_output(Markdown(response).data, height='500px')

# Run the main workflow
if __name__ == "__main__":
    main()