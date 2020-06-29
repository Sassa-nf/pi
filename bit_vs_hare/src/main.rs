/*
 * Given an array nums containing n + 1 integers where each integer is between
 * 1 and n (inclusive), prove that at least one duplicate number must exist.
 * Assume that there is only one duplicate number, find the duplicate one.
 *
 * You must not modify the array (assume the array is read only).
 * You must use only constant, O(1) extra space.
 * Your runtime complexity should be less than O(n^2).
 * There is only one duplicate number in the array, but it could be repeated
 * more than once.
 *
 * Input: [1,3,4,2,2]
 * Output: 2
 *
 * Input: [3,1,3,4,2]
 * Output: 3
 *
 * The discussion of the problem points out one can represent this as a
 * problem of finding a loop in a graph. Then arranging two arrays:
 *
 * [0, 1, 2, 3, 4] - indices
 * [1, 3, 4, 2, 2] - actual input
 *
 * lends itself to the interpretation that this is a linked list 0->1, 1->3,
 * 2->4, 3->2, 4->2.
 *
 * Since 0 is not used, then xs[0] is definitely not part of a loop. Also,
 * since all numbers are between 1 and n, then the loop definitely is entered.
 * (All indices are reachable from 0).
 *
 * Thus we can use the tortoise-and-hare algorithm to find the loop, and thus
 * the repetition. It can be shown to be O(n)
 *
 * However, that's not the only way to work out the loop in O(n). Bit counting
 * also works. It is guaranteed to work in less than 32 re-scans of the array, but
 * this is much faster than the tortoise-and-hare algorithm, because it is just
 * a scan of numbers, not interpretation of them as indices. The maths is easy
 * to vectorize, and the scan is in cache-efficient order, not random.
 *
 * For the array of 64K entries and a very large loop this is 2x faster than the
 * tortoise-and-hare. (But the same implementation in Python is 100x slower) For random
 * arrays tortoise-and-hare is faster.
 *
 * Bit counting works like so: treat all numbers as a sequence of 0..n, not 1..n, then
 * compare bit parity of the original sequence with the parity of the actual sequence.
 *
 * Then the repetition of some number comes because some of the numbers are replaced,
 * 0 being one of those (the actual sequence does not have 0). Now, consider what
 * happens to bit parity. When removing one number, and adding another, we are removing
 * some ones and zeroes, and replace them with others. The counts of ones for each bit
 * is reduced, when we take out a number with a 1 in that position, and insert a number
 * with a zero in that position. The counts of ones increases, when we take out a
 * number with a 0 in that position, and insert a number with a 1 in that position.
 * Because one of the numbers we take out is a 0, then the bit parity for the positions
 * where the inserted number has 1 increases.
 *
 * The expected parity for each bit position can be worked out from the bit position
 * and the length of the sequence alone.
 */
use std::time::Instant;

use rand::*;

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

fn shuffle(mut xs: Vec<u32>) -> Vec<u32> {
   let mut rnd = rand::thread_rng();
   for i in 0..xs.len() {
      let j = (rnd.gen::<f64>() * i as f64) as usize;
      let o = xs[i];
      xs[i] = xs[j];
      xs[j] = o;
   }

   return xs;
}

const ITERS: usize = 10000;

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

   let mut vecs: Vec<Vec<u32>> = vec![];
   let mut rnd = rand::thread_rng();
   for _ in 0..ITERS {
      let n = (rnd.gen::<f64>() * 200000 as f64) as usize + 1;
      let extra = (rnd.gen::<f64>() * n as f64) as u32 + 1;
      let repeats = (rnd.gen::<f64>() * n as f64) as usize + 1;
      let mut xs = vec![0u32; n];
      for (i, x) in xs.iter_mut().enumerate() {
         *x = i as u32;
      }
      xs[0] = extra;
      xs = shuffle(xs);
      let mut extras = vec![extra; repeats];
      xs.append(&mut extras);
      xs = xs[repeats-1..].to_vec();
      xs = shuffle(xs);
      vecs.push(xs);
   }

   let now = Instant::now();
   for i in 0..ITERS {
      r = bit_count(&vecs[i].as_slice());
   }
   println!("Bit count: {}; {}", now.elapsed().as_micros(), r);

   let now = Instant::now();
   for i in 0..ITERS {
      r = tortoise(&vecs[i].as_slice());
   }
   println!("Hare: {}; {}", now.elapsed().as_micros(), r);
}
