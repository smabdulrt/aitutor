import asyncio
import websockets
import json
from ta_core import TeachingAssistant

# Dictionary to store TA instances, one per connection
tas = {}

async def ta_handler(websocket, path):
    """
    Handles WebSocket connections for the Teaching Assistant.
    One TA instance is created per connection.
    """
    ta = TeachingAssistant()
    tas[websocket] = ta

    # Define a callback for prompt injection
    async def inject_prompt(prompt):
        await websocket.send(json.dumps({
            "type": "prompt",
            "data": prompt
        }))

    ta.set_prompt_injection_callback(inject_prompt)

    try:
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'start_session':
                student_name = data.get('student_name', 'student')
                await ta.greet_on_startup(student_name)
                # Start activity monitoring in the background
                asyncio.create_task(ta.monitor_activity())

            elif data['type'] == 'conversation_update':
                # For now, just reset the activity timer.
                # Later, this will be used for more complex TA logic.
                ta.reset_activity()

            elif data['type'] == 'end_session':
                session_summary = data.get('summary', {})
                await ta.greet_on_close(session_summary)

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed.")
    finally:
        del tas[websocket]

async def main():
    """Starts the Teaching Assistant WebSocket server."""
    server = await websockets.serve(ta_handler, "localhost", 8766)
    print("Teaching Assistant WebSocket server started on ws://localhost:8766")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())