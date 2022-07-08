import numpy as np
from pwn import *
from subprocess import check_output
from time import sleep
from math import log
from matplotlib import pyplot as plt

debug = True

def recvline(p1):
    line = p1.recvline()
    # print(line)
    return line

responses = {}

try:
    with open('oracle_responses', 'r') as f:
        responses = eval(f.read())
except:
    pass

magic = log(127)
num_samples = 50
weights = np.linspace(magic, magic / 0.1, num_samples)
num_pixels = 768

while True:
    try:
        if debug:
            proc = process(['python3.9', 'server.py'])
            proc.recvline()
        else:
            proc = remote('ocr.2022.ctfcompetition.com', 1337)

            for _ in range(3): recvline(proc)

            pow = proc.recvline().strip()
            source = check_output(pow.split(b'<(')[1].split(b')')[0].split(b' '))
            pl = pow.split(b' ')[-1]

            pow_sol = check_output(['python3.9', '-c', source, 'solve', pl])

            for _ in range(2): recvline(proc)

            proc.sendline(pow_sol)

            recvline(proc)

        for _ in range(6):
            recvline(proc)

        for pixel in range(num_pixels):
            if pixel in responses and len(responses[pixel]) == num_samples: continue
            if pixel not in responses:
                responses[pixel] = {}

            proc.sendline(b'1')
            proc.recvline()
            proc.sendline(f'0 {pixel} 0 1'.encode())
            for _ in range(5): recvline(proc)

            print(pixel)

            pl = b''
            line_count = 0
            weight_idxs = []

            for weight in weights:
                if weight in responses[pixel]: continue

                pl += b'1\n' + f'2 0 0 {weight}'.encode() + b'\n'
                line_count += 6

                pl += b'2\n'
                line_count += 6

                weight_idxs.append(weight)

            if pl != b'':
                proc.send(pl)
            
            weight_idx = 0
            for _ in range(line_count):
                res = proc.recvline()

                if b'sees' in res:
                    val = res.split(b': ')[1].strip()[1:-1].decode('unicode_escape')
                    responses[pixel][weight_idxs[weight_idx]] = val
                    weight_idx += 1

            if not debug: sleep(1)
            
            proc.sendline(b'0')
            for _ in range(5): recvline(proc)
       
            with open('oracle_responses', 'w') as f:
                f.write(str(responses))
            
        break
    except Exception as e:
        print('Fail')
        pass

num_chars = len(list(responses[list(responses.keys())[0]].values())[0])

sols = np.zeros((num_chars, num_pixels))

for char in range(num_chars):
    for pixel in responses:
        for weight in responses[pixel]:
            if responses[pixel][weight][char] == '\x00':
                sols[char][pixel] = magic / weight
                break

plt.figure(figsize = (20, 3))
plt.imshow(np.hstack([sols[i].reshape((16, 16, 1)) for i in range(len(sols))]),
           interpolation='nearest')
plt.savefig('solution.png')

for char in range(num_chars):
    plt.imshow(sols[char].reshape((16, 16, 1)))
    plt.show()
    plt.clf()
