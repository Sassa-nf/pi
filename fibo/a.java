import java.math.BigInteger;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;
import java.util.concurrent.atomic.AtomicInteger;

public class a {
   public static void main(String[] as) throws Exception {
      BigInteger[] bis = new BigInteger[1000];

      for(int i = 0; i < bis.length; i++) {
         bis[i] = new Fact(10000 + i).invoke();
      }
      for(int i = 0; i < bis.length; i++) {
         BigInteger bi = new Fact2(10000 + i).invoke();
         if (!bi.equals(bis[i])) {
            System.out.println("Oops..." + bi + " != " + bis[i]);
            return;
         }
      }
      for(int i = 0; i < bis.length; i++) {
         BigInteger bi = fact3(10000 + i);
         if (!bi.equals(bis[i])) {
            System.out.println("Oops..." + bi + " != " + bis[i]);
            return;
         }
      }

      long t0 = System.nanoTime();
//      for(int i = 0; i < 1000; i++) {
         new Fact(2 * 1024 * 1024).invoke();
//      }

      long t1 = System.nanoTime();
//      for(int i = 0; i < 1000; i++) {
         new Fact2(2 * 1024 * 1024).invoke();
//      }
      long t2 = System.nanoTime();
        fact3(2 * 1024 * 1024);
      long t3 = System.nanoTime();

      System.out.printf("Fact straightforward: %.3f\nFact multiply equally sized nums: %.3f\nFact multiply only odd: %.3f\n%s\n",
                        (t1 - t0) / 1e9, (t2 - t1) / 1e9, (t3 - t2) / 1e9, new Fact(20000).invoke().equals(new Fact2(20000).invoke()));
   }

   public static BigInteger fact3(int n) {
      if (n == 0) {
         return BigInteger.ONE;
      }

      Fact3 f = new Fact3(n);
      BigInteger r = f.invoke();
      return r.shiftLeft(f.shift);
   }

   static class Fact extends RecursiveTask<BigInteger> {
      int from;
      int to;

      public Fact(int n) {
         this(0, n);
      }

      private Fact(int from, int to) {
         this.from = from;
         this.to = to;
      }

      @Override
      protected BigInteger compute() {
         if (from == to) {
            return from == 0? BigInteger.ONE: BigInteger.valueOf(from);
         }

         int mid = (from + to) >>> 1;
         ForkJoinTask<BigInteger> left = new Fact(from, mid).fork();
         BigInteger right = new Fact(mid+1, to).invoke();
         return right.multiply(left.join());
      }
   }

   static class Fact2 extends RecursiveTask<BigInteger> {
      int from;
      int to;
      int step;

      public Fact2(int n) {
         this(0, n, 1);
      }

      private Fact2(int from, int to, int step) {
         this.from = from;
         this.to = to;
         this.step = step;
      }

      @Override
      protected BigInteger compute() {
         if (from + step > to) {
            return from < 2? BigInteger.ONE: BigInteger.valueOf(from);
         }

         ForkJoinTask<BigInteger> left = new Fact2(from, to, step << 1).fork();
         BigInteger right = new Fact2(from + step, to, step << 1).invoke();
         return right.multiply(left.join());
      }
   }

   static class Fact3 extends RecursiveTask<BigInteger> {
      int from;
      int to;
      int step;
      public int shift;

      public Fact3(int n) {
         this(1, n, 1, 0);
      }

      private Fact3(int from, int to, int step, int shift) {
         this.from = from;
         this.to = to;
         this.step = step;
         this.shift = shift;
      }

      @Override
      protected BigInteger compute() {
         if (from + step > to) {
            return from < 2? BigInteger.ONE: BigInteger.valueOf(from);
         }

         if (from == 2 && step > 1) {
            from = 1;
            to >>>= 1;
            step >>= 1;
            shift++;
         }

         Fact3 lf = new Fact3(from, to, step << 1, shift);
         ForkJoinTask<BigInteger> left = lf.fork();
         Fact3 rf = new Fact3(from + step, to, step << 1, shift);
         BigInteger right = rf.invoke().multiply(left.join());

         shift = lf.shift + rf.shift;
         return right;
      }
   }
}
