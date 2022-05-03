# Algorand Smart Contract/Signature Extraction

This document is intended as a rough guide on how you can pull smart contracts
and smart signatures from an Algorand network. This can be useful if you want
to analyse real-world usecases of them on Mainnet.

First I will explain how to pull all existing contracts from the network, and
then how to monitor a network in real-time for new contracts and signatures.

## Historic Extraction

To retrieve the bulk of all existing smart contracts and smart signatures
you'll want to use this method. Whilst each algod node will contain all of this
data, we're going to use [FlipsideCrypto](https://app.flipsidecrypto.com/) to perform all the heavy lifting and
provide us back with a CSV file of the data we're interested in.

The following SQL will return a list of all the active smart contract IDs,
approval programs, and clear state programs.

```sql
SELECT
	APP_ID,
	JSON_EXTRACT_PATH_TEXT(PARAMS, 'approv') AS "APPROVAL_PROG",
	JSON_EXTRACT_PATH_TEXT(PARAMS, 'clearp') AS "CLEARSTATE_PROG"
FROM algorand.app WHERE CLOSED_AT IS NULL
```

To get all the smart signatures (that have been used at least once), you can
use the following SQL to retrieve a list of addresses and logic.

NOTE: This query is extremely heavy and I've noticed has been limited to
100,000 results. So it would be worth doing this in chunks of time if you
really want all of them.

```sql
SELECT
	ACC.ADDRESS AS ADDRESS,
	JSON_EXTRACT_PATH_TEXT(TXN.TX_MESSAGE, 'lsig.l') AS LOGIC
FROM algorand.account AS ACC
INNER JOIN algorand.transactions AS TXN
WHERE ACC.ADDRESS=TXN.sender AND ACC.WALLET_TYPE='lsig'
GROUP BY ADDRESS, LOGIC
```

## Real-Time Extraction

If you're interested in keeping a copy of all future smart contracts and smart
signatures then you can use this method to monitor the network (using an algod
node) and check each block for new smart contracts and smart signatures being
deployed and used.

The `monitor.py` script will attempt to connect to a local network (sandbox)
and begin watching for new blocks. It won't retrieve existing smart contracts,
only newly deployed ones.

```bash
$ ./monitor.py
Round: 20759485
Txns: 46
Round: 20759486
Txns: 40
New Lsigs: 1
Round: 20759487
Txns: 32
Round: 20759488
Txns: 71
New Apps: 1
Round: 20759489
Txns: 39
```

