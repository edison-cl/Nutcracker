from web3 import Web3
from abi import panabi
from config import Config
import time

conf = Config()

web3 = Web3(Web3.HTTPProvider(conf.default.bsc))

# print(web3.isConnected())

slippage_tolerance = 2



def Buy(web3,amountOutMin):
    private_key = conf.secret.pricateKey

    token_address = conf.address.tokenContract

    #pancakeswap router
    panRouterContractAddress = conf.address.panRouterContract

    #pancakeswap router abi 
    panabi

    sender_address = conf.address.sender  # my wallet address
    

    balance = web3.eth.get_balance(sender_address)
    # print(balance)

    
    humanReadable = web3.fromWei(balance,'ether')
    # print(humanReadable)

    
    #Contract Address of Token we want to buy
    tokenToBuy = web3.toChecksumAddress(token_address)            #web3.toChecksumAddress("0x6615a63c260be84974166a5eddff223ce292cf3d")
    spend = web3.toChecksumAddress(conf.address.wbnbContract)  #wbnb contract
    
    #Setup the PancakeSwap contract
    contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi)
    

    nonce = web3.eth.get_transaction_count(sender_address)
    

    pancakeswap2_txn = contract.functions.swapExactETHForTokens(
        amountOutMin*1_000_000_000_000_000_000, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
        [spend,tokenToBuy],
        sender_address,
        (int(time.time()) + 10000)
        ).buildTransaction({
        'from': sender_address,
        'value': web3.toWei(0.0005,'ether'),#This is the Token(BNB) amount you want to Swap from
        'gas': 250000,
        'gasPrice': web3.eth.gasPrice,
        'nonce': nonce,
    })
        
    signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=private_key)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(web3.toHex(tx_token))