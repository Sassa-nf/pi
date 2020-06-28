use std::time::Instant;

fn bit_count(xs: &[u32]) -> u32 {
   let mut m = 1;
   let mut should = 1;
   let mut r = 0;
   while should > 0 {
      let mut actual = 0;
      should = 0;
      for (i, x) in xs.iter().enumerate() {
         should += (i as u32) & m;
         actual += x & m;
      }
      if should < actual {
         r += m;
      }
      m = m << 1;
   }
   return r;
}

fn find_duplicate(nums: &Vec<u32>) -> u32 {
   let mut m = 1;
   let mut should = 1;
   let mut r = 0;
   while should > 0 {
      let mut actual = 0;
      should = 0;
      for (i, x) in nums.iter().enumerate() {
         should += (i as u32) & m;
         actual += x & m;
      }
      if should < actual {
         r += m;
      }
      m = m << 1;
   }
   return r;
}

fn tortoise(xs: &[u32]) -> u32 {
   let mut t = xs[0];
   let mut h = xs[xs[0] as usize];
   while t != h {
      t = xs[t as usize];
      h = xs[xs[h as usize] as usize];
   }

   t = 0;
   while t != h {
      t = xs[t as usize];
      h = xs[h as usize];
   }
   return h;
}

const ITERS: u32 = 10000;

fn main() {
   let xs = [13, 2, 3, 13, 13, 6, 7, 13, 9, 10, 11, 12, 13, 13];
   println!("{}", bit_count(&xs));
   println!("{}", tortoise(&xs));
   let mut xs: Vec<u32> = (1..=65538).collect();
   xs.push(2);

   let now = Instant::now();
   for _ in 0..ITERS {
      find_duplicate(&xs);
   }
   println!("Bit count: {}", now.elapsed().as_micros());

   let xs = xs.as_slice();

   let now = Instant::now();
   for _ in 0..ITERS {
      bit_count(xs);
   }
   println!("Bit count: {}", now.elapsed().as_micros());

   let now = Instant::now();
   for _ in 0..ITERS {
      tortoise(xs);
   }
   println!("Hare: {}", now.elapsed().as_micros());
}
