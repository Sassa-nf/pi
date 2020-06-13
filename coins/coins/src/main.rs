use std::slice::Iter;
use std::thread;
use std::time::Instant;

fn change_mx(amount: usize, coins: Iter<u32>) -> Vec<u32> {
   let mut row0 = vec![0; amount+1];
   row0[0] = 1;
   for c in coins {
      let c = *c as usize;
      for i in c..(amount+1) {
         row0[i] += row0[i - c];
      }
   }

   row0
}

fn change(amount: usize, coins: Vec<u32>) -> u32 {
   let now = Instant::now();
   let r = if coins.len() < 2 {
      change_mx(amount, coins.iter())[amount]
   } else {
      let mut half_coins = Vec::new();
      half_coins.extend_from_slice(&coins[0..coins.len() / 2]);
      let mx_l = thread::spawn(move || change_mx(amount, half_coins.iter()));
      let mut mx_r = change_mx(amount, coins[coins.len() / 2..].iter());
      mx_r.reverse();
      mx_l.join().unwrap().iter().zip(mx_r.iter()).map(|v| v.0 * v.1).sum()
   };
   println!("{}", now.elapsed().as_micros());
   r
}

fn main() {
   println!("{}", change(500, vec![3,5,7,8,9,10,11]));
}
