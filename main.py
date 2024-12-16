import asyncio
import json
import websockets
from websockets.legacy.protocol import WebSocketCommonProtocol
from websockets.legacy.server import WebSocketServerProtocol
from google.auth import default
from google.auth.transport.requests import Request

HOST = "us-central1-aiplatform.googleapis.com"
SERVICE_URL = f"wss://{HOST}/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent"

DEBUG = False

def get_gcp_token():
    """Get Google Cloud authentication token."""
    credentials, project = default()
    
    # Refresh token if expired
    if not credentials.valid:
        credentials.refresh(Request())
    
    return credentials.token

async def proxy_task(
    client_websocket: WebSocketCommonProtocol, server_websocket: WebSocketCommonProtocol
) -> None:
    try:
        async for message in client_websocket:
            try:
                data = json.loads(message)
                if DEBUG:
                    print("proxying: ", data)
                await server_websocket.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                error_msg = str(e)
                if "RESOURCE_EXHAUSTED" in error_msg:
                    await client_websocket.send(json.dumps({
                        "type": "error",
                        "error": "Resource limit exceeded. Please try again later."
                    }))
                    await client_websocket.close(1011, "Resource exhausted")
                elif "Authentication error" in error_msg:
                    error_details = error_msg.split("Error Details:")[1].strip() if "Error Details:" in error_msg else "Invalid token"
                    await client_websocket.send(json.dumps({
                        "type": "error",
                        "error": f"Authentication failed: {error_details}"
                    }))
                    await client_websocket.close(1008, error_details[:123])
                break
            except Exception as e:
                error_msg = str(e)
                print(f"Error in proxy task: {error_msg}")
                if "RESOURCE_EXHAUSTED" in error_msg:
                    try:
                        await client_websocket.send(json.dumps({
                            "type": "error",
                            "error": "Resource limit exceeded. Please try again later."
                        }))
                    except:
                        pass
                    await client_websocket.close(1011, "Resource exhausted")
                elif "Authentication error" in error_msg:
                    try:
                        error_details = error_msg.split("Error Details:")[1].strip() if "Error Details:" in error_msg else "Invalid token"
                        await client_websocket.send(json.dumps({
                            "type": "error",
                            "error": f"Authentication failed: {error_details}"
                        }))
                    except:
                        pass
                    await client_websocket.close(1008, error_details[:123])
                break
    except Exception as e:
        error_msg = str(e)
        print(f"Error in proxy task: {error_msg}")
        try:
            if "RESOURCE_EXHAUSTED" in error_msg:
                await client_websocket.send(json.dumps({
                    "type": "error",
                    "error": "Resource limit exceeded. Please try again later."
                }))
                await client_websocket.close(1011, "Resource exhausted")
            elif "Authentication error" in error_msg:
                error_details = error_msg.split("Error Details:")[1].strip() if "Error Details:" in error_msg else "Invalid token"
                await client_websocket.send(json.dumps({
                    "type": "error",
                    "error": f"Authentication failed: {error_details}"
                }))
                await client_websocket.close(1008, error_details[:123])
            else:
                await client_websocket.close(1011, error_msg[:123])
        except:
            pass

async def create_proxy(
    client_websocket: WebSocketCommonProtocol, bearer_token: str
) -> None:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        async with websockets.connect(SERVICE_URL, additional_headers=headers) as server_websocket:
            client_to_server = asyncio.create_task(
                proxy_task(client_websocket, server_websocket)
            )
            server_to_client = asyncio.create_task(
                proxy_task(server_websocket, client_websocket)
            )
            try:
                await asyncio.gather(client_to_server, server_to_client)
            except websockets.exceptions.ConnectionClosed:
                pass
    except Exception as e:
        error_msg = str(e)
        print(f"Connection error: {error_msg}")
        if "RESOURCE_EXHAUSTED" in error_msg:
            error_response = {
                "type": "error",
                "error": "Resource limit exceeded. Please try again later.",
                "details": error_msg
            }
            try:
                await client_websocket.send(json.dumps(error_response))
            except:
                pass  # Client might be already disconnected
        await client_websocket.close(1011, "Resource exhausted")

async def handle_client(websocket: WebSocketServerProtocol) -> None:
    try:
        print("New connection...")
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        auth_data = json.loads(auth_message)

        if "bearer_token" in auth_data:
            bearer_token = auth_data["bearer_token"]
        else:
            await websocket.close(1008, "Failed to obtain authentication token")
            return

        await create_proxy(websocket, bearer_token)
    except Exception as e:
        print(f"Error handling client: {e}")

async def main() -> None:
    async with websockets.serve(handle_client, "localhost", 8080):
        print("Running websocket server on localhost:8080...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
