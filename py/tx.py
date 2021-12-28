from eth_keys.datatypes import PrivateKey
from eth_utils import address
from web3 import Web3
import json
import requests
import time

w3 = Web3(Web3.HTTPProvider('https://bsc.getblock.io/mainnet/?api_key=a37acbf1-2bde-4f29-b4ab-718273792df4'))
myAddress = "0xaF1DADe21ee0FCD7A3A3d8F915847d492A5b5CBF"
myKey = "c9ef018a09840eb549157052b61378b613f2a3fdab2ae626b9498da37270f623"
PancakeSwap = "0x10ed43c718714eb63d5aa57b78b54704e256024e"
tokenaddr = "0xe2604c9561d490624aa35e156e65e590eb749519"

token = Web3.toChecksumAddress(tokenaddr)
contract = w3.eth.contract(address=token,abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+tokenaddr).text)["result"])

def sendTxn(tx):
    signed_txn =  w3.eth.account.sign_transaction(tx,private_key=myKey)
    res = w3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
    txn_receipt = w3.eth.wait_for_transaction_receipt(res)
    print(res)
    return txn_receipt


to = Web3.toChecksumAddress(myAddress)

BNB  = Web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
USDT = Web3.toChecksumAddress("0x55d398326f99059ff775485246999027b3197955")
GM   = Web3.toChecksumAddress("0xe2604c9561d490624aa35e156e65e590eb749519")
address = [BNB,USDT,GM]
amountOut = 10*1_000_000_000_000_000_000
amountIn = 0
# tx = contract.functions.swapETHForExactTokens(45*100000000000,address,to,int(time.time())+120).buildTransaction(
#     {
#         "chainId":56,
#         "nonce":w3.eth.getTransactionCount(myAddress),
#         "value":Web3.toWei(0,"ether"),
#         "gasPrice":w3.eth.gasPrice,
#         "gas":360_0000,
#     }
# )
# gas = w3.eth.estimate_gas({"to":to,"from":PancakeSwap,"value":Web3.toWei(0,"ether")})
# print(gas)





if __name__ == '__main__':

    # amountOutMin = int((50000*1.05))*1_000_000_000_000_000_000 
    # print(amountOutMin)
    
    # wbnbGet = contract.functions.getAmountsOut(amountOutMin,[GM,USDT,BNB]).call()[-1]#[0]/1_000_000_000_000_000_000
    # wbnbPay = Web3.toWei(contract.functions.getAmountsIn(amountOutMin,[BNB,GM]).call()[0],"ether") + 250000*Web3.toWei('6','gwei')/1_000_000_000_000_000_000
    # wbnbPay = (contract.functions.getAmountsIn(amountOutMin,[BNB,GM]).call()[0] + 250000*Web3.toWei('6','gwei'))/1_000_000_000_000_000_000
    # wbnbPay2 = contract.functions.getAmountsIn(amountOutMin,[BNB,GM]).call()[0]#[0]/1_000_000_000_000_000_000
    # print(wbnbGet)
    # print(wbnbPay)
    # print(Web3.toWei(wbnbPay,"ether"))
    # print( Web3.toWei('5','gwei'))
    from operate import Sell,Buy,buildTxn,buildTxnEngine
    # Sell(w3,20000*1_000_000_000_000_000_000 )
    buildTxnEngine(w3,2000*10**18,1)
    # while 1:
    #     buildTxn(w3,2000*10**18,1)
    # Sell(w3,2000*1_000_000_000_000_000_000,0)
    # t = w3.eth.wait_for_transaction_receipt("0x988865c6a50188e28fb04d47029aa134f45f60d60edb9752e1cff2ad107fb80b")
    # greetingEvent = contract.events.Transfer()
    # from web3.logs import IGNORE
    # r = greetingEvent.processReceipt(t,IGNORE)
    # print(t)
