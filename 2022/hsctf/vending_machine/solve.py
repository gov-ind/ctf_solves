import socket
from subprocess import check_output
from random import randint

class Solver():
    def __init__(self):
        self.memo = {}

    def add_to_memo(self, a, b, val):
        if a not in self.memo:
            self.memo[a] = {}
        self.memo[a][b] = val

    def get_from_memo(self, a, b):
        if a in self.memo and b in self.memo[a]:
            return self.memo[a][b]
        return None

    def subset_sum(self, remaining, coins, start_idx=0, sols=[]):
        if remaining < 0:
            return False
        if remaining == 0:
            return True

        if start_idx == len(coins):
            self.add_to_memo(remaining, start_idx, False)
            return False

        from_memo = self.get_from_memo(remaining - coins[start_idx],
                                       start_idx)
        if from_memo: return from_memo

        sol_exists = self.subset_sum(remaining - coins[start_idx],
                                     coins,
                                     start_idx=start_idx + 1,
                                     sols=sols)
       
        if sol_exists:
            sols.append(coins[start_idx])
            return True

        self.add_to_memo(remaining - coins[start_idx], start_idx, False)

        from_memo = self.get_from_memo(remaining, start_idx)
        if from_memo: return from_memo

        sol_exists = self.subset_sum(remaining, coins,
                                     start_idx=start_idx + 1, sols=sols)

        self.add_to_memo(remaining, start_idx, sol_exists)

        return sol_exists

def solve(items, coins):
    results = []

    for i, item in enumerate(items):
        sols = []
        
        if not Solver().subset_sum(item + randint(0, 1), coins, 0, sols=sols):
            spare_coins = sum(coins) - sum(items[i:])
            for extra_coin in range(1, spare_coins + 1):
                sols = []
                if Solver().subset_sum(item + extra_coin, coins, 0, sols=sols):
                    break
            else:
                return False

        results.append(sols)

        for coin in sols:
            coins.remove(coin)

    return results

def _solve(items, coins):
    i = 1
    while True:
        print(f'Attempt: {i}')
        
        sol = solve(items.copy(), coins.copy())
        
        if sol:
            return sol
        
        print('Attempt failed')
        i += 1

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('35.204.95.14', 1337))

sock_read = sock.makefile()

print(sock_read.readline())
print(sock_read.readline())
print(sock_read.readline())

pow_res = sock_read.readline().encode()

curl = pow_res.split(b'(')[1].split(b')')[0]
pow = pow_res.split(b' ')[-1].strip()

source = check_output(curl.split(b' '))

print('Solving PoW')
pow_sol = check_output(['python3.9', '-c', source, 'solve', pow])
print('Done')

print(sock_read.readline())
print(sock_read.readline())

sock.sendall(pow_sol + b'\n')
print(sock_read.readline()) 

for _ in range(12):
    sock.sendall(b'Display\n')
    print(sock_read.readline())
    print(sock_read.readline())

    items = {}
    for _ in range(56):
        line = sock_read.readline().strip()

        item_id, item = line.split(': ')
        items[item_id] = int(item)

    print(sock_read.readline())
    print(sock_read.readline())

    coins = {}
    for _ in range(200):
        line = sock_read.readline().strip()

        coin_id, coin = line.split(': ')
        coins[coin_id] = int(coin)

    _items = sorted([items[a] for a in items])
    _coins = [coins[a] for a in coins]

    print(f'Items: {_items}')
    print(f'Coins: {_coins}')

    sols = _solve(_items, _coins)

    sock_read.readline()

    payload = b''
    line_count = 0
    for item, sol in zip(_items, sols):
        line_count += 1

        item_idx = list(items.keys())[list(items.values()).index(item)]
        coin_idxs = [list(coins.keys())[list(coins.values()).index(a)] for a in sol]

        payload += b'Insert ' + ' '.join(coin_idxs).encode() + b'\n'
          
        for _ in range(len(sol)):
            line_count += 1
        
        payload += b'Buy ' + item_idx.encode() + b'\n'

        for idx in coin_idxs:
            if idx in coins: del coins[idx]
        del items[item_idx]

    sock.sendall(payload)
    for i in range(line_count):
        sock_read.readline()

    print(sock_read.readline())

print(sock_read.readline())
