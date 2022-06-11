from pwn import *
from collections import Counter

def _simulate(start):
    if randint(0, 1) == 0:
        if start == 8:
            return 7
        return start + 1
    if start == 1:
        return 2
    return start - 1

def simulate():
    trials = []
    for _ in range(200):
        houses = []
        start = randint(1, 8)
        for __ in range(8):
            start = _simulate(start)
            houses.append(start)

        trials.append(houses)
    return trials

def evaluate(trial, guesses):
    correct_count = 0

    for houses in trial:
        if 0 in [a ^ b for a, b in zip(houses, guesses)]:
            correct_count += 1

    return correct_count

guesses = [4, 7, 2, 5, 5, 2, 7, 4]
#guesses = []

def dfs(houses, level=0, arr_min=1, arr_max=8):
    if level == arr_max - 1:
        most_common = Counter(houses).most_common(1)[0][0]
        prob = 1 - houses.count(most_common) / len(houses)
        return [most_common], prob

    uniq_houses = list(set(houses))
    probs = []

    for house in uniq_houses:
        if level == 0:
            print(house)
        prob = 1 - houses.count(house) / len(houses)

        next_houses = []
        for i in houses:
            if i == house: continue
            if i != arr_min:
                next_houses.append(i - 1)
            else:
                next_houses.append(i + 1)
            if i != arr_max:
                next_houses.append(i + 1)
            else:
                next_houses.append(i - 1)
           
        _next_houses, next_prob = dfs(next_houses,
                                      level=level + 1,
                                      arr_min=arr_min,
                                      arr_max=arr_max)
        probs.append(([house] + _next_houses, prob * next_prob))

    probs = sorted(probs, key=lambda a: a[1])
    return probs[0]

houses = list(range(1, 9))

if len(guesses) == 0:
    guesses, probs = dfs(houses)
    print(f'Guesses: {guesses}')

samples = []
for _ in range(1000):
    trials = simulate()
    samples.append(evaluate(trials, guesses))

print(f'Mean: sum(samples) / len(samples)')
#print(probs)

print(f'Max: max(samples)')

print('Probability of success: ' +
       str(len([a for a in samples if a >= 187]) / len(samples)))

while True:
    proc = remote('tunnels.hsctf.com', 1337)
    proc.recvline()

    correct_count = 0
    for trial_num in range(200):
        print(proc.recvline().strip())
        if trial_num != 0:
            print(f'Wrong count: {trial_num - correct_count} ' +
                  f'Projected: {correct_count / trial_num * 200}')
        for guess_num in range(8):
            proc.sendline(str(guesses[guess_num]).encode())

            response = proc.recvline().strip()

            print(response)

            if response == b'guess: correct':
                correct_count +=1
                break

    if correct_count >= 187:
        print(proc.recvline())
        print(proc.recvline())
        exit()
    else:
        print(f'Failed, trying again...')
        proc.close()
