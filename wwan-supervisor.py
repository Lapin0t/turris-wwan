from subprocess import run
import time
import json
from ipaddress import ip_interface
import shlex


#--------------------
# rooter/package/rooter/0drivers/rqmi/files/usr/lib/rooter/qmi/connectqmi.sh
# /usr/lib/rooter/qmi/connectqmi.sh

#	echo "Y" > /sys/class/net/$ifname/qmi/raw_ip
#fi
#
#uqmi -d $device --fcc-auth
#sleep 1
#
#log "Waiting for network registration"
#while uqmi -s -d "$device" --get-serving-system | grep '"searching"' > /dev/null; do
#	sleep 5;
#done
#
#log "Starting network $NAPN"
#cid=`uqmi -s -d "$device" --get-client-id wds`
#[ $? -ne 0 ] && {
#	log "Unable to obtain client ID"
#	exit 1
#}
#
#uqmi -s -d "$device" --set-client-id wds,"$cid" --set-ip-family ipv4 > /dev/null
#
#ST=$(uqmi -s -d "$device" --set-client-id wds,"$cid" --start-network ${NAPN:+--apn $NAPN} ${auth:+--auth-type $auth} \
#	${username:+--username $username} ${password:+--password $password} --autoconnect)
#log "Connection returned : $ST"
#
#CONN=$(uqmi -s -d "$device" --get-data-status)
#log "status is $CONN"
#
#CONNZX=$(uqmi -s -d $device --set-client-id wds,$cid --get-current-settings)
#log "GET-CURRENT-SETTINGS is $CONNZX"
#
#T=$(echo $CONN | grep "disconnected")
#if [ -z $T ]; then
#	echo "1" > /tmp/qmigood
#	
#	cid6=`uqmi -s -d "$device" --get-client-id wds`
#	[ $? -ne 0 ] && {
#		log "Unable to obtain client ID"
#		exit 1
#	}


# echo "Y" > /sys/class/net/$ifname/qmi/raw_ip
# uqmi -d $device --fcc-auth
# 


DEV = '/dev/cdc-wdm0'
UQMI = f'/sbin/uqmi -s -d {DEV}'
IFACE = 'wwan0'
APN =  'free'


def run_cmd(cmd):
    #proc = subprocess.run(
    #    shlex.split(cmd.format(**esc, **ENV)),
    #    capture_output=True, text=True)
    #return proc.stdout
    print('CMD: ', shlex.split(cmd))
    return 'PLACEHOLDER'
    

def fix_network():
    print('Stopping network...')
    run_cmd('{UQMI} --stop-network 0xffffffff --autoconnect')
    # TODO check shutdown/delay

    print(f'Starting network, APN: {APN}')
    cid = run_cmd(f'{UQMI} --get-client-id wds')
    run_cmd(f'{UQMI} --set-client-id wds,{cid} --start-network {APN} --auth-type none --autoconnect')

    # TODO: check failure/delay

    conf = run_cmd(f'{UQMI} --set-client-id wds,{cid} --get-current-settings')
    #conf = json.loads(run_cmd('{uqmi} --get-current-settings'))
    #addr = ip_interface('{}/{}'.format(conf['ipv4']['ip'], conf['ipv4']['subnet']))
    #gw = conf['ipv4']['gateway']
    addr_o = ip_interface('{}/{}'.format('192.168.0.10', '255.255.255.0'))
    network = addr_o.network
    address = str(addr_o)

    gateway = '192.168.0.254'

    print(f'IP: {address}, gateway: {gateway}')

    run_cmd(f'/sbin/ip address flush dev {IFACE}')
    run_cmd(f'/sbin/ip route flush dev {IFACE}')

    run_cmd(f'/sbin/ip address add {address} dev {IFACE}')
    run_cmd(f'/sbin/ip route add {gateway} dev {IFACE}')
    run_cmd(f'/sbin/ip route add {network} via {gateway} dev {IFACE}')



fix_network()
