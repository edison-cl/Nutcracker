from eth_keys.datatypes import PrivateKey
from eth_utils import address
from web3 import Web3
import json
import requests
import time

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
myAddress = "0xaF1DADe21ee0FCD7A3A3d8F915847d492A5b5CBF"
myKey = "c9ef018a09840eb549157052b61378b613f2a3fdab2ae626b9498da37270f623"
PancakeSwap = "0x10ed43c718714eb63d5aa57b78b54704e256024e"

PancakeSwap = Web3.toChecksumAddress(PancakeSwap)
contract = w3.eth.contract(address=PancakeSwap,abi=json.loads(requests.get("https://api.bscscan.com/api?module=contract&action=getabi&address="+PancakeSwap).text)["result"])

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
tx = contract.functions.swapETHForExactTokens(45*100000000000,address,to,int(time.time())+120).buildTransaction(
    {
        "chainId":56,
        "nonce":w3.eth.getTransactionCount(myAddress),
        "value":Web3.toWei(0,"ether"),
        "gasPrice":w3.eth.gasPrice,
        "gas":360_0000,
    }
)
# gas = w3.eth.estimate_gas({"to":to,"from":PancakeSwap,"value":Web3.toWei(0,"ether")})
# print(gas)





if __name__ == '__main__':
    # print(sendTxn(tx))
    a = time.time()
    print(contract.functions.getAmountsOut(10000000000000000000,address).call())
    b = time.time()
    print("ok",b-a)