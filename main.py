from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the incoming data here, e.g., call LangChain functions
            response = f"Echo: {data}"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/status")
async def get_status():
    return {"status": "running"}
