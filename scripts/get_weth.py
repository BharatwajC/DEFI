from scripts.helpful_scripts import get_account
from brownie import interface,network,config
def main():
    get_weth()

def get_weth():
    """
    Mints WETH by depositing ETH
    """    
    pass
    #Depositing ETH into the WETH comtract will mint you WETH token
    # and it will transfer usWETH
    # so we are going to interact with that weth contract 

    #ABI
    #Address

    account = get_account()
    # Now lets go ahead and get WETH contract so import interface
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])

    # why not we use get_contract() here as in smartlottery
    #To make it simpler we used config instead of get_contract


    # we have our address from config
    # we have pur abi from our interface
    #Now lets call the deposit fomction to get weth 

    tx = weth.deposit({"from":account,"value": 0.1*10**18})     # deposit function exist in the weth contract checkout weth kovan etherscan
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx

    # Now to switch back from weth to ETH we can just use the withdraw function
    # so just use weth.withdraw({"from:account"}) 

