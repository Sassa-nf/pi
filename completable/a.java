import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

public class a {
   public static void main(String [] args) throws Exception {
      CompletableFuture<String> blah = CompletableFuture.supplyAsync(() -> {
         System.out.println("STARTED");
         String doh = new CompletableFuture<String>().orTimeout(500, TimeUnit.MILLISECONDS).exceptionally(_th -> "doh").join();
         System.out.println("WAIT OVER");
         return doh;
      }).thenCompose(it -> {
         System.out.println("ANOTHER SLEEP");
         String doh = new CompletableFuture<String>().orTimeout(500, TimeUnit.MILLISECONDS).exceptionally(_th -> "doh").join();
         System.out.println("WAIT OVER");
         return CompletableFuture.completedFuture(it);
      //}).exceptionally(th -> {
      //   System.out.println("At least we know it got cancelled");
      //   throw th instanceof RuntimeException? (RuntimeException) th: new RuntimeException(th);
      });

      Thread.sleep(200);
      System.out.println("OK, let me cancel: " + blah.orTimeout(100, TimeUnit.MILLISECONDS).exceptionally(_th -> "timeout").join());
      Thread.sleep(1200);
      System.out.println("In the end got: " + blah.join());
   }
}
