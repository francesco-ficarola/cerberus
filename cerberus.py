#!/usr/bin/python3

# The Cerberus Tool has been developed by Francesco Ficarola.
# The Cerberus Tool is published under the MIT Licence (c) 2022.

import os, re, http.client, urllib.parse, sys, random, string, time, collections, json, argparse, click
from threading import Thread
from queue import Queue
from random import randint

class bcolors:
    VIOLET = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

REGEX_IP_HOST = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)+([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$'

HOST = None
PORT = 443
PATH = '/'
CONNECTIONS = 10000
CONCURRENTS = 3000
METHOD = 'get'
TIMEOUT = 120
NOSSL = False
REFERER = 'example.com'
VERBOSE = False
DATA = None
JSON_PARAMS = '{}'
BLOCKSIZE = 8192

RESULTS_DICT = {}
Q = Queue(CONCURRENTS)

HEADERS = {
    'User-Agent': 'Cerberus/0.1',
    'Referer': REFERER,
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    'Accept-Encoding': 'gzip;q=0,deflate,sdch',
    'Connection': 'keep-alive'
}


def printBanner():
    ascii_banner = ("""
\x1b[1;35m_____________________
__________________________________________
________________________________________________________________
\x1b[31m
 _______ _______  ______ ______  _______  ______ _     _ _______
 |       |______ |_____/ |_____] |______ |_____/ |     | |______
 |_____  |______ |    \_ |_____] |______ |    \_ |_____| ______|
\x1b[1;35m                                                                
________________________________________________________________
__________________________________________
_____________________

\x1b[0;39m
-------------------------------------------------------------------\x1b[1;39m
Stress Testing Tool by Francesco Ficarola (c) MIT 2022
\x1b[0;39m
CERBERUS IS NOT DESIGNED TO PERFORM ILLEGAL ACTIVITIES.
By using this software, you agree to take full responsability
for any damage caused by an irregulare practice of Cerberus.
-------------------------------------------------------------------
""")
    print(ascii_banner)


def makeConnection(path, referer):
    try:
        startres = time.time()

        # Cipher-text traffic (e.g. port 443)
        if PORT == 443 or not NOSSL:
            conn = http.client.HTTPSConnection(HOST, PORT, timeout=int(TIMEOUT), blocksize=BLOCKSIZE)
        else:
            # Clear-text traffic (e.g. port 80)
            conn = http.client.HTTPConnection(HOST, PORT, timeout=int(TIMEOUT), blocksize=BLOCKSIZE)

        HEADERS['referer'] = referer

        # Establishing connection for GET method
        if METHOD == 'get':
            conn.request('get', path, headers=HEADERS)

        # Establishing connection for POST method
        elif METHOD == 'post':
            conn.request('post', path, DATA, HEADERS)

        res = conn.getresponse()
        
        endres = time.time()
        elapres = endres - startres
        
        # Print some details if the verbose param is enabled
        if VERBOSE:
            print('\n' + HOST + ':' + str(PORT) + path + ': HTTP code ' + str(res.status))
            print('Response time: ' + '{:.2f}'.format(elapres))

        return res.status, elapres

    except ConnectionResetError as err:
        if VERBOSE:
            print('\n' + HOST + ':' + str(PORT) + path + ': Connection reset by peer')
        return 'CONN_RESET', 0
    except TimeoutError as err:
        if VERBOSE:
            print('\n' + HOST + ':' + str(PORT) + path + ': Connection timed out')
        return 'SERVER_TIMEOUT', 0  
    except ConnectionRefusedError as err:
        if VERBOSE:
            print('\n' + HOST + ':' + str(PORT) + path + ': Connection refused')
        return 'CONN_REFUSED', 0

    except Exception as err:
        result = 'OTHER_ERRORS'
        if 'timed out' in str(err):
            result = 'CLIENT_TIMEOUT'
        if VERBOSE:
            print('\n' + HOST + ':' + str(PORT) + path + ': ' + str(err))
        return result, 0


def storeResults(status, elapres):
    global RESULTS_DICT
    if not status in RESULTS_DICT:
        RESULTS_DICT[status] = [1, elapres]
    else:
        RESULTS_DICT[status][0] += 1
        if elapres > 0:
            RESULTS_DICT[status][1] += elapres


def doWork():
    while True:
        global Q
        (path, referer) = Q.get()
        status, elapres = makeConnection(path, referer)
        storeResults(status, elapres)
        Q.task_done()


def main():
    global HOST, PORT, PATH, CONNECTIONS, CONCURRENTS, METHOD, HEADERS, TIMEOUT, REFERER, JSON_PARAMS, DATA, NOSSL, BLOCKSIZE, VERBOSE, Q, RESULTS_DICT

    # Get PID to kill with CTRL-C
    pid = os.getpid()

    # Banner
    printBanner()

    # Help and parameters
    parser = argparse.ArgumentParser(description='Cerberus is a stressing tool to test the resilience of your service.', epilog='[IMPORTANT] Unlock your system ulimit before running Cerberus DDoS (e.g. "ulimit -c unlimited -n 65536 -u unlimited") and monitor the connections number (e.g. "watch -n 0,5 \'ss dst <target_ip> | tail -n +2 | wc -l\'")')
    parser.add_argument('target', help='Target host or IP.')
    parser.add_argument('--port', default=PORT, type=int, help='Target port. Default is ' + str(PORT))
    parser.add_argument('--path', default=PATH, help='Use this option if you need to specify a different path with respect to root. Default is ' + PATH + '.')
    parser.add_argument('--conns', default=CONNECTIONS, type=int, help='Specify the total number of connections. Default is ' + str(CONNECTIONS) + '.')
    parser.add_argument('--concs', default=CONCURRENTS, type=int, help='Specify the number of concurrent connections. Default is ' + str(CONCURRENTS) + '.')
    parser.add_argument('--method', default=METHOD, help='Specify the request method: GET or POST. Default is ' + METHOD + '.')
    parser.add_argument('--timeout', default=TIMEOUT, type=int, help='Specify the connection timeout. Default is ' + str(TIMEOUT) + ' seconds.')
    parser.add_argument('--referer', default=REFERER, help='Specify the request referer. Default is ' + REFERER + '.')
    parser.add_argument('--data', default=JSON_PARAMS, help='Specify data in JSON format to be sent through the POST method (e.g. \'{"login": "admin", "pwd": "qwerty", "submit": "Log In"}\'.')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL encryption (e.g. for HTTP instead of HTTPS)')
    parser.add_argument('--block', default=BLOCKSIZE, type=int, help='Specify the blocksize of connections. Default is ' + str(BLOCKSIZE) + '.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode to print details and statistics.')
    args = parser.parse_args()

    # Variables
    HOST = args.target.lower()
    PORT = args.port
    PATH = args.path.lower()
    CONNECTIONS = args.conns
    CONCURRENTS = args.concs
    METHOD = args.method.lower()
    REFERER = args.referer.lower()
    TIMEOUT = args.timeout
    JSON_PARAMS = args.data.lower()
    NOSSL = args.no_ssl
    BLOCKSIZE = args.block
    VERBOSE = args.verbose


    # Method check
    if METHOD == 'post':
        HEADERS['Content-Type'] = 'application/x-www-form-urlencoded'

        # Data check
        if JSON_PARAMS != '{}':
            try:
                DATA = urllib.parse.urlencode(json.loads(JSON_PARAMS))
            except Exception as err:
                print(f'{bcolors.RED}[ERROR] --data param is invalid, please check your JSON input:{bcolors.ENDC}\n')
                print(JSON_PARAMS + '\n')
                sys.exit(1)
        else:
            print()
            if not click.confirm(f'{bcolors.YELLOW}[WARN] You have chosen the POST method but you haven\'t passed any data. Do you want to continue with SSL enabled?{bcolors.ENDC}', default=False):
                sys.exit(1)

    elif METHOD != 'get':
        print(f'{bcolors.RED}[ERROR] Method is invalid, please pass \'get\' or \'post\'! Exit.{bcolors.ENDC}\n')
        sys.exit(1)


    # Host check
    if re.match(REGEX_IP_HOST, HOST):
        print(f'{bcolors.GREEN}Ok, your target is valid since it matchces an IP address or a FQDN: {bcolors.CYAN}' + HOST + f'{bcolors.ENDC}\n')
    else:
        print(f'{bcolors.RED}[ERROR] IP or host invalid, please check your target! Exit.{bcolors.ENDC}\n')
        sys.exit(1)

    # Port check
    if PORT != 443 and not NOSSL:
        if not click.confirm(f'{bcolors.YELLOW}[WARN] You are targeting a port different from 443 (HTTPS), so maybe you\'ve forgotten to add "--no-ssl" option. Do you want to continue with SSL enabled?{bcolors.ENDC}', default=False):
            sys.exit(1)


    # Process start
    start_time = time.time()
    print(f'DoSsing {bcolors.BLUE}' + HOST + f'{bcolors.ENDC} on port {bcolors.BLUE}' + str(PORT) + f'{bcolors.ENDC} with {bcolors.BLUE}' + str(CONCURRENTS) + f'{bcolors.ENDC} concurrent connections for a total of {bcolors.BLUE}' + str(CONNECTIONS) + f'{bcolors.ENDC} requests (timeout = {bcolors.BLUE}' + str(TIMEOUT) + f' seconds{bcolors.ENDC})...\n')
    print('(Please wait for completion or press CTRL-C to interrupt the execution)\n')

    for i in range(CONCURRENTS):
        t = Thread(target=doWork)
        t.daemon = True
        t.start()

    try:
        rndmstr = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        pattern = '?' + rndmstr + '='

        for i in range(CONNECTIONS):
            path = PATH + pattern + str(i)
            referer = rndmstr + str(i) + '.' + REFERER

            Q.put((path, referer))
        Q.join()
    except KeyboardInterrupt:
        os.system('kill -9 ' + str(pid))
        sys.exit(1)

    end_time = time.time()
    elapsed_time = end_time - start_time

    for status, stats in RESULTS_DICT.items():
        if status == 200:
            print(f'{bcolors.GREEN}')
        elif type(status) is int:
            print(f'{bcolors.YELLOW}')
        else:
            print(f'{bcolors.RED}')

        print('Response status: ' + str(status))
        print('Number of reponses: ' + str(stats[0]))
        if type(status) is int:
            avgtime = '{:.2f}'.format(stats[1]/stats[0])
            print('Avg response time: ' + avgtime + ' seconds')

    print('\n')
    print(f'{bcolors.VIOLET}**********************')
    print('Elapsed Time: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) )
    print(f'**********************{bcolors.ENDC}')

if __name__ == '__main__':
    main()