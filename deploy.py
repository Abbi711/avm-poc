import os
import base64
import time
from dotenv import load_dotenv
load_dotenv()

from algosdk.v2client import algod, indexer
from algosdk.future import transaction
from algosdk import encoding, account, mnemonic, error
from pyteal import compileTeal, Mode
from contracts import basic_poc

ALGOD_ENDPOINT = "https://testnet-algorand.api.purestake.io/ps2"
ALGOD_TOKEN = "Cg6qehffpc37kn9VLLf0eqjRK0R0WGt7giDFIfo5"
INDEXER_ENDPOINT = "https://testnet-algorand.api.purestake.io/idx2"
INDEXER_TOKEN = "Cg6qehffpc37kn9VLLf0eqjRK0R0WGt7giDFIfo5"

DEV_ACCOUNT_MNEMONICS = os.getenv('MY_DEV_MNEMONICS')
DEVELOPER_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(DEV_ACCOUNT_MNEMONICS)
DEVELOPER_ACCOUNT_ADDRESS = account.address_from_private_key(DEVELOPER_ACCOUNT_PRIVATE_KEY)

TEST_ACCOUNT_MNEMONICS = os.getenv('MY_TEST_MNEMONICS')
TEST_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(TEST_ACCOUNT_MNEMONICS)
TEST_ACCOUNT_ADDRESS = account.address_from_private_key(TEST_ACCOUNT_PRIVATE_KEY)

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
    "x-api-key": ALGOD_TOKEN})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
    "x-api-key": INDEXER_TOKEN})


def wait_for_transaction(transaction_id):
    suggested_params = algod_client.suggested_params()
    algod_client.status_after_block(suggested_params.first + 4)
    result = indexer_client.search_transactions(txid=transaction_id)
    assert len(result['transactions']) == 1, result
    return result['transactions'][0]


def compile_state_manager():
    print("Compiling application...")

    manager_approve_teal_code = compileTeal(
        basic_poc.approval_program(), Mode.Application, version=5)
    compile_response = algod_client.compile(manager_approve_teal_code)
    manager_approve_code = base64.b64decode(compile_response['result'])
    MANAGER_APPROVE_BYTECODE_LEN = len(manager_approve_code)
    MANAGER_APPROVE_ADDRESS = compile_response['hash']

    manager_clear_teal_code = compileTeal(
        basic_poc.clear_program(), Mode.Application, version=5)
    compile_response = algod_client.compile(manager_clear_teal_code)
    manager_clear_code = base64.b64decode(compile_response['result'])
    MANAGER_CLEAR_BYTECODE_LEN = len(manager_clear_code)
    MANAGER_CLEAR_ADDRESS = compile_response['hash']

    print(
        f"State Manager | Approval: {MANAGER_APPROVE_BYTECODE_LEN}/1024 bytes ({MANAGER_APPROVE_ADDRESS}) | Clear: {MANAGER_CLEAR_BYTECODE_LEN}/1024 bytes ({MANAGER_CLEAR_ADDRESS})")

    print()

    return manager_approve_code, manager_clear_code


def deploy_state_manager(manager_approve_code, manager_clear_code):
    print("Deploying state manager application...")

    create_manager_transaction = transaction.ApplicationCreateTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=manager_approve_code,
        clear_program=manager_clear_code,
        global_schema=transaction.StateSchema(num_uints=16, num_byte_slices=0),
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0),
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
    tx_id = algod_client.send_transaction(create_manager_transaction)
    print(tx_id)
    manager_app_id = wait_for_transaction(tx_id)['created-application-index']
    print(
        f"State Manager deployed with Application ID: {manager_app_id} (Txn ID: https://testnet.algoexplorer.io/tx/{tx_id})"
    )

    print()

    return manager_app_id


if __name__ == "__main__":
    print("Starting deployment process...")

    manager_approve_code, manager_clear_code = compile_state_manager()

    manager_app_id = deploy_state_manager(
        manager_approve_code, manager_clear_code)
    
    print(f"State Manager App ID = {manager_app_id}")
    
    print("Deployment completed successfully!")
