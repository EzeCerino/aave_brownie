from operator import le
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import config, network, interface
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    # print(lending_pool)
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # borrowable eth => borrowable dai -- 95%
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth) * 0.95
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # We will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI")
    get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)
    print(
        "you just deposited, borrowed, and repayed everething with Aave, Borwnie and Chainlink"
    )


def repay_all(amount, lending_pool, account):
    approve_erc20(
        amount,
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    print("repayed!")


def get_asset_price(price_feed_addres):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_addres)
    lastest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_lastest_price = Web3.fromWei(lastest_price, "ether")
    print(f"The DAI/ETH last price is {converted_lastest_price}")
    print(f"The ETH/DAI last price is {1/converted_lastest_price}")
    return float(converted_lastest_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You can borrow {available_borrows_eth} worth of ETH.")
    return (float(available_borrows_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("approving ERC20 Token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_lending_pool():
    lending_pool_addresses_prvider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_addresses = lending_pool_addresses_prvider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_addresses)
    return lending_pool
