from pyteal import *

TXN_TYPE_PAYMENT = Bytes("P")
TXN_TYPE_WHILE_LOOP = Bytes("W")
TXN_TYPE_FOR_LOOP = Bytes("F")
TXN_TYPE_ASSET_CREATION = Bytes("C")
TXN_TYPE_ASSET_OPTIN = Bytes("O")
TXN_TYPE_ASSET_XFER = Bytes("X")
TXN_TYPE_MULTIPLE_ASSET_XFER = Bytes("M")

def approval_program():

    totalFees = ScratchVar(TealType.uint64)
    i = ScratchVar(TealType.uint64)

    on_create = Int(1)
     
    on_delete = Int(1)

    on_closeout = Int(1)

    on_opt_in = Int(1)

    on_pay = Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: Int(3000000),
            }
        ),
        InnerTxnBuilder.Submit(),
        Log(Bytes("Inner payment done")),
        Int(1)
    ])

    on_asset_creation = Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: Bytes('htty'),
                TxnField.config_asset_unit_name: Bytes('HTTY'),
                TxnField.config_asset_total: Int(10000000),
                TxnField.config_asset_decimals: Int(3),
                TxnField.config_asset_url: Bytes('https://google.com/'),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),            
            }
        ),
        InnerTxnBuilder.Submit(),
        App.globalPut(Bytes("Created Asset"), InnerTxn.created_asset_id()),
        Log(Bytes("Inner asset creation done")),
        Int(1),
    ])
 
    on_asset_optin = Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.asset_amount: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
        Log(Bytes("Inner asset optin done")),
        Int(1)
    ])

    on_asset_transfer = Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: Int(5),
            }
        ),
        InnerTxnBuilder.Submit(),
        Log(Bytes("Inner asset xfer done")),
        Int(1)
    ])

    on_multiple_asset_xfer = Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: Int(5),
            }
        ),
        InnerTxnBuilder.Submit(),

        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: Txn.assets[0],
                TxnField.asset_receiver: Txn.accounts[1],
                TxnField.asset_amount: Int(3),
            }
        ),
        InnerTxnBuilder.Submit(),
        Log(Bytes("Inner asset xfer done")),
        Int(1)
    ])

    on_while_loop = Seq([
        i.store(Int(0)),
        totalFees.store(Int(0)),
        While(i.load() < Global.group_size()).Do(Seq([
            totalFees.store(totalFees.load() + Gtxn[i.load()].fee()),
            i.store(i.load() + Int(1))
            ])),
        App.globalPut(Bytes("FeeTotal-While"), totalFees.load()),
        Log(Bytes("While loop check done")),
        Int(1)
    ])

    on_for_loop = Seq([
        totalFees.store(Int(0)),
        For(i.store(Int(0)), i.load() < Global.group_size(), i.store(i.load() + Int(1))).Do(
            totalFees.store(totalFees.load() + Gtxn[i.load()].fee())
        ),
        App.globalPut(Bytes("FeeTotal-For"), totalFees.load()),
        Log(Bytes("For loop check done")),
        Int(1),
    ])

    program = Cond(
        [Txn.application_id() == Int(0),
            on_create],
        [Txn.on_completion() == OnComplete.CloseOut,
            on_closeout],
        [Txn.on_completion() == OnComplete.OptIn,
            on_opt_in],    
        [Txn.on_completion() == OnComplete.DeleteApplication,
            on_delete],     
        [Txn.application_args[0] == TXN_TYPE_PAYMENT,
            on_pay], 
        [Txn.application_args[0] == TXN_TYPE_ASSET_CREATION,
            on_asset_creation],    
        [Txn.application_args[0] == TXN_TYPE_ASSET_OPTIN,
            on_asset_optin],
        [Txn.application_args[0] == TXN_TYPE_ASSET_XFER,
            on_asset_transfer],              
        [Txn.application_args[0] == TXN_TYPE_MULTIPLE_ASSET_XFER,
            on_multiple_asset_xfer],    
        [Txn.application_args[0] == TXN_TYPE_WHILE_LOOP,
            on_while_loop],
        [Txn.application_args[0] == TXN_TYPE_FOR_LOOP,
            on_for_loop],            
    )
    return program

def clear_program():
    return Int(1)

if __name__ == "__main__":

    approve_teal_code = compileTeal(approval_program(), Mode.Application, version=5)
    with open('./build/basic_poc_approval.teal', 'w') as f:
        f.write(approve_teal_code)

    clear_teal_code = compileTeal(clear_program(), Mode.Application, version=5)    
    with open('./build/basic_poc_clear.teal', 'w') as f:
        f.write(clear_teal_code)
