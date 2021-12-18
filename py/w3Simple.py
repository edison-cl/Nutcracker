from logging import error
from web3 import Web3
from web3.logs import IGNORE
import requests
import json
import time
import os




with open("method.json","r")as f:method = json.load(f)
needUpdate = {}
address = "0xe2604c9561d490624aa35e156e65e590eb749519"
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
contractAddress = Web3.toChecksumAddress(address)
contract = w3.eth.contract(address=contractAddress,abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+address).text)["result"])
greetingEvent = contract.events.Transfer()






def handle_event(event):
    transactionHash = event.transactionHash.hex()
    getTransaction(transactionHash)
    # if len(result) == 0:
    #     print("pending???")
    # else:
    #     try:
    #         print(result[0]["args"])
    #     except:
    #         print("not fund args")
    # print()


def getTransaction(transactionHash):
    receipt = w3.eth.get_transaction_receipt(transactionHash)
    result = greetingEvent.processReceipt(receipt,IGNORE)
    print(result[0]["data"])
    # print("---------------------------------------------------")
    res = w3.eth.get_transaction(transactionHash)
    print(res)
    # if len(res["input"]) < 32:
    #     return
    if res["to"] == contractAddress:
        # print(transactionHash,"approve")
        # approve
        return
    if method[res["input"][0:10]] == "" or method[res["input"][0:10]] == "claim":
        return
    if res["input"][0:10] not in method and res["input"][0:10] not in needUpdate:
        needUpdate[res["input"][0:10]] = transactionHash
        with open("needUpdate.txt","a+")as f:
            f.write(transactionHash+"\n")
        return
    # print(transactionHash,method[res["input"][0:10]])
    if "swap" in method[res["input"][0:10]]:
        inputData = getInputData(method[res["input"][0:10]],res["input"])
        amountIn = 0
        amountOut = 0
        Type = ""
        for item in inputData:
            if "amountIn" in item["name"]  :
                amountIn = int(item["data"])
            if "amountOut" in item["name"]:
                amountOut = int(item["data"])

        if amountOut > amountIn:
            Type = "BUY"
        else:
            Type = "SELL"
        # if Type == "BUY":
        # if "amountIn" not in inputData :
        print(transactionHash,method[res["input"][0:10]],Type)
        print()
    # else:
        # print(transactionHash,method[res["input"][0:10]],"[NOTIN]")
            # print("method:",method[res["input"][0:10]])
            # print("input :",res["input"])


    
    
    # print(res)
    # with open("output.txt","a+",encoding="utf-8")as f:
    #     f.write(transactionHash+"\n")
    #     f.write("from : ")
    #     f.write(res["from"])
    #     f.write("\n")
    #     f.write("to   : ")
    #     f.write(res["to"])
    #     f.write("\n")
    #     f.write("input: ")
    #     f.write(res["input"])
    #     f.write("\n\n")

def getInputData(name,data):
    res = os.popen("node ../js/main.js %s %s"%(name,data))
    return json.loads(res.read())

def logLoog(eventFilter,poolInterval):
    while 1:
        try:
            while 1:
                for event in eventFilter.get_new_entries():
                    event = handle_event(event)
                time.sleep(poolInterval)
        except Exception as e:
            print(e)
            eventFilter = w3.eth.filter({"fromBlock":"latest","toBlock":"pending","address":contractAddress})
        

def main():
    blockFilter = w3.eth.filter({"fromBlock":"latest","toBlock":"pending","address":contractAddress})
    logLoog(blockFilter,2)
   

# w3.eth.sign_transaction(dict(
#     nonce=w3.eth.get_transaction_count(w3.eth.coinbase),
#     maxFeePerGas=2000000000,
#     maxPriorityFeePerGas=1000000000,
#     gas=100000,
#     to='0x10ed43c718714eb63d5aa57b78b54704e256024e',
#     value=1,
#     data=b'',
# ))
 
print(w3.eth.gasPrice)