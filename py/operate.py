from requests import NullHandler
from toolz.itertoolz import interleave
from abi import panabi,sellabi
from config import Config
import time
from web3 import Web3
import asyncio
from threading import Thread



conf = Config()


slippage_tolerance = 2

bnb = Web3.toChecksumAddress(conf.address.wbnbContract)
busd = Web3.toChecksumAddress(conf.address.middleTokenContract)
token = Web3.toChecksumAddress(conf.address.tokenContract)
buyAddress = [bnb,busd,token]
gasCount = 250000
txnObject = ()



def buildTxn(web3,amountOutMin,nonce):
    contract = web3.eth.contract(address=conf.address.panRouterContract, abi=panabi)
    sender_address = conf.address.sender
    wbnbPay = (contract.functions.getAmountsIn(amountOutMin,buyAddress).call()[0] + gasCount*web3.toWei('10','gwei'))/10**18
    pancakeswap2_txn = contract.functions.swapExactETHForTokens(
        amountOutMin, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
        buyAddress,
        sender_address,
        (int(time.time()) + 10000)
        ).buildTransaction({
        'from': sender_address,
        'value': web3.toWei(wbnbPay,'ether'),#This is the Token(BNB) amount you want to Swap from
        'gas': gasCount,
        'gasPrice': web3.toWei('6','gwei'),
        'nonce': nonce,
    })
    signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=conf.secret.pricateKey)
    global txnObject
    txnObject = (signed_txn,nonce,contract)

def trackTxnOBject():
    while 1:
        time.sleep(1)
        if txnObject:
            break

def loopBuildTxn(web3,amountOutMin,nonce):
    while 1:
        a = time.time()
        buildTxn(web3,amountOutMin,nonce)
        b = time.time()
        interval = 3-b+a
        if interval < 0:
            interval = 0
        time.sleep(interval)

def buildTxnEngine(web3,amountOutMin,nonce):
    for _ in range(3):
        Thread(target=loopBuildTxn,args=(web3,amountOutMin,nonce)).start()
        time.sleep(2)

def Buy(web3,amountOutMin):
    print(txnObject)
    return
    signed_txn,nonce,contract = txnObject
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_token)
    print("buy success!",web3.toHex(tx_token))
    getToken = contract.functions.getAmountsOut((contract.functions.getAmountsIn(amountOutMin,buyAddress).call()[0] + gasCount*web3.toWei('10','gwei')),buyAddress).call()[-1]
    return getToken,nonce

def Sell(web3,tokenValue,nonce):
    #pancakeswap router
    panRouterContractAddress = conf.address.panRouterContract

    if nonce == 0:
        nonce = web3.eth.get_transaction_count(conf.address.sender)
    else:
        nonce += 1

    #pancakeswap router abi 
    sender_address = conf.address.sender #TokenAddress of holder



    #Get BNB Balance
    # balance = web3.eth.get_balance(sender_address)
    # print(balance)
    
    # humanReadable = web3.fromWei(balance,'ether')
    # print(humanReadable)
    
    #Contract id is the new token we are swaping to
    #contract_id = Web3.toChecksumAddress("0xc9849e6fdb743d08faee3e34dd2d1bc69ea11a51")
    
    #Setup the PancakeSwap contract
    contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi)

    #Abi for Token to sell - all we need from here is the balanceOf & approve function can replace with shortABI
    #Create token Instance for Token
    # sellTokenContract = web3.eth.contract(sellToken, abi=sellabi)

    #Get Token Balance
    # balance = sellTokenContract.functions.balanceOf(sender_address).call()
    # symbol = sellTokenContract.functions.symbol().call()
    # readable = web3.fromWei(balance,'ether')
    # print("Balance: " + str(readable) + " " + symbol)

    #Enter amount of token to sell
    # tokenValue = web3.toWei(input("Enter amount of " + symbol + " you want to sell: "), 'ether')
    # tokenValue = 1000 * 1_000_000_000_000_000_000

    #Approve Token before Selling
    # tokenValue2 = web3.fromWei(tokenValue, 'ether')
    # start = time.time()
    # approve = sellTokenContract.functions.approve(panRouterContractAddress, balance).buildTransaction({
    #             'from': sender_address,
    #             'gasPrice': web3.toWei('5','gwei'),
    #             'nonce': web3.eth.get_transaction_count(sender_address),
    #             })

    # signed_txn = web3.eth.account.sign_transaction(approve, private_key=config.private)
    # tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # print("Approved: " + web3.toHex(tx_token))

    #Wait after approve 10 seconds before sending transaction
    # time.sleep(10)
    # print(f"Swapping {tokenValue2} {symbol} for BNB")
    #Swaping exact Token for ETH 


    address = [token,busd,bnb]
    # address = [sellToken,busd,wbnb]
    amoutOutMin = int(contract.functions.getAmountsOut(tokenValue,address).call()[-1]*0.99)

    pancakeswap2_txn = contract.functions.swapExactTokensForETH(
                tokenValue ,amoutOutMin, 
                address,
                sender_address,
                (int(time.time()) + 1000000)
                ).buildTransaction({
                'from': sender_address,
                'gas':300000,
                'gasPrice': web3.toWei('5','gwei'),
                'nonce': nonce,
                })
    
    signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=conf.secret.pricateKey)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Sold success, tx:",Web3.toHex(tx_token))
    txn_receipt = web3.eth.wait_for_transaction_receipt(tx_token)
    print(web3.toHex(tx_token))

def Clip(web3,amountOutMin):
    tokenValue,nonce = Buy(web3,amountOutMin)
    Sell(web3,tokenValue,nonce)
    import os
    print("Clip Finish.")
    os._exit(0)