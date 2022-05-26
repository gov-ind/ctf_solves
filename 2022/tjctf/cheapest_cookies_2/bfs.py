from time import time

end = 20
start = 0

def weighted_bfs(costs):
    paths = {
      0: [[0]]  # all the paths that have 0 cost
    }

    while len(paths) > 0:
        least_cost = sorted(paths)[0]

        for path in paths[least_cost]:
            # start from the last node in the route
            node = path[-1]
        
            if node == end:
                return least_cost

            for next_node in costs[node]:
                # avoid cyclic paths
                if next_node in path: continue

                next_cost = least_cost + costs[node][next_node]
                next_path = [path + [next_node]]
                
                if next_cost not in paths:
                    paths[next_cost] = next_path
                else:
                    paths[next_cost] += next_path

        del paths[least_cost]

    return -1

with open('tests', 'rb') as f:
    tests = eval(f.read())

times = []

for test in tests:
    start_time = time()
    print(weighted_bfs(test))
    times.append(time() - start_time)

print(sum(times) / len(times))
