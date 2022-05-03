#!/usr/bin/env python3

import os
from algosdk import v2client
from algosdk.encoding import base64

algod_token  = 'a' * 64
algod_addr   = 'http://192.168.1.142:4001'
algod_client = v2client.algod.AlgodClient(algod_token, algod_addr)

def contains_lsig(txn):
    if 'lsig' in txn:
        return True
    return False

def contains_sc(txn):
    if txn['txn']['type'] == 'appl':
        return True
    return False

def decompile_lsig_to_teal(addr, b64):
    os.system(f"echo \"{b64}\" | base64 -d | goal clerk compile -D - > lsigs/{addr}.teal")
    return True

def decompile_existing_app_to_teal(appid):
    # Removed
    return True

def decompile_app_approval_to_teal(appid, b64):
    os.system(f"echo \"{b64}\" | base64 -d | goal clerk compile -D - > apps/{appid}_approval.teal")
    return True

def decompile_app_clearstate_to_teal(appid, b64):
    os.system(f"echo \"{b64}\" | base64 -d | goal clerk compile -D - > apps/{appid}_clearstate.teal")
    return True

def lsig_exists(addr):
    if os.path.exists(f"lsigs/{addr}.teal"):
        return True
    return False

def sc_exists(appid):
    if os.path.exists(f"apps/{appid}_approval.teal"):
        return True
    return False

def wait_for_next_round(last_round):
    status = algod_client.status_after_block(last_round)
    return status['last-round']

status = algod_client.status()
last_round = status['last-round']

while True:
    block = algod_client.block_info(last_round)
    print(f"Round: {last_round}")
    if 'txns' not in block['block']:
        print(f"Txns: 0")
        last_round = wait_for_next_round(last_round)
        continue
    print(f"Txns: {len(block['block']['txns'])}")

    new_lsigs = 0
    new_apps = 0
    for txn in block['block']['txns']:
        if contains_lsig(txn):
            sender = txn['txn']['snd']
            if not lsig_exists(sender):
                logic_b64 = txn['lsig']['l']
                decompile_lsig_to_teal(sender, logic_b64)
                new_lsigs += 1
        if contains_sc(txn):
            # Existing apps contains the application ID in:
            #   txn['txn']['apid']
            # New apps contain the application ID in:
            #   txn['apid']
            if 'apid' not in txn['txn']:
                appid = txn['apid']
                approval = txn['txn']['apap']
                clearstate = txn['txn']['apsu']
                if not sc_exists(appid):
                    decompile_app_approval_to_teal(appid, approval)
                    decompile_app_clearstate_to_teal(appid, clearstate)
                    new_apps += 1
    if new_lsigs > 0:
        print(f"New Lsigs: {new_lsigs}")
    if new_apps > 0:
        print(f"New Apps: {new_apps}")

    last_round = wait_for_next_round(last_round)

