from subprocess import check_output
import socket

def find_num_deadlocked_nodes(test):
    good_nodes = set()
    deadlocked_nodes = set()

    for idx, target in enumerate(test):
        if idx in good_nodes:
            good_nodes.add(idx)
            continue

        visited = [idx]
        next_idx = target - 1

        while True:
            if next_idx in good_nodes or next_idx in deadlocked_nodes:
                good_nodes |= set(visited)
                break

            if next_idx in visited:
                good_nodes |= set(visited)

                split_idx = visited.index(next_idx)
                _deadlocked_nodes = set(visited[split_idx:])

                deadlocked_nodes |= _deadlocked_nodes

                break

            visited.append(next_idx)
            next_idx = test[next_idx] - 1

    return len(deadlocked_nodes)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('hacking.hsctf.com', 1337))  
  
sock_read = sock.makefile()

sock_read.readline()
sock_read.readline()
sock_read.readline()

pow_res = sock_read.readline().encode()

curl = pow_res.split(b'(')[1].split(b')')[0]
pow = pow_res.split(b' ')[-1].strip()

source = check_output(curl.split(b' '))

print('Solving PoW')
pow_sol = check_output(['python3.9', '-c', source, 'solve', pow])
print('Done')

sock_read.readline()
sock_read.readline()

sock.sendall(pow_sol + b'\n')

sock_read.readline()
sock_read.readline()

sols = []
for i in range(5):
    print(f'Fetching test {i}')
    line = sock_read.readline()
    test = [int(a) for a in line.strip().split(', ')]

    sols.append(find_num_deadlocked_nodes(test))

sols = ', '.join([str(a) for a in sols]).encode()
print(f'sols: {sols}')

sock.sendall(sols + b'\n')

print(sock_read.readline())
print(sock_read.readline())
print(sock_read.readline())
print(sock_read.readline())
