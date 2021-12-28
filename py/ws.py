import asyncio
import json
import requests
import websockets
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

me = "0xaF1DADe21ee0FCD7A3A3d8F915847d492A5b5CBF".lower()
url = "wss://apis.ankr.com/wss/7c80a4b259bc4dcebc6749bbcd85fb0a/558a59a39b0486f77bc14577140d05a9/binance/full/main"
# url = "wss://dex.binance.org/api/ws/"+me
print(url)

async def get_event():
    async with websockets.connect(url,ssl=ssl_context) as ws:
        # request_data = { "method": "subscribe", "topic": "transfers", "address": "0xaF1DADe21ee0FCD7A3A3d8F915847d492A5b5CBF".upper()}
        # request_data = { "method": "subscribe", "topic": "transfers","address":"a37acbf1-2bde-4f29-b4ab-718273792df4"}
        # request_data = {"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
        request_data = {"jsonrpc": "2.0", "id": 0, "method": "eth_getTransactionByHash", "params": ["0x13a0aa58c39e457642d5235960ffec3e62999c5f884aef25706c45f15b671d08"]}
        await ws.send(json.dumps(request_data))
        subscription_response = await ws.recv()
        print(subscription_response)
        return
        while 1:
            pass
        # you are now subscribed to the event 
        # you keep trying to listen to new events (similar idea to longPolling)
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                print(json.loads(message))
                pass
            except:
                pass
# async def get_event():
#     async with websockets.connect("wss://mainnet.infura.io/ws/v3/7d7f8f033d4848cf96efb52a43f8f460") as websocket_client:
#         request_data = {"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
#         await websocket_client.send(json.dumps(request_data))
#         result = await websocket_client.recv()
#         print(result)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # while True:
    loop.run_until_complete(get_event())