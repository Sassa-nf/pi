fn is_odd_tco(mut x: u32, y: &mut u32) -> bool {
   while x != 0 {
      x += 2;
   }
   *y = x;
   return false;
}

fn is_even(x: u32) -> bool {
   is_odd(x - 1)
}

fn is_odd(x: u32) -> bool {
   x != 0 && is_even(x - 1)
}

fn main() {
    println!("{}, {}, {}, {}", is_odd(0), is_odd(1), is_odd(2), is_odd(3));

    let mut x = 0;
    let mut y = 0;
    let mut z = 0;
    let mut t = 0;
    println!("{}, {}", is_odd_tco(0, &mut x), is_odd_tco(2, &mut z));
    println!("{}, {}", is_odd_tco(1, &mut y), is_odd_tco(3, &mut t));
}
