from subprocess import run
import time
import json
from ipaddress import ip_interface


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


ENV = {
    'uqmi': '/sbin/uqmi -s -d /dev/cdc-wdm0',
    'ifc': 'wwan0',
    'apn': 'free',
}


def run_cmd(cmd, **args):
    esc = {k: shlex.quote(v) for (k, v) in args.items()}
    proc = subprocess.run(
        shlex.split(cmd.format(**esc, **ENV)),
        capture_output=True, text=True)
    return proc.stdout
    

def fix_network():
    print('Stopping network...')
    run_cmd('{uqmi} --stop-network 0xffffffff --autoconnect')
    # TODO check shutdown/delay

    print('Starting network...')
    cid = run_cmd('{uqmi} --get-client-id wds')
    print('QMI Client ID: {cid}, APN: {apn}'.format(cid, apn=ENV['apn']))
    run_cmd('{uqmi} --set-client-id wds,{cid} --start-network --apn {apn} --auth-type none --autoconnect', cid=cid)

    # TODO: check failure/delay

    conf = json.loads(run_cmd('{uqmi} --get-current-settings'))['ipv4']
    addr = ip_interface('{}/{}'.format(conf['ip'], conf['subnet']))
    gw = conf['gateway']

    print('IP: {addr}, gateway: {gw}', ip=addr, gw=gw)

    run_cmd('/sbin/ip address flush dev {ifc}')
    run_cmd('/sbin/ip route flush dev {ifc}')

    run_cmd('/sbin/ip address add {addr} dev {ifc}')
    run_cmd('/sbin/ip route add {gw} dev {ifc}', gw=gw)
    run_cmd('/sbin/ip route add {gw} dev {ifc}', gw=gw)

while 1:
    fix_network()

