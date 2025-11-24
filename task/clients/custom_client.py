import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        # Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # Create request_data dictionary with messages
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }
        
        # Print request for logging (Step 10)
        print("\n=== REQUEST ===")
        print(f"URL: {self._endpoint}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Body: {json.dumps(request_data, indent=2)}")
        print("===============\n")
        
        # Make POST request
        response = requests.post(
            self._endpoint,
            headers=headers,
            json=request_data
        )
        
        # Print response for logging (Step 10)
        print("\n=== RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("================\n")
        
        # Check status code
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        # Get content from response
        response_json = response.json()
        content = response_json["choices"][0]["message"]["content"]
        
        # Print content
        print(content)
        
        # Return message with assistant role and content
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # Create request_data dictionary with stream enabled
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        
        # Print request for logging (Step 10)
        print("\n=== STREAM REQUEST ===")
        print(f"URL: {self._endpoint}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Body: {json.dumps(request_data, indent=2)}")
        print("======================\n")
        
        # Create empty list to store content snippets
        contents = []
        
        # Create aiohttp.ClientSession using async with
        async with aiohttp.ClientSession() as session:
            # Make POST request using async with
            async with session.post(
                self._endpoint,
                json=request_data,
                headers=headers
            ) as response:
                # Print response status for logging (Step 10)
                print(f"\n=== STREAM RESPONSE (Status: {response.status}) ===")
                
                # Read response line by line
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    # Skip empty lines
                    if not line_str:
                        continue
                    
                    # Check if line starts with 'data: '
                    if line_str.startswith('data: '):
                        data_content = line_str[6:]  # Remove 'data: ' prefix
                        
                        # Check for end of stream
                        if data_content == '[DONE]':
                            print("\n[Stream completed]")
                            break
                        
                        # Parse JSON chunk
                        try:
                            chunk_json = json.loads(data_content)
                            
                            # Extract content from chunk
                            if 'choices' in chunk_json and len(chunk_json['choices']) > 0:
                                delta = chunk_json['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content_chunk = delta['content']
                                    # Print content chunk
                                    print(content_chunk, end="", flush=True)
                                    # Collect in contents array
                                    contents.append(content_chunk)
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
                
                print("\n======================\n")
        
        # Return Message with assistant role and collected content
        full_content = "".join(contents)
        return Message(role=Role.AI, content=full_content)

