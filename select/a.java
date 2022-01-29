import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;

import java.net.InetSocketAddress;
import java.net.StandardSocketOptions;

import java.nio.ByteBuffer;

public class a {
   public static void main(String [] args) throws Exception {
      SocketChannel sc = SocketChannel.open();

      sc.connect(new InetSocketAddress("127.0.0.1", 8080));
      sc.configureBlocking(false);

      Selector sel = Selector.open();
      SelectionKey sk = sc.register(sel, SelectionKey.OP_READ);
      sk.interestOps(SelectionKey.OP_WRITE);

      ByteBuffer buf = ByteBuffer.allocate(100 * 1024 * 1024);

      buf.put("GET /books HTTP/1.1\n\n".getBytes("US-ASCII"));
      buf.flip();

      while(buf.remaining() > 0) {
         int n;
         do {
            sel.selectedKeys().clear();
            n = sel.select(1);
            System.out.println("\nhow many ready? " + n);
         }while(n == 0);

         int w = sc.write(buf);
         System.out.println("Wrote: " + w + " " + buf.remaining());
         System.out.println("Read back: " + sc.read(buf));
      }

      buf.clear();

      sk.interestOps(SelectionKey.OP_READ);
      while(buf.remaining() > 0) {
         int r = 0;
         do {
            sel.selectedKeys().clear();
            int n = sel.select(10000);
            System.out.println("\nhow many ready? " + n);
            if (sk.isReadable()) {
               System.out.println("channel is open: " + sc.isOpen());
               r = sc.read(buf);
               System.out.println("is read-ready? " + sk.isReadable());
            }
         } while(r == 0);

         if (r < 0) {
            System.out.println("Ok, we know it is closed");
            System.out.println("channel is open: " + sc.isOpen());

            sk.interestOps(SelectionKey.OP_WRITE);
            sel.selectedKeys().clear();

            int w = 0;
            int i = 0;
            int n = 0;

            try {
            for(; i < 100000; i++) {
               n = sel.select(10000);
               buf.clear();
               int ww = sc.write(buf);
               if (ww <= 0 || n == 0) {
                  System.out.println("oops: " + i + " " + n + " " + ww);
                  break;
               }
               w += ww;
            }
            } catch (Exception ioe) {
               System.out.println("aha! " + i + " " + n + " " + ioe);
               sk.interestOps(SelectionKey.OP_READ);
               sel.selectedKeys().clear();
               i = -1;
               try {
                  n = sel.select(10000);
                  i = sc.read(buf);
               }catch(Exception e) {
               }
               System.out.println(" and then..." + n + " " + i);
            }

            System.out.println("wrote: " + w + " " + buf.remaining());
            System.out.println("channel is open: " + sc.isOpen());
            throw new Exception("connection closed");
         }
         buf.flip();
         byte[] bs = new byte[r];
         buf.get(bs);
         System.out.print(new String(bs));

         buf.clear();
      }
   }
}
