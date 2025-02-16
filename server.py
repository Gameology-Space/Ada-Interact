import asyncio
import websockets

async def handler(websocket, path):
    print("Client connected")
    
    # Send a welcome message to the client upon connection.
    await websocket.send("Hello from the server!")
    
    try:
        # Handle incoming messages from the client.
        async for message in websocket:
            print(f"Received: {message}")
            # Check if the message is "AdaV3"
            if message == "AdaV3":
                await websocket.send("hello Ada V3")
            else:
                # Otherwise, echo the message back.
                await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")

async def main():
    # Start a WebSocket server on localhost at port 8999.
    async with websockets.serve(handler, "localhost", 8999):
        # Run forever.
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
