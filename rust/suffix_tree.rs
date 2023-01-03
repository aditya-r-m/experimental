use std::collections::BTreeMap;

struct Node {
    id: usize,
    edges: BTreeMap<char, Edge>,
    suffix_link: Option<usize>,
}

impl Node {
    fn render(&self, nodes: &Vec<Node>, chars: &Vec<char>, prefix: &str) {
        println!("{}BEGIN Node: {}", prefix, self.id);
        println!("{}suffix_link->{:?}", prefix, self.suffix_link);
        let nprefix = prefix.to_owned() + "\t";
        for (c, e) in self.edges.iter() {
            println!("{}edge_key: {}", nprefix, c);
            e.render(nodes, chars, &nprefix);
        }
        println!("{}END Node: {}", prefix, self.id);
    }
}

struct Edge {
    start: usize,
    length: usize,
    target: usize,
}

impl Edge {
    fn render(&self, nodes: &Vec<Node>, chars: &Vec<char>, prefix: &str) {
        println!("{}edge_start: {}", prefix, self.start);
        println!(
            "{}edge_string: {:?}",
            prefix,
            &chars[self.start..if self.length == std::usize::MAX {
                chars.len()
            } else {
                self.start + self.length
            }]
        );
        nodes[self.target].render(nodes, chars, prefix);
    }
}

struct SuffixTree {
    chars: Vec<char>,
    nodes: Vec<Node>,
    remainder: usize,
    active_node_id: usize,
    active_edge_char: Option<char>,
    active_length: usize,
    last_added_internal_node: Option<usize>,
}

impl SuffixTree {
    fn new() -> SuffixTree {
        SuffixTree {
            chars: Vec::new(),
            nodes: vec![Node {
                id: 0,
                edges: BTreeMap::new(),
                suffix_link: None,
            }],
            remainder: 0,
            active_node_id: 0,
            active_edge_char: None,
            active_length: 0,
            last_added_internal_node: None,
        }
    }

    fn from(s: &str) -> SuffixTree {
        let mut tree = Self::new();
        for c in s.chars() {
            tree.push(c);
        }
        tree
    }

    fn follow_active_edge_via_suffix_link(&mut self) {
        let mut active_edge_char = self.active_edge_char.unwrap();
        let old_active_node_id = self.active_node_id;
        let old_active_edge_char = active_edge_char;
        let mut old_active_edge_index = self.nodes[old_active_node_id]
            .edges
            .get(&old_active_edge_char)
            .unwrap()
            .start;

        if old_active_node_id == 0 {
            self.active_length -= 1;
            old_active_edge_index += 1;
            active_edge_char =
                self.chars[self.nodes[0].edges.get(&active_edge_char).unwrap().start + 1];
            self.active_edge_char = Some(active_edge_char);
        } else {
            self.active_node_id = self.nodes[self.active_node_id].suffix_link.unwrap();
        }
        let mut active_edge;
        while self.active_length >= {
            active_edge = self.nodes[self.active_node_id]
                .edges
                .get(&active_edge_char)
                .unwrap();
            active_edge
        }
        .length
        {
            let length_diff = active_edge.length;
            self.active_node_id = active_edge.target;
            self.active_length -= length_diff;
            old_active_edge_index += length_diff;
            if self.active_length > 0 {
                active_edge_char = self.chars[old_active_edge_index];
                self.active_edge_char = Some(active_edge_char);
            } else {
                break;
            }
        }

        if self.active_length == 0 {
            self.active_edge_char = None;
            if let Some(last_added_internal_node) = self.last_added_internal_node {
                self.nodes[last_added_internal_node].suffix_link = Some(self.active_node_id);
            }
        }
    }

    fn insert_in_active_edge(&mut self, c: char, ci: usize) -> bool {
        let active_edge_char = self.active_edge_char.unwrap();
        let active_edge = self.nodes[self.active_node_id]
            .edges
            .get(&active_edge_char)
            .unwrap();
        if c == self.chars[active_edge.start + self.active_length] {
            self.active_length += 1;
            if self.active_length == active_edge.length {
                self.active_length = 0;
                self.active_node_id = active_edge.target;
                self.active_edge_char = None;
            }
            return true;
        }
        let leaf_id = self.nodes.len();
        self.nodes.push(Node {
            id: leaf_id,
            edges: BTreeMap::new(),
            suffix_link: None,
        });
        let internal_id = self.nodes.len();
        self.nodes.push(Node {
            id: internal_id,
            edges: BTreeMap::new(),
            suffix_link: None,
        });
        self.nodes[internal_id].edges.insert(
            c,
            Edge {
                start: ci,
                length: std::usize::MAX,
                target: leaf_id,
            },
        );
        let old_start;
        let old_length;
        let old_target;
        {
            let old_edge = self.nodes[self.active_node_id]
                .edges
                .get_mut(&active_edge_char)
                .unwrap();
            old_start = old_edge.start;
            old_length = old_edge.length;
            old_target = old_edge.target;
            old_edge.length = self.active_length;
            old_edge.target = internal_id;
        }
        self.nodes[internal_id].edges.insert(
            self.chars[old_start + self.active_length],
            Edge {
                start: old_start + self.active_length,
                length: if old_length == std::usize::MAX {
                    old_length
                } else {
                    old_length - self.active_length
                },
                target: old_target,
            },
        );
        if let Some(last_added_internal_node) = self.last_added_internal_node {
            self.nodes[last_added_internal_node].suffix_link = Some(internal_id);
        }
        self.last_added_internal_node = Some(internal_id);
        self.follow_active_edge_via_suffix_link();
        self.remainder -= 1;

        false
    }

    fn insert_under_active_node(&mut self, c: char, ci: usize) -> bool {
        if let Some(new_active_edge) = self.nodes[self.active_node_id].edges.get(&c) {
            if new_active_edge.length > 1 {
                self.active_edge_char = Some(c);
                self.active_length = 1;
            } else {
                self.active_node_id = new_active_edge.target;
            }
            return true;
        }
        let n = self.nodes.len();
        self.nodes.push(Node {
            id: n,
            edges: BTreeMap::new(),
            suffix_link: None,
        });
        self.nodes[self.active_node_id].edges.insert(
            c,
            Edge {
                start: ci,
                length: std::usize::MAX,
                target: n,
            },
        );
        if let Some(sl) = self.nodes[self.active_node_id].suffix_link {
            self.active_node_id = sl;
        }
        self.remainder -= 1;

        false
    }

    fn push(&mut self, c: char) {
        let ci = self.chars.len();
        self.chars.push(c);
        self.remainder += 1;
        let mut chars_aligned = false;
        while self.remainder > 0 && !chars_aligned {
            chars_aligned = if self.active_edge_char.is_some() {
                self.insert_in_active_edge(c, ci)
            } else {
                self.insert_under_active_node(c, ci)
            };
        }
        self.last_added_internal_node = None;
    }

    fn render(&self) {
        println!("chars: {:?}", self.chars);
        println!("remainder: {}", self.remainder);
        println!("active_node_id: {}", self.active_node_id);
        println!("active_edge_char: {:?}", self.active_edge_char);
        println!("active_length: {}", self.active_length);
        println!(
            "last_added_internal_node: {:?}",
            self.last_added_internal_node
        );
        self.nodes[0].render(&self.nodes, &self.chars, "");
        println!("--------------------------------------");
    }
}

fn main() {
    SuffixTree::from("aabaacaad").render();
    SuffixTree::from("abcabdabce").render();
    SuffixTree::from("abcdacdacde").render();
}
