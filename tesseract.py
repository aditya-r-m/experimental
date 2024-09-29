from collections import defaultdict
from random import randrange


n = 3
q = defaultdict(lambda: 0)
training_sessions = 10000
training_duration = 100


def initial_state():
    return list(range(n * (1 << n)))


def generate_permutations():
    points, point_index_map = [], {}
    for i in range(1 << n):
        point = []
        for _ in range(n):
            point.append(((i & 1) * 2) - 1)
            i >>= 1
        for j in range(n):
            current_point = point[::]
            current_point[j] *= 2
            point_index_map[tuple(current_point)] = len(points)
            points.append(tuple(current_point))
    permutations = [initialize_state()]
    for i in range(n):
        for j in range(i + 1, i + n):
            for k in range(j + 1, i + n):
                for l in range(1, 4):
                    permutation = initialize_state()
                    for point_index, point in enumerate(map(list, points)):
                        if point[i] < 0: continue
                        for _ in range(l):
                            point[j % n], point[k % n] = -point[k % n], point[j % n]
                        permutation[point_index_map[tuple(point)]] = point_index
                    permutations.append(permutation)
    return permutations


def alignment(state):
    return sum(i == pi for (i, pi) in enumerate(state))


def apply(permutation, state):
    next_state = list(map(lambda point_index: permutation[point_index], state))
    return next_state, 10 * (alignment(next_state) - alignment(state)) - 1


def scramble(d):
    state = initialize_state()
    for _ in range(d):
        state, _ = apply(permutations[randrange(len(permutations))], state)
    return state


def policy(state):
    return max(((q[(tuple(state), a)], a) for a in range(len(permutations))))[1]


def train():
    training_depth = 1
    for i in range(training_sessions):
        state = scramble(1 + randrange(training_depth))
        if i % (training_sessions // training_duration) == 0:
            training_depth += 1
        for _ in range(training_duration):
            for a in range(len(permutations)):
                next_state, reward = apply(permutations[a], state)
                q[(tuple(state), a)] = max(q[(tuple(state), a)],
                        reward + max(q[(tuple(next_state), b)] for b in range(len(permutations))))
            state, _ = apply(state, permutations[policy(state)])


def test():
    for _ in range(training_sessions):
        state = scramble(1 + randrange(training_depth))
        start, moves_made = state, 0
        while state != initial_state:
            state, _ = apply(state, permutations[policy(state)])
            moves_made += 1
        print(f"{state} solved in {moves_made} moves")


