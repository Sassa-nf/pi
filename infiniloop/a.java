import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;
import java.util.logging.*;

public class a extends JFrame {
   public static void main(String[] args) throws Exception {
      new a(args).open();
      System.exit(0);
   }

   JTextField tm;
   JButton btn;
   boolean done;

   public a(String[] args) {
      JPanel p = new JPanel();
      p.setLayout(new FlowLayout());
      p.add(btn = new JButton("Press to Exit"));
      p.add(tm = new JTextField(20));
      this.add(p);
      btn.addActionListener(new ActionListener() {
         public void actionPerformed(ActionEvent e) {
            Logger.getLogger(a.class.getName()).info("done...");
            done = true;
         }
      });
   }

   public void open() {
      pack();
      setLocationRelativeTo(null);
      setVisible(true);

      while(!done) {
         tm.setText("" + new java.util.Date());
         try {
            Thread.sleep(500);
         }catch(Exception ex) {
            Logger.getLogger(a.class.getName()).log(Level.SEVERE, ex.getMessage(), ex);
         }
      }
   }
}
