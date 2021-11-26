// -XX:ActiveProcessorCount=8

import java.math.BigInteger;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;

public class b {
  public static void main(String[] a) {
    System.out.printf("Available CPUs: %d\nParallelism: %d\n", Runtime.getRuntime().availableProcessors() , ForkJoinPool.getCommonPoolParallelism());
    for(int i=0; i<40; i++)
    System.out.println(new Fibo(i).compute().b);

    System.out.println(new Fibo(90).compute().b);
  }

  static long fibo(int n) {
    if (n == 0) return 0;
    long a = 0;
    long b = 1;
    long c = 1;
    for(int i = Integer.highestOneBit(n) >>> 1; i!=0; i >>= 1) {
       long e = a*b + b*c;
       b *= b;
       c *= c;
       a *= a;
       a += b;
       c += b;
       b = e;
       if ( (n & i) != 0 ) {
          e = c;
          c += b;
          a = b;
          b = e;
       }
    }
    return b;
  }

  static class Fibo extends RecursiveTask<Fibo> {
    int n;
    BigInteger a;
    BigInteger b;
    BigInteger c;

    public Fibo(int n) {
       this.n = n;
    }

    @Override
    protected Fibo compute() {
       if (n < 2){
          c = BigInteger.ONE;
          a = n == 0? c: BigInteger.ZERO;
          b = c.subtract(a);

          return this;
       }
       ForkJoinTask<Fibo> r = new Fibo(n >> 1);
       ForkJoinTask<BigInteger> nub = ForkJoinTask.adapt(() -> r.join().a.add(r.join().c).multiply(r.join().b)).fork();
       ForkJoinTask<BigInteger> b2 = ForkJoinTask.adapt(() -> r.join().b.multiply(r.join().b)).fork();
       ForkJoinTask<BigInteger> a2 = ForkJoinTask.adapt(() -> r.join().a.multiply(r.join().a)).fork();
       ForkJoinTask<BigInteger> c2 = ForkJoinTask.adapt(() -> r.invoke().c.multiply(r.join().c));
       c = c2.invoke().add(b2.join());
       a = a2.join().add(b2.join());
       b = nub.join();

       if ((n & 1) != 0) {
          a = b;
          b = c;
          c = c.add(a);
       }
       
       return this;
    }
  }
  
}
