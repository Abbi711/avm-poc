const algosdk = require('algosdk');

const atob = require('atob');
const btoa = require('btoa');
const dotenv = require('dotenv').config()


let indexerServer = `https://testnet-algorand.api.purestake.io/idx2`;
let algodServer = `https://testnet-algorand.api.purestake.io/ps2`;
var indexerToken = {
      'X-API-Key': "Cg6qehffpc37kn9VLLf0eqjRK0R0WGt7giDFIfo5"
    };
    
let indexerPort = '';
let indexerClient =  new algosdk.Indexer(indexerToken, indexerServer, indexerPort);
let algodClient =  new algosdk.Algodv2(indexerToken, algodServer, indexerPort);


const getAppAddress = async function(appId){
    let address = await algosdk.getApplicationAddress(appId)
    console.log(address)
}

//getAppAddress(37707016)

const checkPayment = async function(contract_id){
    let userMnemonic =  process.env.MY_TEST_MNEMONICS
    let userAccount = algosdk.mnemonicToSecretKey(userMnemonic);
    
    let params = await algodClient.getTransactionParams().do();

    var enc = new TextEncoder();
    let appArgs = []
    appArgs.push(enc.encode("P"));
    let noteString = 'Payment worked'
    let note = enc.encode(noteString)
  
    let transaction1 = algosdk.makeApplicationNoOpTxn(userAccount.addr, params,
        contract_id, appArgs, undefined, undefined, undefined, note);

    let signedTx1 = transaction1.signTxn(userAccount.sk)
    algodClient.sendRawTransaction(signedTx1).do()
                                            .then((tx) => console.log(tx))
                                            .catch((err)=> console.log(err))
    
}

//checkPayment(37707016)

const checkAssetCreation = async function(contract_id){
    let userMnemonic =  process.env.MY_TEST_MNEMONICS
    let userAccount = algosdk.mnemonicToSecretKey(userMnemonic);
    
    let params = await algodClient.getTransactionParams().do();

    var enc = new TextEncoder();
    let appArgs = []
    appArgs.push(enc.encode("C"));
    let noteString = 'Asset Creation worked'
    let note = enc.encode(noteString)
  
    let transaction1 = algosdk.makeApplicationNoOpTxn(userAccount.addr, params,
        contract_id, appArgs, undefined, undefined, undefined, note);
  
    let signedTx1 = transaction1.signTxn(userAccount.sk)
    algodClient.sendRawTransaction(signedTx1).do()
                                            .then((tx) => console.log(tx))
                                            .catch((err)=> console.log(err))
    
}

//checkAssetCreation(37707016)

const checkAssetXfer = async function(contract_id){
    let userMnemonic =  process.env.MY_TEST_MNEMONICS
    let userAccount = algosdk.mnemonicToSecretKey(userMnemonic);
    
    let params = await algodClient.getTransactionParams().do();

    var enc = new TextEncoder();
    let appArgs = []
    appArgs.push(enc.encode("X"));
    let noteString = 'Asset Xfer worked'
    let note = enc.encode(noteString)
    let appAssets = [28209999]
    let transaction1 = algosdk.makeApplicationNoOpTxn(userAccount.addr, params,
        contract_id, appArgs, undefined, undefined, appAssets, note);
  
    let signedTx1 = transaction1.signTxn(userAccount.sk)
    algodClient.sendRawTransaction(signedTx1).do()
                                            .then((tx) => console.log(tx))
                                            .catch((err)=> console.log(err))
    
}

//checkAssetXfer(37707016)

const checkMultipleAssetXfer = async function(contract_id){
    let userMnemonic =  process.env.MY_TEST_MNEMONICS
    let userAccount = algosdk.mnemonicToSecretKey(userMnemonic);
    
    let params = await algodClient.getTransactionParams().do();

    var enc = new TextEncoder();
    let appArgs = []
    appArgs.push(enc.encode("M"));
    let noteString = 'Asset Multiple Xfer worked'
    let note = enc.encode(noteString)
    let appAssets = [28209999]
    let appAccts = ['SKHVTWLCUO2PZNJYQBCP34FPEFNYOYQWO4RVDMCMOF75XXQHIQ7WEVYUAE']
    let transaction1 = algosdk.makeApplicationNoOpTxn(userAccount.addr, params,
        contract_id, appArgs, appAccts, undefined, appAssets, note);
  
    let signedTx1 = transaction1.signTxn(userAccount.sk)
    algodClient.sendRawTransaction(signedTx1).do()
                                            .then((tx) => console.log(tx))
                                            .catch((err)=> console.log(err))
    
}

//checkMultipleAssetXfer(37707016)

const checkLoops = async function(contract_id){
    let userMnemonic =  process.env.MY_TEST_MNEMONICS
    let userAccount = algosdk.mnemonicToSecretKey(userMnemonic);
    let extraAccount = 'ZOENMUUAA55HD2TLJ26IQVD5PXKII6V7A6U3RSBX2GJWUX322FO2ITHR7U'
    let params = await algodClient.getTransactionParams().do();

    var enc = new TextEncoder();
    let appArgs = []
    appArgs.push(enc.encode("W"));
    let noteString = 'Loops worked'
    let note = enc.encode(noteString)
  
    let transaction1 = algosdk.makeApplicationNoOpTxn(userAccount.addr, params,
        contract_id, appArgs, undefined, undefined, undefined, note);
    let transaction2 = algosdk.makePaymentTxnWithSuggestedParams(userAccount.addr,
                    extraAccount, 1000000, undefined, note, params);
  
    let txns = [transaction1, transaction2];
    let txgroup = algosdk.assignGroupID(txns);
    let signedTx1 = transaction1.signTxn(userAccount.sk)
    let signedTx2 = transaction2.signTxn(userAccount.sk)

    let signed = []
    signed.push(signedTx1);
    signed.push(signedTx2);

    algodClient.sendRawTransaction(signed).do()
                                            .then((tx) => console.log(tx))
                                            .catch((err)=> console.log(err))
    
}

//checkLoops(37707016)