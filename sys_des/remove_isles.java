import java.util.ArrayList;

public class remove_isles {
   public static void main(String[] args) throws Exception {
      var mx1 = new boolean[][]{
   {true, false, false, false, false, false},
   {false, true, false, true, true, true},
   {false, false, true, false, true, false},
   {true, true, false, false, true, false},
   {true, false, true, true, false, false},
   {true, false, false, false, false, true}
   };
      print(remove_isles(mx1));
   }

   public static void print(boolean[][] mx) {
      for(var r: mx) {
         for(var c: r) {
            System.out.print(c ? '1': '0');
         }
         System.out.println();
      }
   }

   public static boolean[][] remove_isles(boolean[][] mx) {
      if (mx.length <= 2 || mx[0].length <= 2) {
         return mx;
      }

      var reachable = new boolean[mx.length][];
      reachable[0] = mx[0];
      reachable[mx.length-1] = mx[mx.length-1];

      var ps = new ArrayList<Point>();
      for(var i = 0; i < mx[0].length; i++) {
         if (mx[0][i]) {
            ps.add(new Point(i, 0));
         }

         if (mx[mx.length - 1][i]) {
            ps.add(new Point(i, mx.length - 1));
         }
      }

      for(var i = 1; i < mx.length-1; i++) {
         reachable[i] = new boolean[mx[i].length];
         reachable[i][0] = mx[i][0];
         reachable[i][mx[i].length-1] = mx[i][mx[i].length-1];
         if (mx[i][0]) {
            ps.add(new Point(0, i));
         }

         if (mx[i][mx[i].length-1]) {
            ps.add(new Point(mx[i].length-1, i));
         }
      }

      while(!ps.isEmpty()) {
         var ns = new ArrayList<Point>();
         ps.forEach(p -> {
            visit(reachable, ns, mx, p.x-1, p.y);
            visit(reachable, ns, mx, p.x+1, p.y);
            visit(reachable, ns, mx, p.x, p.y-1);
            visit(reachable, ns, mx, p.x, p.y+1);
         });
         ps = ns;
      }

      return reachable;
   }

   private static void visit(boolean[][] reachable, ArrayList<Point> ns, boolean[][] mx, int x, int y) {
      if (x < 0 || y < 0 || y >= mx.length || x >= mx[0].length || reachable[y][x] || !mx[y][x]) {
         return;
      }

      reachable[y][x] = true;
      ns.add(new Point(x, y));
   }

   static class Point {
      int x;
      int y;
      public Point(int x, int y) {
         this.x = x;
         this.y = y;
      }
   }
}
