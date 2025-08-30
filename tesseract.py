"""Experimental Tesseract solver built on JAX
https://docs.jax.dev/en/latest/key-concepts.html

This script contains permutation actions and solver for a high dimensional Rubik's cube (2^4).
After training on a single ~24 core CPU for O(hours),
It has been observed solving up to 4 pieces that make up a single face of the puzzle.
The simple fully connected network will most likely not scale to much higher levels.

The reward function approximation method is not very different from how humans can practice such puzzles
to solve up to a single face with no prior knowledge.
This is not a particularly effective approach in comparison to classical algorithms for this problem,
which can be solved in polynomial time using group theoretic constructs as the following,
https://github.com/aditya-r-m/twisty-polyhedra

- Actions and States are represented as permutation matrices with jnp.dot(action, state) for application.
- Transitions can be visualized using render function that creates a simple webpage with perspective projection.
- Key functions to interact with the solver are : learn, solve, save, load

"""

from jax import grad, jit, random, vmap, numpy as jnp

LEN_EDGE = 2
LEN_DIMENSIONS = 4
GRID = []
from itertools import product
for d in range(LEN_DIMENSIONS):
  for dd in [-1, 1]:
    for cube in product(* [list(range(LEN_EDGE))] * (LEN_DIMENSIONS - 1)):
      point = [0] * LEN_DIMENSIONS
      point[d] = dd * (1 + LEN_EDGE)
      for i in range(1, LEN_DIMENSIONS):
        point[(d + i) % LEN_DIMENSIONS] = (2 * cube[i - 1]) - (LEN_EDGE - 1)
      GRID.append(point)

IDENTITY = jnp.identity(len(GRID), dtype=int)
ACTIONS = [IDENTITY]
for d in range(LEN_DIMENSIONS):
  for e in map(lambda x: (d + x) % LEN_DIMENSIONS, range(1, LEN_DIMENSIONS)):
    f = (e + 1) % LEN_DIMENSIONS
    if f == d: f = (f + 1) % LEN_DIMENSIONS
    for i in range(LEN_EDGE):
      action = IDENTITY
      for (u, point) in enumerate(GRID):
        if (point[d] > 0) != bool(i): continue
        point = point[::]
        point[e], point[f] = -point[f], point[e]
        action = action.at[u].set(GRID.index(point) == jnp.arange(len(GRID))).astype(int)
      ACTIONS.append(action)
      ACTIONS.append(jnp.transpose(action))
ACTIONS = jnp.array(ACTIONS)

MXV = float(len(ACTIONS))
K = random.key(0)

def random_layer_params(m, n, key, scale=0.01):
  w_key, b_key = random.split(key)
  w, b = scale * random.normal(w_key, (n, m)), scale * random.normal(b_key, (n,))
  return w, b

def init_network_params(sizes, key=K):
  keys = random.split(key, len(sizes) - 1)
  return [random_layer_params(m, n, k) for m, n, k in zip(sizes[:-1], sizes[1:], keys)]

def save(params, directory="."):
  jnp.savez(f"{directory}/params.npz", *(arr for pair in params for arr in pair))

def load(directory="."):
  arrs = list(jnp.load(f"{directory}/params.npz").values())
  return list(zip(arrs[0::2], arrs[1::2]))

@jit
def relu(x):
  return jnp.maximum(0, x)

@jit
def dot_batch(actions, state):
  return vmap(jnp.dot, (0, None))(actions, state)

@jit
def predict(params, state):
  activations = state.flatten().astype('float32')
  for w, b in params[:-1]: activations = relu(jnp.dot(w, activations) + b)
  return (jnp.dot(params[-1][0], activations) + params[-1][1]).sum()

@jit
def predict_batch(params, states):
  return vmap(predict, (None, 0))(params, states)

@jit
def is_solved(state):
  return jnp.diag(state).all()

@jit
def greedy_estimate(params, state):
  s = is_solved(state)
  return s * MXV + (1. - s) * (-1. + jnp.maximum(1., jnp.minimum(MXV,
    jnp.max(predict_batch(params, dot_batch(ACTIONS, state))))))

