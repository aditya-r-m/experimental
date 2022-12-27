use std::collections::BinaryHeap;
use std::collections::HashMap;

#[derive(Clone, Debug)]
struct Graph {
    n: usize,
    f: Vec<HashMap<usize, u64>>,
    b: Vec<HashMap<usize, u64>>,
}

impl Graph {
    fn new(n: usize) -> Graph {
        Graph {
            n: n,
            f: vec![HashMap::new(); n],
            b: vec![HashMap::new(); n],
        }
    }

    fn add_edge(&mut self, u: usize, v: usize, w: u64) {
        self.f[u].insert(v, w);
        self.b[v].insert(u, w);
    }

    fn shortcuts(&self, i: usize) -> Vec<(usize, usize)> {
        let mut result = vec![];
        for (&u, &du) in self.b[i].iter() {
            for (&v, &dv) in self.f[i].iter() {
                if self
                    .find_distance(u, v, Some(i), Some(du + dv))
                    .unwrap_or(u64::MAX)
                    > du + dv
                {
                    result.push((u, v));
                }
            }
        }
        result
    }

    fn preprocess(&mut self) {
        let mut f: Vec<HashMap<usize, u64>> = vec![HashMap::new(); self.n];
        let mut b: Vec<HashMap<usize, u64>> = vec![HashMap::new(); self.n];

        let mut q = BinaryHeap::new();
        for i in 0..self.n {
            q.push((i & 1, i));
        }
        while let Some((_, i)) = q.pop() {
            for (u, v) in self.shortcuts(i) {
                let w = self.b[i][&u] + self.f[i][&v];
                self.f[u].insert(v, w);
                self.b[v].insert(u, w);
            }
            for (&v, &w) in self.f[i].iter() {
                f[i].insert(v, w);
                self.b[v].remove(&i);
            }
            for (&v, &w) in self.b[i].iter() {
                b[i].insert(v, w);
                self.f[v].remove(&i);
            }
            self.f[i].clear();
            self.b[i].clear();
        }
        self.f = f;
        self.b = b;
    }

    fn find_distance(&self, s: usize, t: usize, ox: Option<usize>, ol: Option<u64>) -> Option<u64> {
        let x = ox.unwrap_or(self.n);
        let l = ol.unwrap_or(u64::MAX);
        if s >= self.n || t >= self.n || s == x || t == x {
            return None;
        }
        let mut qf = BinaryHeap::new();
        let mut df = HashMap::new();
        let mut qb = BinaryHeap::new();
        let mut db = HashMap::new();
        qf.push((0, s));
        df.insert(s, 0);
        qb.push((0, t));
        db.insert(t, 0);
        df.insert(x, u64::MAX);
        db.insert(x, u64::MAX);
        while !qf.is_empty() || !qb.is_empty() {
            if let Some((d, u)) = qf.pop() {
                if let Some(r) = db.get(&u) {
                    return Some(d + r);
                }
                for (&v, &w) in self.f[u].iter() {
                    if df.contains_key(&v) || d + w >= l {
                        continue;
                    }
                    qf.push((d + w, v));
                    df.insert(v, d + w);
                }
            }
            if let Some((d, v)) = qb.pop() {
                if let Some(r) = df.get(&v) {
                    return Some(d + r);
                }
                for (&u, &w) in self.b[v].iter() {
                    if db.contains_key(&u) || d + w >= l {
                        continue;
                    }
                    qb.push((d + w, u));
                    db.insert(u, d + w);
                }
            }
        }
        None
    }
}

fn main() {
    let n: usize = 5;
    let mut graph: Graph = Graph::new(n);
    for i in 0..n - 1 {
        graph.add_edge(i, i + 1, 1);
    }
    println!("{:?}", graph);
    graph.preprocess();
    println!("{:?}", graph);
    for u in 0..n {
        for v in 0..n {
            println!("{}->{}:{:?}", u, v, graph.find_distance(u, v, None, None));
        }
    }
}
