from brownie import (
    network,
    accounts,
    config,
    Contract,
)

FORKED_LOCAL_ENVIROMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIROMENTES = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load[id]
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTES
        or network.show_active() in FORKED_LOCAL_ENVIROMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
