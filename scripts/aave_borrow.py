from scripts.helpful_scripts import get_account
from brownie import config,network,interface, web3
from scripts.get_weth import get_weth
from web3 import Web3

#0.1
amount = web3.toWei(0.1,"ether")



def get_lending_pool():
    # lending pool address may change
    # so there is a lending pool address provider gives us lending poool address of our market

    # getLendingPool() gives us lending pool address
    # so we need ABI and Address of lendingpooladressprovider
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()

    #ABI
    #Address

    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def  approve_erc20(amount, spender, erc20_address, account):
    #ABI
    #Address of the token contract
    #we could create the interface ourselves looking at the ERC20 standard and fiunction

    print("Approving ERC20 token ...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender,amount,{"from":account})
    tx.wait(1)
    print("Approved")
    return tx
    
    
def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth, 
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = lending_pool.getUserAccountData(account.address)        #It returns six useful data health factor, how much liquidity prone etc etc see aave lendingpool documentation  
     # This getUserAccountData is view function so we dont need to spend gas

    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether") 
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"you have {total_collateral_eth} worth of ETH deposited.")
    print(f"you have {total_debt_eth} worth of ETH borrowed.")
    print(f"you can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))  #we have to add this float because we added some of the math 


def get_asset_price(price_feed_address):
    #ABI
    #Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]     #latestRoundData() returns 5 values but the value we want is answer at index 1
    converted_latest_price =  Web3.fromWei(latest_price,"ether")
    print(f"The DAI/ETH price is {converted_latest_price}")         # when printed using direct latest_priec = 341015209779670   which 0.000341015209779670 
    return float(converted_latest_price)


def repay_all(amount,lending_pool,account):
    #The first thing we need to do is call the approve function and approve we are going to pay back
    approve_erc20(Web3.toWei(amount,"ether"),
                lending_pool,
                config["networks"][network.show_active()]["dai_token"],
                account)

    #function repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)            
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"],
                                    amount,
                                    1,
                                    account.address,
                                    {"from":account})
    repay_tx.wait(1)
    print("Repayed!")


def main():
    account = get_account()
    # weth token is actually an erc20 so lets use it as reference instead

    erc20_address = config["networks"][network.show_active()]["weth_token"]
    #get_weth() we dont need it as in kovan we already have 0.1weth

    #but in local dev environment we need to call it 

    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    lending_pool = get_lending_pool()
    print(lending_pool)    

    # lending pool aave
    #we need ABI na address
    #Now we are going to deposit this WETH (ERC20 Token) into this contract like we did in the user interface
    #Now in order to deposit we need to first approve another contract to use your tokensb
    # this is done using approve function

    #Approve sending out ERC20 tokens
 
    approve_erc20(amount, lending_pool.address ,erc20_address ,account)
    # spender is going to be this lending_pool.address
    #lending_poool on whole is the contract


    #lending_pool.deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)       https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool
    tx = lending_pool.deposit(erc20_address,amount,account, 0,{"from":account})
    tx.wait(1)
    print("Deposited!")

    # Now that a collateral is deposited now we can borrow some other asset
    # But ...how much? can we borrow
    #getUserAccountData() this returns many useful functions health factor,liquidity,etc etc

    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    #Deposited:0.1 ETH but we can only borrow 0.0825ETH
    #This is because of liquidation Threshold  see risk parameters


    #Now lets borrow some DAI

    #DAI in terms of ETH
    #so we going to use our pricefeeds

    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])  #dai_eth_price_feed  This will be the address of dai_ETH conversion rate

    #The dai_eth_price = DAI/ETH price is 0.00034101520977967

    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 95% because we dont want to liquidated
    # even the 95% could be 50% as we dont want to get liquidated

    print(f"we are going to borrow {amount_dai_to_borrow} DAI")

    dai_address = config["networks"][network.show_active()]["dai_token"]
    

    #function borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    borrow_tx = lending_pool.borrow(dai_address, 
                Web3.toWei(amount_dai_to_borrow,"ether"),       # in wei
                1,                      # 1 represents stable interest rate
                0,                      # referral code depecrated so 0
                account.address,        # address
                {"from": account})  
    
    borrow_tx.wait(1)

    print(" We borrowed some DAI!!")
    get_borrowable_data(lending_pool,account)


    #Now lets repay this back

    repay_all(amount,lending_pool,account)

    print("You just deposited, borrowed and repayed with Aave,brownie, and chainlink!")
    get_borrowable_data(lending_pool,account)
