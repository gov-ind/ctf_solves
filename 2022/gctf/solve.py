import numpy as np
from pwn import process, remote
from subprocess import check_output
from math import log
from matplotlib import pyplot as plt
from tqdm import tqdm

debug = True

def recvline(p1):
    line = p1.recvline()
    # print(line)
    return line

responses = {}

magic = log(127)
num_samples = 10
weights = np.linspace(magic, magic / 0.1, num_samples)
num_pixels = 768

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

pl = b''
pending_pixels = []

for pixel in range(num_pixels):
    pending_pixels.append(pixel)

    pl += b'1\n'
    pl += f'0 {pixel} 0 1\n'.encode()

    for weight in weights:
        pl += b'1\n' + f'2 0 0 {weight}'.encode() + b'\n'
        pl += b'2\n'

    pl += b'0\n'

    if len(pending_pixels) == 128:
        proc.send(pl)

        print('Sending batch of 128 pixels')
        for pixel in tqdm(pending_pixels):
            responses[pixel] = {}
            proc.readuntil(b'Quit\n')

            for idx in range(num_samples):
                proc.readuntil(b'Quit\n')
                val = proc.recvline().split(b': ')[1].strip()[1:-1].decode('unicode_escape')
                responses[pixel][weights[idx]] = val

                proc.readuntil(b'Quit\n')

            proc.readuntil(b'Quit\n')

        pl = b''
        pending_pixels = []

num_chars = len(list(responses[list(responses.keys())[0]].values())[0])

sols = np.zeros((num_chars, num_pixels))

for char in range(num_chars):
    for pixel in responses:
        for weight in responses[pixel]:
            if responses[pixel][weight][char] == '\x00':
                sols[char][pixel] = magic / weight
                break

plt.figure(figsize = (20, 3))
plt.imshow(np.hstack([sols[i].reshape((16, 16, 3)) for i in range(len(sols))]),
           interpolation='nearest')
plt.axis('off')
plt.savefig('solution.png')

for char in range(num_chars):
    plt.imshow(sols[char].reshape((16, 16, 3)))
    plt.show()
    plt.clf()
