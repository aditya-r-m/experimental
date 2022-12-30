use std::ops::AddAssign;

struct Bitree<T>
where
    T: Default + Copy + AddAssign,
{
    collection: Vec<T>,
}

impl<T> Bitree<T>
where
    T: Default + Copy + AddAssign,
{
    fn new(sz: usize) -> Bitree<T> {
        Bitree {
            collection: vec![T::default(); sz],
        }
    }

    fn insert(&mut self, i: usize, v: T) {
        if i == 0 {
            self.collection[0] += v;
            return;
        }
        let mut j = i;
        while j < self.collection.len() {
            self.collection[j] += v;
            j += j & (!j + 1);
        }
    }

    fn get_prefix_sum(&self, l: usize) -> T {
        let mut result = self.collection[0];
        let mut j = l;
        while j != 0 {
            result += self.collection[j];
            j -= j & (!j + 1);
        }
        result
    }
}

fn main() {
    let l = 10;
    let mut tree = Bitree::<u64>::new(10);
    for i in 0..l {
        tree.insert(i, i as u64);
        println!("Triangular number {} -> {}", i, tree.get_prefix_sum(i));
    }
}
