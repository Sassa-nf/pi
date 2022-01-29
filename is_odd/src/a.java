public class a {
   private static final int ITERS = 10;
   public static void main(String [] args) {
      test_odd(2);
      test_odd(4);
      test_odd(1);
   }

   public static void test_odd(int n) {
      int c = 0;
      long t0 = System.nanoTime();
      for(int i = 0; i < ITERS; i++) {
         c += is_odd(n)? 1: 0;
      }
      t0 = System.nanoTime() - t0;

      System.out.println(n + " is odd: " + (c > 0) + " (" + (t0 / 1e9 / ITERS) + " seconds per iteration)");
   }

   public static boolean is_odd(int n) {
      while(n != 0) {
         n += 2;
      }
      return false;
   }
}
