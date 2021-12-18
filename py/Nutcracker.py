from web3 import Web3
import requests
import json
import time
import os
from threading import Thread
from queue import Queue
from web3.logs import IGNORE
from config import Config

conf = Config()

class BeBot():
    def __init__(self,token):
        with open("method.json","r")as f:
            self.method = json.load(f)
        self.needUpdate = {}
        self.transactionPool = {}
        self.lastTransaction = ""
        self.token = token
        self.web3 = Web3(Web3.HTTPProvider(conf.default.web3Url))
        # self.web3 = Web3(Web3.WebsocketProvider("wss://bsc-ws-node.nariox.org:443"))
        self.contractAddress = Web3.toChecksumAddress(self.token)
        self.contract = self.web3.eth.contract(address=self.contractAddress,abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+self.token).text)["result"])
        self.greetingEvent = self.contract.events.Transfer()
        self.blockFilter = self.web3.eth.filter({"fromBlock":"latest","toBlock":"pending","address":self.contractAddress})
        self.MessageQueue = Queue()
    def getTokenBalance(self,token,address):
        contractAddress = Web3.toChecksumAddress(token)
        contract = self.web3.eth.contract(address=contractAddress,abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+address).text)["result"])
        balance = contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()
        return balance/1_000_000_000_000_000_000
    def getBNBBalance(self,address):
        return self.web3.eth.get_balance(Web3.toChecksumAddress(address))/1_000_000_000_000_000_000
    def getInputData(self,name,data):
        res = os.popen("node ../js/main.js %s %s"%(name,data))
        return json.loads(res.read())
    def getTransaction(self,transactionHash):
        time.sleep(0.005)
        if not self.transactionPool[transactionHash]:
            Elem = [transactionHash,"SELL","","","","","",time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())]
            self.MessageQueue.put(Elem)
            return
        # receipt = self.web3.eth.get_transaction_receipt(transactionHash)
        # result = self.greetingEvent.processReceipt(receipt,IGNORE)
        # data = result[0]
        res = self.web3.eth.get_transaction(transactionHash)
        if res["to"] == self.contractAddress:
            return
        if res["input"][0:10] not in self.method and res["input"][0:10] not in self.needUpdate:
            return
        if self.method[res["input"][0:10]] == "" or self.method[res["input"][0:10]] == "claim":
            return
        if "swap" in self.method[res["input"][0:10]]:
            inputData = self.getInputData(self.method[res["input"][0:10]],res["input"])
            amountIn = 0
            amountOut = 0
            Type = ""
            for item in inputData:
                if "amountIn" in item["name"]  :
                    amountIn = int(item["data"])/1_000_000_000_000_000_000
                if "amountOut" in item["name"]:
                    amountOut = int(item["data"])/1_000_000_000_000_000_000

            if amountOut > amountIn:
                Type = "BUY"
            else:
                Type = "SELL"
            if self.transactionPool[transactionHash]:
                Elem = [transactionHash,Type,res["from"],res["to"],amountOut,res["gas"],res["gas"]*5000000000/1_000_000_000_000_000_000,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())]
                self.MessageQueue.put(Elem)
        
    def handleEvent(self,event):
        transactionHash = event.transactionHash.hex()
        if transactionHash not in self.transactionPool:
            self.transactionPool.update({transactionHash:True})
            Thread(target=self.getTransaction,args=(transactionHash,)).start()
            self.lastTransaction = transactionHash
            # if self.lastTransaction != "":
            #     del self.transactionPool[self.lastTransaction]
        else:
            self.transactionPool.update({transactionHash:False})
    def watch(self):
        while 1:
            try:
                while 1:
                    for event in self.blockFilter.get_new_entries():
                        event = self.handleEvent(event)
                    time.sleep(2)
            except Exception as e:
                if "filter not fund" in str(e):
                    print("Connet Broken")
                else:
                    print(str(e))
                self.blockFilter = self.web3.eth.filter({"fromBlock":"latest","toBlock":"pending","address":self.contractAddress})
    def console(self):
        while 1:
            Elem = self.MessageQueue.get()
            print("TX       :",Elem[0])
            print("TYPE     :",Elem[1])
            print("FROM     :",Elem[2])
            print("TO       :",Elem[3])
            print("OUT      :",Elem[4])
            print("GAS      :",Elem[5])
            print("GAS-VAL  :",Elem[6])
            print("TIME     :",Elem[7])
            print()
    def shutDown(self):
        import os
        input()
        print("Wiwi...Zzzz...")
        os._exit(0)
    def main(self):
        print("Bebot...Bebot...",end="\n\n")
        Thread(target=self.shutDown).start()
        Thread(target=self.watch).start()
        Thread(target=self.console).start()
        


if __name__ == '__main__':
    token = conf.get("default","tokenTransaction")
    bot = BeBot(token)
    bot.main()




