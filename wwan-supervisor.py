from datetime import datetime
from ipaddress import ip_interface
import json, shlex, subprocess, time, traceback, sys


# reference: rooter/package/rooter/0drivers/rqmi/files/usr/lib/rooter/qmi/connectqmi.sh


UQMI = '/sbin/uqmi -s -d /dev/cdc-wdm0'
IFACE = 'wwan0'
APN =  'free'

def log(msg):
    sys.stdout.write('{} {}\n'.format(datetime.now(), msg))

def run_cmd(cmd):
    log(f'DEBUG: CMD={cmd}')
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return proc.stdout
    

def fix_network():
    log('INFO: Stopping network...')
    run_cmd(f'{UQMI} --stop-network 0xffffffff --autoconnect')

    log(f'INFO: Starting network, APN={APN}')
    cid = run_cmd(f'{UQMI} --get-client-id wds')
    run_cmd(f'{UQMI} --set-client-id wds,{cid} --start-network {APN} --auth-type none --autoconnect')

    return

    # TODO: do ipconf?
    conf = json.loads(run_cmd(f'{UQMI} --set-client-id wds,{cid} --get-current-settings'))

    gateway = conf['ipv4']['gateway']
    address = conf['ipv4']['ip']
    addr_o = ip_interface('{}/{}'.format(conf['ipv4']['ip'], conf['ipv4']['subnet']))
    network = addr_o.network
    address = str(addr_o)


    log(f'INFO: IP={address}, GATEWAY={gateway}')

    run_cmd(f'/sbin/ip address flush dev {IFACE}')
    run_cmd(f'/sbin/ip route flush dev {IFACE}')

    run_cmd(f'/sbin/ip address add {address} dev {IFACE}')
    run_cmd(f'/sbin/ip route add {network} dev {IFACE}')
    run_cmd(f'/sbin/ip route add default via {gateway} dev {IFACE}')



while True:
    try:
        status = json.loads(run_cmd(f'{UQMI} --get-data-status'))
        if status != 'connected':
            log(f'INFO: DATA_STATUS={status}')
            fix_network()
    except Exception:
        log('ERROR: <<<')
        traceback.print_exc(file=sys.stdout)
        log('ERROR: >>>')
    except KeyboardInterrupt:
        log('INFO: Exiting...')
    time.sleep(3)
