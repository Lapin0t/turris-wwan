from datetime import datetime
from ipaddress import ip_interface
import json, shlex, subprocess, time, traceback, sys


# reference: rooter/package/rooter/0drivers/rqmi/files/usr/lib/rooter/qmi/connectqmi.sh


UQMI = ['/sbin/uqmi', '-s', '-d', '/dev/cdc-wdm0']
IFACE = 'wwan0'
APN =  'free'

def log(msg):
    run_cmd('/bin/logger', '-s', '-t', 'wwan-supervisor', msg)

def run_cmd(*cmd, timeout=5, **kw):
    #log(f'DEBUG: CMD={cmd}')
    proc = subprocess.run(cmd, timeout=timeout, **kw)
    return proc
    

def fix_network():
    log('stopping network')
    run_cmd(*UQMI, '--stop-network', '0xffffffff', '--autoconnect')

    log(f'restarting network (apn: {APN})')
    cid = run_cmd(*UQMI, '--get-client-id', 'wds', stdout=subprocess.PIPE, text=True).stdout
    run_cmd(*UQMI, '--set-client-id', f'wds,{cid}', '--start-network', APN, '--auth-type', 'none', '--autoconnect')
    run_cmd(*UQMI, '--set-client-id', f'wds,{cid}', '--release-client-id')
    log('done')

    return

    # TODO: do ipconf?
    #conf = json.loads(run_cmd(f'{UQMI} --set-client-id wds,{cid} --get-current-settings'))

    #gateway = conf['ipv4']['gateway']
    #address = conf['ipv4']['ip']
    #addr_o = ip_interface('{}/{}'.format(conf['ipv4']['ip'], conf['ipv4']['subnet']))
    #network = addr_o.network
    #address = str(addr_o)


    #log(f'INFO: IP={address}, GATEWAY={gateway}')

    #run_cmd(f'/sbin/ip address flush dev {IFACE}')
    #run_cmd(f'/sbin/ip route flush dev {IFACE}')

    #run_cmd(f'/sbin/ip address add {address} dev {IFACE}')
    #run_cmd(f'/sbin/ip route add {network} dev {IFACE}')
    #run_cmd(f'/sbin/ip route add default via {gateway} dev {IFACE}')



while True:
    try:
        status = json.loads(run_cmd(*UQMI, '--get-data-status'))
        if status != 'connected':
            log(f'bad status: {status}')
            fix_network()
    except subprocess.TimeoutExpired:
        log('uqmi timeout, killing everything')
        run_cmd('/usr/bin/killall', '-w', '/sbin/uqmi', timeout=None)
    except Exception:
        for line in traceback.format_exc().splitlines():
            log(f'error: {line}')
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep(3)
