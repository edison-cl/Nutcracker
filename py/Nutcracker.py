from logging import FATAL
from web3 import Web3
import requests
import json
import time
import os
import asyncio
from threading import Thread
from queue import Queue
from web3.logs import IGNORE
from config import Config
from operate import Buy, Clip,buildTxnEngine,trackTxnOBject
import websockets
import ssl
from abi import panabi,bnbabi

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

conf = Config()

class BeBot():
    def __init__(self):
        with open("method.json","r")as f:
            self.method = json.load(f)
        self.needUpdate = {}
        self.transactionPool = {}
        self.lastTransaction = ""
        self.web3 = Web3(Web3.HTTPProvider(conf.default.bsc))
        # self.web3 = Web3(Web3.WebsocketProvider(conf.default.bscWebsocket))
        self.tokenContract = self.web3.eth.contract(address=Web3.toChecksumAddress(conf.address.tokenContract),abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+conf.address.tokenContract).text)["result"])
        # self.greetingEvent = self.contract.events.Transfer()
        # self.bnbContract = self.web3.eth.contract(address=Web3.toChecksumAddress(conf.address.wbnbContract),abi=bnbabi)
        self.MessageQueue = Queue()
        self.EventQueue = Queue()
        self.TaskList = []
        self.StartListen = True
        self.ListenRuning = False
        self.parseEventCount = 45
        self.amountOutMin = 1000*10**18
        self.buyNonce = self.web3.eth.get_transaction_count(conf.address.sender)
        self.startTime = time.time()
        self.panRouterContract = self.web3.eth.contract(address=conf.address.panRouterContract, abi=panabi)  
        self.txnObject = ()
    def getTokenBalance(self,contract):
        try:
            balance = contract.functions.balanceOf(Web3.toChecksumAddress(conf.address.sender)).call()/10**18
            # decimals = contract.functions.decimals().call()
            symbol = contract.functions.symbol().call()
            print("{}: {}       ".format(symbol,balance))
        except:
            pass

    def getBnbBalance(self):
        balance = self.web3.eth.getBalance(Web3.toChecksumAddress(conf.address.sender))/10**18
        print("{}: {}       ".format("BNB",balance))

    def getInputData(self,name,data):
        res = os.popen("node ../js/main.js %s %s"%(name,data))
        return json.loads(res.read())

    def rush(self,data):
        inputData = self.getInputData(self.method[data["input"][0:10]],data["input"])
        for item in inputData:
            # if "amountIn" in item["name"]  :
            #     amountIn = int(item["data"])
            if "amountOut" in item["name"]:
                amountOut = int(item["data"])

        if self.amountOutMin <= amountOut:
            Thread(target=Clip,args=(self.web3,self.amountOutMin)).start()
            print("RUSH HIM !!! Ура !!![{}]".format(data["hash"]))
            self.waitClip()
        else:
            print("BINGO TARGET, BUT THE PRICE IS TOO LOW [{}]".fotmat(data["hash"]))


    def waitClip(self):
        self.StartListen = False
        for _ in range(self.parseEventCount):
            self.EventQueue.put(0)

    async def parseEvent(self):
        async with websockets.connect(conf.default.bscWebsocket,ssl=ssl_context) as ws:
                while 1:
                    hash = self.EventQueue.get()
                    if hash == 0:
                        break
                    request_data = {"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionByHash", "params": [hash]}
                    await ws.send(json.dumps(request_data))
                    message = await asyncio.wait_for(ws.recv(), timeout=5)
                    tx = json.loads(message)["result"]
                    if not tx:
                        continue
                    if tx['blockHash']:
                        continue
                    
                    try:
                        # if tx["input"][0:10] != "0x7ff36ab5":
                        #     continue
                        if tx["input"][-40::] == conf.address.tokenContract[2::]:
                            if self.StartListen:
                                self.rush(tx)
                    except KeyError:
                        pass
                    except Exception as e:
                        if "Transaction with hash" in str(e):
                            pass
                        elif "Could not find any function with matching selector" == str(e):
                            pass
                        else:
                            print(e)

    def parseEventEngine(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while 1:
            if not self.StartListen:
                break
            try:
                loop.run_until_complete(self.parseEvent())
            except:
                pass

    def buildParsePool(self):
        for _ in range(self.parseEventCount):
            Thread(target=self.parseEventEngine).start()
        scanCount = 0
        while 1:
            if not self.ListenRuning:
                continue
            print("EventQueueSize:%s  ScanCount:%s\r"%(self.EventQueue.qsize(),scanCount),end="")
            scanCount += 1
            time.sleep(5)

    async def listenPending(self):
        async with websockets.connect(conf.default.bscWebsocket,ssl=ssl_context) as ws:
            request_data = {"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
            await ws.send(json.dumps(request_data))
            await ws.recv()
            print("-- Ready Listen --")
            # you are now subscribed to the event 
            # you keep trying to listen to new events (similar idea to longPolling)
            self.ListenRuning = True
            while True:
                if not self.StartListen:
                    break
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=60)
                    hash = json.loads(message)['params']['result']
                    self.EventQueue.put(hash)
                except:
                    pass
    def console(self):
        while 1:
            Elem = self.MessageQueue.get()
            amountOut = Elem[4]
            isPending = False
            try:
                self.web3.eth.get_transaction_receipt(Elem[0])
                isPending = False
            except Exception as e:
                print(e)
                isPending = True
            print("Tx         :",Elem[0])
            print("Type       :",Elem[1])
            print("From       :",Elem[2])
            print("To         :",Elem[3])
            print("OutMin     :",amountOut)
            print("Gas        :",Elem[5])
            print("Gas Price  :",Elem[6])
            print("isPending  :",isPending)
            print("Time       :",Elem[7])
            print()
            # if amountOut == "":
            #     continue
            # if 50000*1_000_000_000_000_000_000 >= amountOut and Elem[1] == "Buy":
            #     Thread(target=Clip,args=(self.web3,amountOut)).start()
            #     time.sleep(60)
            # if isPending:
            #     if 950*1_000_000_000_000_000_000 >= amountOut > 900*1_000_000_000_000_000_000 and Elem[1] == "Buy":
            #         Thread(target=Clip,args=(self.web3,amountOut)).start()
            #         time.sleep(300)
    def shutDown(self):
        input()
        print("\n-- Wait For Stop --")
        self.StartListen = False
        self.ListenRuning = False
        for _ in range(self.parseEventCount):
            self.EventQueue.put(0)
        time.sleep(0.5)
        count = 0
        while 1:
            count += 1
            if self.EventQueue.qsize() <= 1:
                break
            time.sleep(1)
            if count == 5:break
        import os
        print("Wiwi...Zzzz...")
        os._exit(0)  
    def prepared(self):
        buildTxnEngine(self.web3,self.amountOutMin,self.buyNonce)
        trackTxnOBject()
        print("\n-- TxnObject Ready --")
        print("\n-- Balance --")
        self.getBnbBalance()
        self.getTokenBalance(self.tokenContract)
    def main(self):
        print("\n-- Prepared --")
        self.prepared()
        print("\n-- BeBot Start Run --",end="\n\n")
        Thread(target=self.shutDown).start()
        Thread(target=self.buildParsePool).start()
        loop = asyncio.get_event_loop()
        while True:
            if not self.StartListen:
                break
            try:
                loop.run_until_complete(self.listenPending())
            except:
                pass
        


if __name__ == '__main__':
    bot = BeBot()
    bot.main()




