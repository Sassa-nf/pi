use std::time::Instant;

fn bit_count(xs: &[u32]) -> u32 {
   let n = xs.len() as u32;
   let mut should = n >> 1;
   let mut r = 0;
   let mut m = 0;
   while should > 0 {
      let mut actual = 0;
      let mm = 1 << m;
      for x in xs.iter() {
         actual += x & mm;
      }
      if should < (actual >> m) {
         r += mm;
      }
      m += 1;
      should = n >> m;
      should = ((should >> 1) << m) + (if (should & 1) > 0 {
            n - (should << m)
         } else {
            0
         });
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
   let mut r = 0;
   for _ in 0..ITERS {
      r = find_duplicate(&xs);
   }
   println!("Bit count: {}; {}", now.elapsed().as_micros(), r);

   let xs = xs.as_slice();

   let now = Instant::now();
   for _ in 0..ITERS {
      r = bit_count(xs);
   }
   println!("Bit count: {}; {}", now.elapsed().as_micros(), r);

   let now = Instant::now();
   for _ in 0..ITERS {
      r = tortoise(xs);
   }
   println!("Hare: {}; {}", now.elapsed().as_micros(), r);
}
