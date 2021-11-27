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
      for(int i = 0; i < bis.length; i++) {
         BigInteger bi = fact4(10000 + i);
         if (!bi.equals(bis[i])) {
            System.out.println("Oops..." + bi + " != " + bis[i]);
            return;
         }
      }

      long t0 = System.nanoTime();
//      for(int i = 0; i < 10; i++) {
         new Fact(2 * 1024 * 1024).invoke();
//      }

      long t1 = System.nanoTime();
//      for(int i = 0; i < 10; i++) {
         new Fact2(2 * 1024 * 1024).invoke();
//      }
      long t2 = System.nanoTime();
//      for(int i = 0; i < 10; i++) {
        fact3(2 * 1024 * 1024);
//      }
      long t3 = System.nanoTime();
//      for(int i = 0; i < 10; i++) {
        fact4(2 * 1024 * 1024);
//      }
      long t4 = System.nanoTime();
//      for(int i = 0; i < 10; i++) {
        fact4_1(2 * 1024 * 1024);
//      }
      long t5 = System.nanoTime();

      System.out.printf("Fact straightforward: %.3f\nFact multiply equally sized nums: %.3f\nFact multiply only odd: %.3f\nFact multiply only odd-2: %.3f\nFact multiply only odd-2, single-threaded: %.3f\n%s\n",
                        (t1 - t0) / 1e9, (t2 - t1) / 1e9, (t3 - t2) / 1e9, (t4 - t3) / 1e9, (t5 - t4) / 1e9, new Fact(20000).invoke().equals(fact4(20000)));
   }

   public static BigInteger fact3(int n) {
      if (n == 0) {
         return BigInteger.ONE;
      }

      Fact3 f = new Fact3(n);
      BigInteger r = f.invoke();
      return r.shiftLeft(f.shift);
   }

   public static BigInteger fact4(int n) {
      BigInteger res = BigInteger.ONE;
      if (n == 0) {
         return res;
      }

      int[] sz = new int[32 - Integer.numberOfLeadingZeros(n)];
      for(int i = sz.length; i-- > 0; n >>= 1) {
         sz[i] = n;
      }
      int ds = 1;

      ForkJoinTask<BigInteger> one = new Fact4(1, 1).fork();
      int b = sz.length - 1;
      int shifts = b;

      ForkJoinTask<BigInteger>[] forks = new ForkJoinTask[sz.length-1];

      for(int i = 1; i < sz.length; i++) {
         int pow = b;

         b -= 1;
         int from = sz[i-1];
         int to = sz[i];
         from = (from & 1) == 1? from + 2: from + 1; // from is an odd number greater than the end of the previous range
         to = (to & 1) == 1? to + 1: to;
         ds += (to + 1 - from) >> 1; // how many digits will be computed
         shifts += ds * b; // given where we are, these are all even - what power of 2 is skipped

         Fact4 f = new Fact4(from , to);
         forks[i-1] = from > to ? one: ForkJoinTask.adapt(() -> f.invoke().pow(pow));
      }

      return forks(forks, 0, forks.length, 1).invoke().shiftLeft(shifts);
   }

   public static BigInteger fact4_1(int n) {
      BigInteger res = BigInteger.ONE;
      if (n == 0) {
         return res;
      }

      int[] sz = new int[32 - Integer.numberOfLeadingZeros(n)];
      for(int i = sz.length; i-- > 0; n >>= 1) {
         sz[i] = n;
      }
      int ds = 1;

      ForkJoinTask<BigInteger> one = new Fact4(1, 1);
      int b = sz.length - 1;
      int shifts = b;

      ForkJoinTask<BigInteger>[] forks = new ForkJoinTask[sz.length-1];

      for(int i = 1; i < sz.length; i++) {
         int pow = b;

         b -= 1;
         int from = sz[i-1];
         int to = sz[i];
         from = (from & 1) == 1? from + 2: from + 1; // from is an odd number greater than the end of the previous range
         to = (to & 1) == 1? to + 1: to;
         ds += (to + 1 - from) >> 1; // how many digits will be computed
         shifts += ds * b; // given where we are, these are all even - what power of 2 is skipped

         forks[i-1] = from > to ? one: new Fact4(from , to);
      }

      BigInteger prev = BigInteger.ONE;
      for(ForkJoinTask<BigInteger> f: forks) {
         prev = prev.multiply(f.invoke());
         res = res.multiply(prev);
      }

      return res.shiftLeft(shifts);
   }

   static ForkJoinTask<BigInteger> forks(ForkJoinTask<BigInteger>[] fs, int from, int to, int step) {
      if (from + step >= to) {
         return fs[from];
      }

      ForkJoinTask<BigInteger> left = forks(fs, from, to, step << 1);
      ForkJoinTask<BigInteger> right = forks(fs, from + step, to, step << 1);
      return ForkJoinTask.adapt(() -> {
         left.fork();
         return right.invoke().multiply(left.join());
      });
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

   static class Fact4 extends RecursiveTask<BigInteger> {
      int from;
      int to;
      int step;

      public Fact4(int from, int to) {
         this(from, to, 2);
      }

      private Fact4(int from, int to, int step) {
         this.from = from;
         this.to = to;
         this.step = step;
      }

      @Override
      protected BigInteger compute() {
         if (from + step > to) {
            return from < 2? BigInteger.ONE: BigInteger.valueOf(from);
         }

         ForkJoinTask<BigInteger> left = new Fact4(from, to, step << 1).fork();
         return new Fact4(from + step, to, step << 1).invoke().multiply(left.join());
      }
   }
}