@jit
def update(params, state, learning_rate):
  m = learning_rate * (greedy_estimate(params, state) - predict(params, state))
  return [
    (pw + m * dw, pb + m * db)
    for ((pw, pb), (dw, db)) in zip(params, grad(predict)(params, state))]

@jit
def update_batch(params, states, learning_rate):
  return [
    (jnp.mean(pws, 0), jnp.mean(pbs, 0))
    for (pws, pbs) in vmap(update, (None, 0, None))(params, states, learning_rate)]

@jit
def greedy_action(params, state):
  next_states = dot_batch(ACTIONS, state)
  next_values = predict_batch(params, next_states)
  return ACTIONS[jnp.argmax(next_values)]

@jit
def random_step(key, state):
  return jnp.dot(ACTIONS[random.randint(key, (), 0, len(ACTIONS))], state)

@jit
def random_step_batch(key, states):
  keys = random.split(key, len(states))
  return vmap(random_step, (0, 0))(keys, states)

def learn(
    level=3,
    sessions=10000,
    depth=100,
    breadth=10,
    learning_rate=0.01,
    decay_rate=0.9,
    key=K):
  params = init_network_params([len(GRID) * level, len(GRID) * level, 1], key)
  target = IDENTITY[:,:level]
  for _ in range(sessions):
    states = jnp.array([target] * breadth)
    for _ in range(depth):
      params = update_batch(params, states, learning_rate)
      action_key, key = random.split(key)
      states = random_step_batch(action_key, states)
    learning_rate -= decay_rate * learning_rate / sessions
  return params

def solve(params, depth=100, key=K):
  level = len(params[0][0][0]) // len(GRID)
  state = IDENTITY
  for _ in range(depth):
    action_key, key = random.split(key)
    state = random_step(action_key, state)
  chain = [state]
  for d in range(depth):
    if is_solved(chain[-1][:,:level]): break
    chain.append(jnp.dot(greedy_action(params, chain[-1][:,:level]), chain[-1]))
  return chain

def render(states, level=None, directory="."):
  states = [jnp.dot(jnp.arange(len(GRID)), state).tolist() for state in states]
  color_fn = f"rgb(${{20 + 50 * (c & 4)}},${{20 + 100 * (c & 2)}},${{20 + 200 * (c & 1)}})"
  if level: color_fn = f"${{i >= {level} ? 'white' : 'black'}}"
  with open(f"{directory}/output.html", "w") as f:
    f.write(f'''
  <html><body><canvas id='cout' width='512px' height='512px'></canvas>
  <script>
  const F = 16;
  const grid = {GRID};
  const states = {states};
  let state = {states[0]};
  const ctx = cout.getContext('2d');
  ctx.translate(255, 255);
  ctx.scale(127, 127);
  let m = 0;
  let f = 0;
  function render() {{
      f += 1;
      if (f === F) {{
          f = 0;
          m += 1;
          if (m === states.length - 1) return;
      }}
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, cout.width, cout.height);
      ctx.restore();
      clen = grid.length >> 3;
      let dots = [];
      for (let i = 0; i < states[0].length; i++) {{
          let [w0, x0, y0, z0] = grid[states[m][i]];
          let [w1, x1, y1, z1] = grid[states[m + 1][i]];
          let w = (f * w1 + (F - 1 - f) * w0) / (F - 1);
          let x = (f * x1 + (F - 1 - f) * x0) / (F - 1);
          let y = (f * y1 + (F - 1 - f) * y0) / (F - 1);
          let z = (f * z1 + (F - 1 - f) * z0) / (F - 1);
          x /= w + 8;
          y /= w + 8;
          z /= w + 8;
          x = x * 4/5 - z * 3/5;
          z = x * 3/5 + z * 4/5;
          y = y * 4/5 - z * 3/5;
          x *= 2;
          y *= 2;
          let c = Math.floor(i / clen);
          dots.push([-z, x, y, `{color_fn}`]);
      }}
      dots.sort();
      for (let [_, x, y, c] of dots) {{
          ctx.fillStyle = 'black';
          ctx.fillRect(x - 1/128, y - 1/128, 1/16 + 2/128, 1/16 + 2/128);
          ctx.fillStyle = c;
          ctx.fillRect(x, y, 1/16, 1/16);
      }}
      requestAnimationFrame(render);
  }}
  render();
  </script></body></html>
  ''')
