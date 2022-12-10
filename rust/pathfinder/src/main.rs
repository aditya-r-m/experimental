use std::collections::BinaryHeap;
use std::io;

fn read_u64_vec() -> Vec<u64> {
    let mut result: Vec<u64> = Vec::new();
    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .expect("Failed to read line");
    for val in input.split_whitespace() {
        match val.parse::<u64>() {
            Ok(i) => result.push(i),
            Err(..) => println!("failed to parse as u64 {}", val),
        };
    }

    result
}

fn find_distance(graph: &Vec<Vec<(usize, u64)>>, s: usize, t: usize) -> Option<u64> {
    let n = graph.len();
    if s >= n || t >= n {
        return None;
    }
    let mut q = BinaryHeap::new();
    let mut visited: Vec<bool> = vec![false; n];
    q.push((0, s));
    visited[s] = true;
    while let Some((d, u)) = q.pop() {
        if u == t {
            return Some(d);
        }
        for &(v, w) in graph[u].iter() {
            if visited[v] {
                continue;
            }
            q.push((d + w, v));
            visited[v] = true;
        }
    }

    None
}

fn main() {
    println!("enter the count of vertices & edges");
    let mut input_vec = read_u64_vec();
    let (n, m) = (input_vec[0] as usize, input_vec[1] as usize);
    println!("{:?}", (n, m));
    let mut graph: Vec<Vec<(usize, u64)>> = Vec::new();
    graph.resize_with(n, Vec::new);
    for i in 0..m {
        println!("enter edge {}", i);
        input_vec = read_u64_vec();
        let (u, v, w) = (input_vec[0] as usize, input_vec[1] as usize, input_vec[2]);
        graph[u].push((v, w));
        graph[v].push((u, w));
    }
    println!("The adjacency list representation of the graph is as follows");
    println!("{:?}", graph);
    loop {
        println!("Enter the source & target, Enter 0 0 to terminate");
        input_vec = read_u64_vec();
        let (s, t) = (input_vec[0] as usize, input_vec[1] as usize);
        if s == 0 && t == 0 {
            break;
        }
        println!(
            "The distance from source to target is {:?}",
            find_distance(&graph, s, t)
        );
    }
}
