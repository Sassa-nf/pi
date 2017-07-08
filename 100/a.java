/*
 * Output numbers 1..100 without using loops or if-statements
 */
public class a {
  public static interface F<A> {
    public A f(A x);
  }

  public static interface Num {
    public <A> A g(F<A> f, A x);
    public static final Zero zero = new Zero();
    public static final One one = new One();
    public static final Succ succ = new Succ();
  }

  public static class Succ implements F<Num> {
    protected Succ(){}

    public Num f(Num n) {
      return new Num(){
        public <A> A g(F<A> f, A x) {
          return f.f(n.g(f, x));
        }

        public String toString(){
          return "1+" + n;
        }
      };
    }
  }

  public static class Zero implements Num {
    protected Zero(){}
    public <A> A g(F<A> f, A x) {
      return x;
    }

    public String toString() {
      return "0";
    }
  }

  public static class One implements Num {
    protected One() {}
    public <A> A g(F<A> f, A x) {
      return f.f(x);
    }
    public String toString() {
      return "1";
    }
  }

  public static Num add(Num m, Num n) {
    return m.g(Num.succ, n);
  }

  public static Num mul(Num m, Num n) {
    return m.g(new F<Num>(){
      public Num f(Num x) {
        return add(n, x);
      }
    }, Num.zero);
  }

  public static Num exp(Num n, Num p) {
    return p.g(new F<Num>(){
      public Num f(Num x) {
        return mul(n, x);
      }
    }, Num.one);
  }

  public static F<Integer> print() {
    return new F<Integer>(){
      public Integer f(Integer x) {
        System.out.println(++x);
        return x;
      }
    };
  }

  public static Num intToNum(int i) {
    Num two = add(Num.one, Num.one);
    Num five = add(Num.one, add(two, two));
    Num[] bits = new Num[]{Num.zero, Num.one};
    return exp(two, five).g(new F<Num>(){
      protected int j = i;
      public Num f(Num x){
        int k = j;
        j <<= 1;
        return bits[k >>> 31].g(Num.succ, add(x, x));
      }
    }, Num.zero);
  }

  public static void main(String [] args) {
    int i = Integer.parseInt(args[0]);
    intToNum(i).g(print(), 0);
  }
}
