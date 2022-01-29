use std::thread;
use std::sync::Arc;

pub struct Done {
   done: bool,
}

fn wait_till_done(f: Arc<Done>) -> bool {
   while !f.done {}
   true
}

fn main() {
   let d = Done {done: false};
   let b = Arc::new(d);
   let d = b.clone();

   thread::spawn(move || {
      b.done = true;
   });
   wait_till_done(d);
}
