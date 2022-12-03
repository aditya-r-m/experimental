use std::io;

fn read_usize_pair() -> (usize, usize) {
    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .expect("Failed to read line");
    let input_vec = input.split_whitespace().collect::<Vec<&str>>();
    let mut u: usize = 0;
    let mut v: usize = 0;
    match input_vec[0].parse::<usize>() {
        Ok(i) => u = i,
        Err(..) => println!("failed to parse as usize {}", input_vec[0]),
    };
    match input_vec[1].parse::<usize>() {
        Ok(i) => v = i,
        Err(..) => println!("failed to parse as usize {}", input_vec[1]),
    };
    (u, v)
}

fn find_distance(graph: &Vec<Vec<usize>>, s: usize, t: usize) -> usize {
    let n = graph.len();
    if s >= n || t >= n {
        return usize::MAX;
    }
    let mut vecq: Vec<usize> = vec![s, n];
    let mut visited: Vec<bool> = vec![false; n];
    visited[s] = true;
    let mut i: usize = 0;
    let mut d: usize = 0;
    while i < vecq.len() {
        let u = vecq[i];
        i += 1;
        if u == n {
            if i == vecq.len() {
                return usize::MAX;
            }
            d += 1;
            vecq.push(n);
            continue;
        }
        if u == t {
            return d;
        }
        for &v in graph[u].iter() {
            if visited[v] {
                continue;
            }
            vecq.push(v);
            visited[v] = true;
        }
    }
    usize::MAX
}

fn main() {
    println!("enter the count of vertices & edges");
    let (n, m) = read_usize_pair();
    println!("{:?}", (n, m));
    let mut graph: Vec<Vec<usize>> = Vec::new();
    graph.resize_with(n, Vec::new);
    for i in 0..m {
        println!("enter (directional) edge {}", i);
        let (u, v) = read_usize_pair();
        graph[u].push(v);
    }
    println!("The adjacency list representation of the graph is as follows");
    println!("{:?}", graph);
    loop {
        println!("Enter the source & target, Enter 0 0 to terminate");
        let (s, t) = read_usize_pair();
        if s == 0 && t == 0 {
            break;
        }
        println!(
            "The distance from source to target is {}",
            find_distance(&graph, s, t)
        );
    }
}
