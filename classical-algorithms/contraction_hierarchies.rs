use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::convert::TryFrom;

struct Graph {
    n: usize,
    forward_edge_list: Vec<HashMap<usize, u64>>,
    backward_edge_list: Vec<HashMap<usize, u64>>,
}

impl Graph {
    fn new(n: usize) -> Graph {
        Graph {
            n: n,
            forward_edge_list: vec![HashMap::new(); n],
            backward_edge_list: vec![HashMap::new(); n],
        }
    }

    fn add_edge(&mut self, u: usize, v: usize, w: u64, bi: bool) {
        if u == v {
            return;
        }
        self.forward_edge_list[u].insert(v, w);
        self.backward_edge_list[v].insert(u, w);
        if bi {
            self.add_edge(v, u, w, false);
        }
    }

    fn shortcuts(&self, i: usize) -> Vec<(usize, usize)> {
        let mut result = vec![];
        for (&u, &du) in self.backward_edge_list[i].iter() {
            for (&v, &dv) in self.forward_edge_list[i].iter() {
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

    fn edge_difference(&self, i: usize) -> i64 {
        i64::try_from(self.shortcuts(i).len()).unwrap()
            - i64::try_from(self.forward_edge_list[i].len() + self.backward_edge_list[i].len())
                .unwrap()
    }

    fn preprocess(&mut self) {
        let mut forward_edge_list: Vec<HashMap<usize, u64>> = vec![HashMap::new(); self.n];
        let mut backward_edge_list: Vec<HashMap<usize, u64>> = vec![HashMap::new(); self.n];

        let mut contracted_neighbors: Vec<usize> = vec![0; self.n];

        const D: i64 = -12;
        const E: i64 = -19;
        let priority = |c: usize, de: i64| D * i64::try_from(c).unwrap() + E * de;

        let mut queue = BinaryHeap::new();
        for i in 0..self.n {
            queue.push((
                priority(contracted_neighbors[i], self.edge_difference(i)),
                i,
            ));
        }

        while let Some((p, i)) = queue.pop() {
            let shortcuts = self.shortcuts(i);
            let pn = priority(contracted_neighbors[i], self.edge_difference(i));
            if p != pn {
                queue.push((pn, i));
                continue;
            }
            println!("contracting {} with priority {}", i, p);
            for (u, v) in shortcuts {
                println!("\tadding shortcut {}->{}", u, v);
                let w = self.backward_edge_list[i][&u] + self.forward_edge_list[i][&v];
                self.add_edge(u, v, w, false);
            }
            for (&v, &w) in self.forward_edge_list[i].iter() {
                forward_edge_list[i].insert(v, w);
                self.backward_edge_list[v].remove(&i);
                contracted_neighbors[v] += 1;
            }
            for (&v, &w) in self.backward_edge_list[i].iter() {
                backward_edge_list[i].insert(v, w);
                self.forward_edge_list[v].remove(&i);
                contracted_neighbors[v] += 1;
            }
            self.forward_edge_list[i].clear();
            self.backward_edge_list[i].clear();
        }
        self.forward_edge_list = forward_edge_list;
        self.backward_edge_list = backward_edge_list;
    }

    fn find_distance(&self, s: usize, t: usize, ox: Option<usize>, ol: Option<u64>) -> Option<u64> {
        let x = ox.unwrap_or(self.n);
        let l = ol.unwrap_or(u64::MAX);
        if s >= self.n || t >= self.n || s == x || t == x {
            return None;
        }
        if s == t {
            return Some(0);
        }
        let mut dist = u64::MAX;
        let mut queue_forward = BinaryHeap::new();
        let mut dist_forward = HashMap::new();
        let mut queue_backward = BinaryHeap::new();
        let mut dist_backward = HashMap::new();

        queue_forward.push((Reverse(0), s));
        queue_backward.push((Reverse(0), t));
        dist_forward.insert(s, 0);
        dist_backward.insert(t, 0);
        dist_forward.insert(x, u64::MAX);
        dist_backward.insert(x, u64::MAX);

        while !queue_forward.is_empty() || !queue_backward.is_empty() {
            if let Some((Reverse(d), u)) = queue_forward.pop() {
                dist_forward.insert(u, d);
                if d >= dist {
                    queue_forward.clear();
                    break;
                }
                if let Some(r) = dist_backward.get(&u) {
                    dist = dist.min(d + r);
                }
                for (&v, &w) in self.forward_edge_list[u].iter() {
                    if dist_forward.contains_key(&v) || d + w >= l {
                        continue;
                    }
                    queue_forward.push((Reverse(d + w), v));
                }
            }
            if let Some((Reverse(d), v)) = queue_backward.pop() {
                dist_backward.insert(v, d);
                if d >= dist {
                    queue_backward.clear();
                    break;
                }
                if let Some(r) = dist_forward.get(&v) {
                    dist = dist.min(d + r);
                }
                for (&u, &w) in self.backward_edge_list[v].iter() {
                    if dist_backward.contains_key(&u) || d + w >= l {
                        continue;
                    }
                    queue_backward.push((Reverse(d + w), u));
                }
            }
        }
        if dist == u64::MAX {
            None
        } else {
            Some(dist)
        }
    }

    fn print(&self) {
        println!("nodes : {}", self.n);
        for i in 0..self.n {
            println!("{} -> {:?}", i, self.forward_edge_list[i]);
            println!("{} <- {:?}", i, self.backward_edge_list[i]);
        }
    }
}

fn main() {
    let mut graph: Graph = Graph::new(11);
    graph.add_edge(0, 8, 5, true);
    graph.add_edge(0, 9, 3, true);
    graph.add_edge(1, 5, 5, true);
    graph.add_edge(1, 9, 2, true);
    graph.add_edge(2, 7, 6, true);
    graph.add_edge(2, 8, 3, true);
    graph.add_edge(3, 4, 7, true);
    graph.add_edge(3, 7, 3, true);
    graph.add_edge(4, 6, 3, true);
    graph.add_edge(5, 6, 4, true);
    graph.add_edge(6, 10, 5, true);
    graph.add_edge(7, 10, 1, true);
    graph.add_edge(8, 10, 3, true);
    graph.add_edge(9, 10, 1, true);
    let mut dist_map: HashMap<(usize, usize), Option<u64>> = HashMap::new();
    for u in 0..graph.n {
        for v in 0..graph.n {
            dist_map.insert((u, v), graph.find_distance(u, v, None, None));
        }
    }
    println!("Initial graph:");
    graph.print();

    println!("\nPreprocessing phase:");
    graph.preprocess();
    println!("\nPreprocessed graph:");
    graph.print();

    println!("\nValidation phase:");
    for u in 0..graph.n {
        for v in 0..graph.n {
            assert_eq!(
                *dist_map.get(&(u, v)).unwrap(),
                graph.find_distance(u, v, None, None)
            );
        }
    }
    println!("All pairwise distance computation validated.");
}
