# Expandable JSON Structure for AI–Unity Integration

Designing a JSON structure for real-time AI-assisted interactions in Unity requires organizing data into clear sections that can be easily extended. The structure below is divided into logical parts for **Message Log**, **Game Context**, **Active User Interactions**, and **Available Functions**. This modular design makes it easy to add new fields or sections in the future. We also discuss best practices regarding streaming updates and client-server responsibilities.

## Message Log
This section holds the latest exchange between the user and the AI. To conserve the LLM’s context window, only the most recent user message and AI response are stored (rather than the entire chat history). Keeping the log short prevents hitting token limits as conversations grow ([Managing Context in a Conversation Bot with Fixed Token Limits - API - OpenAI Developer Community](https://community.openai.com/t/managing-context-in-a-conversation-bot-with-fixed-token-limits/1093181#:~:text=1,Everything)). If longer context is needed, consider summarizing or truncating older messages.

**Structure**: 
- **role** – indicates speaker (`"user"` or `"assistant"`).  
- **message** – the content of the utterance.

**Example**:  
```json
"message_log": {  
  "user": "How do I open this chest?",  
  "assistant": "It looks locked. You might need a key."  
}
```

*Best Practice:* Always update this with the latest turn. If a conversation needs memory, handle it in the AI backend (e.g. via summarization or retrieval) rather than sending a long log each time.

## Game Context Information
This section provides situational awareness of the game world to the AI. It includes visible objects, UI elements, and relevant text content. Each object or UI element should have a unique reference so the AI can identify it unambiguously. Spatial details (position, orientation) can be included if they aid reasoning, though one must judge if raw coordinates are useful for the LLM. Some developers suggest including full transform data for every object ([Anyone else struggling to use AI in Unity? : r/unity](https://www.reddit.com/r/unity/comments/1g3xijo/anyone_else_struggling_to_use_ai_in_unity/#:~:text=Try%20representing%20the%20scene%20in,every%20object%20in%20a%20scene)), but often it's better to include only what’s relevant (e.g. an object is *in front of* the player or at a certain distance) to avoid overloading the prompt.

**Structure** (organized by categories for clarity):
- **objects_in_view** – an array of world objects the player currently sees. Each object can include:  
  - **id**: Unique identifier (or hierarchical path) for the object.  
  - **name**: Human-readable name or type (e.g., `"Chest"` or `"Key"`).  
  - **attributes**: Any important properties (e.g., `"isLocked": true`).  
  - **position/orientation**: *Optional.* Coordinates or relative direction (if needed for context).  
  - **text**: *Optional.* Text content associated with the object (e.g., text on a sign or note).
- **ui_elements** – an array of UI components currently visible or interacted with. Each entry might include:  
  - **id**: Unique reference for the UI element (e.g., `"Screen/InventoryPanel/CloseButton"` as a path).  
  - **type**: Type of UI element (button, panel, tooltip, etc.).  
  - **state**: Relevant state info (e.g., `"hovered": true` or `"value": 5` for a slider).  
  - **text**: Any visible text (for labels, tooltips, chat boxes, etc.).
- **player_status** – *Optional.* Include player-centric context if needed (e.g., player’s coordinates, health, current scene or area).

**Example**:  
```json
"game_context": {  
  "objects_in_view": [  
    { "id": "obj_42", "name": "Ancient Chest", "isLocked": true, "position": [10,0,5] },  
    { "id": "obj_43", "name": "Silver Key", "position": [8,0,5] }  
  ],  
  "ui_elements": [  
    { "id": "HUD/QuestHint", "type": "text", "text": "Find the key to open the chest" }  
  ]  
}
```

*Best Practices:*  
- **Relevance Filtering**: Include only relevant objects/UI (e.g. those in view or pertinent to the last user action) to keep the JSON concise and focused.  
- **Unique References**: Use stable IDs or path strings so the AI can reference objects reliably across messages.  
- **Spatial Data**: If spatial info is included, ensure it’s in a form the AI can use (raw coordinates may be less meaningful than qualitative descriptors like “to your left”). Consider summarizing spatial relations in natural language if necessary.

## Active User Interactions
This section captures what the player is currently doing, beyond just looking. It can track multiple simultaneous interactions – for example, the user might be *looking at* an object while *holding* another, and also has a UI panel open. Represent each distinct interaction as an entry, so the AI can understand the full context of the player’s focus and actions.

**Structure**: An array of interaction objects, each with:  
- **type** – The kind of interaction (e.g., `"gaze"`, `"select"`, `"manipulating"`, `"UI_focus"`).  
- **target** – A reference to the object or UI element involved (using the same ID or path from the context section).  
- **details** – *Optional.* Additional info about the interaction (e.g., for a drag action, the drag distance; for a UI input, the value being entered).

**Example**:  
```json
"active_interactions": [  
  { "type": "gaze", "target": { "id": "obj_42", "name": "Ancient Chest" } },  
  { "type": "holding", "target": { "id": "obj_43", "name": "Silver Key" } }  
]
``` 

In this example, the user’s crosshair or camera is focused on the chest, and they are holding a key. The AI can infer the player might want to use the key on the chest based on these interactions.

*Best Practices:*  
- Always update this list when the player’s focus or action changes (e.g., new object looked at or selected).  
- Keep it synchronized with the game context (the IDs in interactions should appear in the context if those objects/UI are relevant).  
- Use consistent interaction **type** labels so the AI can learn what each means (for instance, `"gaze"` for look-at target via raycast, `"selected"` for a clicked or highlighted object, etc.).

## Available Functions
This section enumerates the functions or actions the AI can invoke to affect the game or query additional info. It acts as an **API manifest** for the AI. Unity (client) can provide game-specific functions (e.g., open a door, move an object) and the backend might add utility functions (e.g., database queries or general tools), all listed together. By listing multiple functions, the AI can perform more than one operation if needed during a single interaction (calling one after the other). Modern LLM systems support calling functions sequentially before giving a final answer ([Trigger multiple functions simultaneously with Function Calling - API - OpenAI Developer Community](https://community.openai.com/t/trigger-multiple-functions-simultaneously-with-function-calling/328103#:~:text=The%20AI%20can%20call%20multiple,and%20then%20decides%20to%20%E2%80%9Cbing%E2%80%9D)).

**Structure**: An array of function definitions. Each function entry can include:  
- **name** – The function identifier the AI should call (e.g., `"openChest"`).  
- **description** – A brief description of what the function does, useful for the AI to decide when to use it.  
- **parameters** – An object defining the expected parameters and their types/meaning. This acts like a schema for function inputs.  
- **source** – *Optional.* Indicate origin if needed (e.g., `"backend"` or `"client"`) – in most cases this isn’t necessary for the AI, but could be used for debugging or routing the call.

**Example**:  
```json
"available_functions": [  
  {  
    "name": "unlockChest",  
    "description": "Unlocks a chest given a key object ID",  
    "parameters": { "chestId": "string", "keyId": "string" }  
  },  
  {  
    "name": "highlightObject",  
    "description": "Highlights an object in the scene for the player",  
    "parameters": { "objectId": "string" }  
  }  
]
```

Here, the AI knows it can call `unlockChest` (perhaps to script the unlocking action) and `highlightObject` (maybe to draw the player’s attention). If the user asks *"Can you help me open the chest?"*, the AI might call `highlightObject` on the chest and suggest using the key, possibly also calling `unlockChest` if appropriate. The structure supports the AI calling one function, getting result, then another, within one round of interaction if your AI system allows it ([Trigger multiple functions simultaneously with Function Calling - API - OpenAI Developer Community](https://community.openai.com/t/trigger-multiple-functions-simultaneously-with-function-calling/328103#:~:text=The%20AI%20can%20call%20multiple,and%20then%20decides%20to%20%E2%80%9Cbing%E2%80%9D)).

*Best Practices:*  
- Ensure function names and descriptions are clear and cover the actions the AI might need. Avoid overwhelming the AI with too many functions – include only those relevant to the current game context or session.  
- Update this list if available actions change (for example, if the player enters a new mode with different possible actions, the client can send an updated function list).  
- Support the AI making multiple function calls by processing each call sequentially and updating the game state (Unity side) between calls if needed, before the AI formulates a final answer.

## Streaming vs Full JSON Updates
When communicating these JSON structures in real-time, we can either send the **full state** every time or only send **deltas (changes)**. Each approach has trade-offs:

- **Full JSON Updates**: Sending the entire JSON context for each interaction ensures the AI always has complete, up-to-date information. This approach is simpler and avoids relying on the AI’s memory for past state. The downside is potential redundancy and higher bandwidth usage if the context is large. However, if the context (objects in view, etc.) is reasonably sized, this is a reliable method to maintain consistency. It also simplifies the backend, which can treat each request independently without storing previous state.

- **Streaming (Partial Updates)**: In this approach, the client sends only what changed since the last update (e.g., an object moved or a new UI element appeared). This can save bandwidth and processing, especially in very dynamic scenes. The challenge is ensuring the AI retains or reconstructs the full context from these snippets. One would need to either maintain an ongoing aggregated state in the backend or include some memory mechanism. Simply relying on the LLM to remember prior JSON from earlier messages is risky, as its conversation memory may not perfectly retain all details ([Managing Context in a Conversation Bot with Fixed Token Limits - API - OpenAI Developer Community](https://community.openai.com/t/managing-context-in-a-conversation-bot-with-fixed-token-limits/1093181#:~:text=1,Everything)). If using streaming updates, a robust solution is to have the server merge each partial update into the last known full state before feeding it to the AI. This way, the prompt always contains the relevant whole context (recently updated).

*Recommendation:* For most cases, prefer full updates of relevant context each turn for reliability. Use streaming/deltas only if performance profiling shows full JSON updates are a bottleneck, and implement state management carefully if you do.

## Client-Server Role Separation
Maintaining a clear split between the Unity client and the AI backend is crucial:

- **Unity (Client)**: Unity should gather all necessary context (message log, game state info, interactions, and function list) and package it into the JSON. Unity remains the **source of truth** for game state. When the AI suggests an action (via function call or message), Unity should execute those functions or apply changes to the game — but Unity is in control of actually changing the game state.

- **AI Backend (Server)**: The backend (hosting the LLM or AI service) receives the JSON, interprets it, and decides on a response (which could be a conversational answer, a function call, or both). The backend does **not** directly modify the JSON or the game state; it only returns instructions or information. This keeps the AI stateless regarding the game – each turn it relies on the fresh JSON from Unity. The Unity community has found it effective to run the LLM as a separate service and call it from Unity, rather than embedding it directly ([LLM integration in Unity! : r/Unity3D](https://www.reddit.com/r/Unity3D/comments/1956ljr/llm_integration_in_unity/#:~:text=The%20LLM%20runs%20locally%20with,I%20answer%20your%20question)). This separation means the game doesn’t depend on external services for its logic except through this defined JSON interface.

*Best Practices:*  
- Define a clear protocol for requests and responses. Unity sends JSON and expects either a JSON answer or function calls from the AI.  
- Validate and sanitize AI outputs on the Unity side. Since Unity holds authority on game state, it should ensure any action from the AI is safe and valid before applying it (for example, ignore a function call to delete an object that doesn’t exist).  
- Keep the backend as stateless as possible. If needed, the backend can keep a short-term memory of the conversation (for example, the last message or a summary) but it should not be the master record of game state. That way, if the AI restarts or loses context, Unity can simply resend the latest state and nothing is lost.

## Example JSON Structure
Below is an example of the complete JSON payload incorporating all the sections above. This demonstrates how the data comes together for a single interaction cycle:

```json
{
  "message_log": {
    "user": "I found a key. What should I do now?",
    "assistant": "You could try using the key on the locked chest."
  },
  "game_context": {
    "objects_in_view": [
      { "id": "obj_100", "name": "Ancient Chest", "isLocked": true, "position": [12.5, 0, -3.2] },
      { "id": "obj_101", "name": "Silver Key", "position": [0, 1.6, 2] }
    ],
    "ui_elements": [
      { "id": "HUD/MessageLog", "type": "text_box", "text": "\"You picked up a Silver Key.\"" }
    ]
    // ... (could include more context like player_status if needed)
  },
  "active_interactions": [
    { "type": "gaze", "target": { "id": "obj_100", "name": "Ancient Chest" } },
    { "type": "holding", "target": { "id": "obj_101", "name": "Silver Key" } }
  ],
  "available_functions": [
    {
      "name": "unlockChest",
      "description": "Unlocks a chest using a key.",
      "parameters": { "chestId": "string", "keyId": "string" }
    },
    {
      "name": "openChest",
      "description": "Opens an unlocked chest to reveal its contents.",
      "parameters": { "chestId": "string" }
    },
    {
      "name": "highlightObject",
      "description": "Highlights an object in the game world or UI.",
      "parameters": { "objectId": "string" }
    }
  ]
}
```

In this example, the JSON is ready to be sent from Unity to the AI backend. The AI sees that the user asked a question and the context shows a locked chest, a key in hand, and some available actions. The AI might respond by calling the `unlockChest` function with the appropriate IDs (from the context) and then instruct the player to open the chest. Unity would execute the `unlockChest` function (if the key matches, unlock the chest in-game), possibly then receive another function call like `openChest`, execute it, and finally display any message the AI sends. All along, Unity updates the JSON (e.g., the chest’s `isLocked` might become false, and the key might be consumed or removed from view) for the next interaction cycle.

## Conclusion
The above JSON structure is optimized for clarity and expandability. Each section serves a distinct purpose and can be extended independently (for instance, adding more detail to game_context or new interaction types) without breaking the format. By sending context in a structured JSON, the Unity client and AI backend maintain a clean separation of concerns and a shared understanding of the game state. This approach ensures the AI can provide relevant, real-time assistance to the player while Unity remains in control of the game’s world and logic ([LLM integration in Unity! : r/Unity3D](https://www.reddit.com/r/Unity3D/comments/1956ljr/llm_integration_in_unity/#:~:text=The%20LLM%20runs%20locally%20with,I%20answer%20your%20question)).

