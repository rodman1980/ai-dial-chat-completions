from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # Create Dial client for synchronous requests
        self._client = Dial(
            base_url=DIAL_ENDPOINT,
            api_key=self._api_key
        )
        # Create AsyncDial client for streaming requests
        self._async_client = AsyncDial(
            base_url=DIAL_ENDPOINT,
            api_key=self._api_key
        )

    def get_completion(self, messages: list[Message]) -> Message:
        # Convert messages to dict format for API
        messages_dict = [msg.to_dict() for msg in messages]
        
        # Create chat completions with client
        response = self._client.chat.completions.create(
            deployment_id=self._deployment_name,
            messages=messages_dict
        )
        
        # Check if choices are present
        if not response.choices:
            raise Exception("No choices in response found")
        
        # Get content from response
        content = response.choices[0].message.content
        
        # Print the response
        print(content)
        
        # Return message with assistant role and content
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # Convert messages to dict format for API
        messages_dict = [msg.to_dict() for msg in messages]
        
        # Create chat completions with async client with streaming enabled
        response = await self._async_client.chat.completions.create(
            deployment_id=self._deployment_name,
            messages=messages_dict,
            stream=True
        )
        
        # Create array to collect content chunks
        contents = []
        
        # Make async loop from chunks
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                # Print content chunk
                print(content_chunk, end="", flush=True)
                # Collect it in contents array
                contents.append(content_chunk)
        
        # Print empty row to end streaming output
        print()
        
        # Return Message with assistant role and collected content
        full_content = "".join(contents)
        return Message(role=Role.AI, content=full_content)
