use std::collections::BinaryHeap;
use std::collections::HashMap;

#[derive(Clone, Debug)]
struct Graph {
    n: usize,
    f: Vec<Vec<(usize, u64)>>,
    b: Vec<Vec<(usize, u64)>>,
}

impl Graph {
    fn new(n: usize) -> Graph {
        Graph {
            n: n,
            f: vec![vec![]; n],
            b: vec![vec![]; n],
        }
    }

    fn add_edge(&mut self, u: usize, v: usize, w: u64) {
        self.f[u].push((v, w));
        self.b[v].push((u, w));
    }
}

fn _preprocess(graph: &Graph) -> Graph {
    graph.clone()
}

fn find_distance(graph: &Graph, s: usize, t: usize) -> Option<u64> {
    if s >= graph.n || t >= graph.n {
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
    while !qf.is_empty() || !qb.is_empty() {
        if let Some((d, u)) = qf.pop() {
            if let Some(r) = db.get(&u) {
                return Some(d + r);
            }
            for &(v, w) in graph.f[u].iter() {
                if df.contains_key(&v) {
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
            for &(u, w) in graph.b[v].iter() {
                if db.contains_key(&u) {
                    continue;
                }
                qb.push((d + w, u));
                db.insert(u, d + w);
            }
        }
    }
    None
}

fn main() {
    let n: usize = 4;
    let mut graph: Graph = Graph::new(n);
    for i in 0..n - 1 {
        graph.add_edge(i, i + 1, 1);
    }
    for u in 0..n {
        for v in 0..n {
            println!("{}->{}:{:?}", u, v, find_distance(&graph, u, v));
        }
    }
}
