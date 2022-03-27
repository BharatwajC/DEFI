from brownie import Contract, accounts,config,network,interface
from web3 import Web3


LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local","mainnet-fork"]
FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork","mainnet-fork-dev"]



def get_account(index=None, id=None):

    #   accounts[0]
    # account.add("env")
    # account.load("id")
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT or network.show_active() in FORKED_LOCAL_ENVIRONMENT):     #If the network is developmental
        return accounts[0]
                                               #If the network is testnet
    return accounts.add(config["wallets"]["from_key"])   



