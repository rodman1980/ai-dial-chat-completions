import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    # Step 1.1 & 1.2: Create DialClient and CustomDialClient
    # TODO: Replace 'gpt-4' with actual deployment name from https://ai-proxy.lab.epam.com/openai/models
    deployment_name = "gpt-4"
    
    # You can switch between DialClient and CustomDialClient for testing (step 9)
    client = DialClient(deployment_name)
    # Uncomment to use CustomDialClient (with request/response logging):
    # client = CustomDialClient(deployment_name)
    
    # Step 2: Create Conversation object
    conversation = Conversation()
    
    # Step 3: Get System prompt from console or use default
    print("Enter system prompt (or press Enter to use default):")
    system_prompt_input = input("> ").strip()
    system_prompt = system_prompt_input if system_prompt_input else DEFAULT_SYSTEM_PROMPT
    
    # Add system message to conversation
    system_message = Message(role=Role.SYSTEM, content=system_prompt)
    conversation.add_message(system_message)
    
    print(f"\nSystem prompt set: {system_prompt}")
    print("\nChat started. Type 'exit' to quit.\n")
    
    # Step 4: Infinite loop to get user messages
    while True:
        # Get user input
        print("You: ", end="", flush=True)
        user_input = input().strip()
        
        # Step 5: Check if user wants to exit
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        # Skip empty messages
        if not user_input:
            continue
        
        # Step 6: Add user message to conversation history
        user_message = Message(role=Role.USER, content=user_input)
        conversation.add_message(user_message)
        
        # Step 7: Call appropriate completion method based on stream parameter
        print("Assistant: ", end="", flush=True)
        try:
            if stream:
                # Call stream_completion for streaming responses
                assistant_message = await client.stream_completion(conversation.get_messages())
            else:
                # Call get_completion for complete responses
                assistant_message = client.get_completion(conversation.get_messages())
            
            # Step 8: Add generated message to history
            conversation.add_message(assistant_message)
            
        except Exception as e:
            print(f"\nError: {e}")
            # Remove the user message from history if the request failed
            conversation.messages.pop()


if __name__ == "__main__":
    asyncio.run(start(True))
