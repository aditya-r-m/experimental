use std::ops::Add;
use std::ops::AddAssign;
use std::ops::Mul;
use std::ops::MulAssign;

#[derive(Debug, Clone, Copy)]
struct Complex {
    x: f64,
    y: f64,
}

impl Add for Complex {
    type Output = Complex;
    fn add(self, other: Complex) -> Complex {
        Complex {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

impl AddAssign for Complex {
    fn add_assign(&mut self, other: Complex) {
        *self = *self + other
    }
}

impl Mul for Complex {
    type Output = Complex;
    fn mul(self, other: Complex) -> Complex {
        Complex {
            x: self.x * other.x - self.y * other.y,
            y: self.x * other.y + self.y * other.x,
        }
    }
}

impl MulAssign for Complex {
    fn mul_assign(&mut self, other: Complex) {
        *self = *self * other
    }
}

const ONE: Complex = Complex { x: 1., y: 0. };
const MINUS_ONE: Complex = Complex { x: -1., y: 0. };

fn fft_(vs: &Vec<Complex>, w: Complex) -> Vec<Complex> {
    if vs.len() == 1 {
        return vs.clone();
    }
    let mut ves = Vec::new();
    let mut vos = Vec::new();
    for i in 0..vs.len() {
        if i & 1 == 0 {
            ves.push(vs[i]);
        } else {
            vos.push(vs[i]);
        }
    }
    let res = fft_(&ves, w * w);
    let ros = fft_(&vos, w * w);
    let mut rs = Vec::with_capacity(vs.len());
    let mut wi = ONE;
    for i in 0..res.len() {
        rs.push(res[i] + wi * ros[i]);
        wi *= w;
    }
    wi = ONE;
    for i in 0..res.len() {
        rs.push(res[i] + MINUS_ONE * wi * ros[i]);
        wi *= w;
    }
    rs
}

fn fft(f: &Vec<Complex>, i: bool) -> Vec<Complex> {
    assert!(f.len().count_ones() == 1);
    let p = f.len() as f64;
    let w = Complex {
        x: (2. * std::f64::consts::PI / p).cos(),
        y: (if i { -2. } else { 2. } * std::f64::consts::PI / p).sin(),
    };
    fft_(f, w)
        .into_iter()
        .map(|c| {
            c * Complex {
                x: 1. / p.sqrt(),
                y: 0.,
            }
        })
        .collect::<Vec<Complex>>()
}

fn main() {
    let mut v: Vec<Complex> = Vec::new();
    for i in 0..8 {
        v.push(Complex { x: i as f64, y: 0. })
    }
    println!("initial vector:");
    for &c in v.iter() {
        print!(" {:.2}", c.x);
    }
    println!("\n\nfourier transform:");
    for &c in fft(&v, false).iter() {
        print!(" {:.2}", c.x);
    }
    println!("\n\ninverted fourier transform:");
    for &c in fft(&fft(&v, false), true).iter() {
        print!(" {:.2}", c.x);
    }
    println!("");
}
