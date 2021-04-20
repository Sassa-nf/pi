// https://github.com/gvsmirnov/java-perv/blob/master/labs-8/src/main/java/ru/gvsmirnov/perv/labs/gc/MetaspaceOom.java
import java.io.*;
import java.nio.charset.Charset;
import java.security.SecureClassLoader;
import java.util.ArrayList;

public class MetaspaceOom {

    public static volatile Object sink;

    public static void main(String[] args) throws Exception {
        int sz = Integer.parseInt(args[0]);
        final long pid = getPid();
        final double startMemory = getMemoryUsage(pid); // To load the required classes
        final long startTime = System.currentTimeMillis();

        BottomlessClassLoader loader = new BottomlessClassLoader();

        try {
            for (int i = 0; i < 1000000 / sz; i++) {
                loader = new BottomlessClassLoader();

                for(int j = 0; j < sz; j++)
                   loader.loadAnotherClass();
                System.out.printf("Metaspace use: %.3f\n", getMemoryUsage(pid));
            }
            System.out.println("Done");
            System.in.read();
        } catch (OutOfMemoryError e) {
            long elapsed = System.currentTimeMillis() - startTime;
            double memoryUsage = getMemoryUsage(pid);
            System.err.println(
                    "Got an OOM: " + e.getMessage() + " after loading " + loader.classesLoaded +
                    " classes in " + elapsed + " ms, memory: " + (memoryUsage * 1024) + "M");
        } catch (ClassNotFoundException e) {
            System.err.println("Class generation failed.");
        }
    }

    public static class BottomlessClassLoader extends SecureClassLoader {

        public static volatile Object sink;

        private byte[] classBytes;
        private final String className;
        private final byte[] classNameBytes;
        private final ArrayList<Integer> replaceLocations;
        private final Class<?> sourceClass = CombinatorialExplosion_XXXXXX.class;
        private final String baseName = sourceClass.getName().substring(0, sourceClass.getName().length() - 6);

        private final Charset UTF8_CHARSET = Charset.forName("UTF-8");

        private int classesLoaded = 0;

        public BottomlessClassLoader() {
            super(BottomlessClassLoader.class.getClassLoader());

            this.classBytes = null;
            this.className = sourceClass.getName().replace('.', '/');
            this.classNameBytes = this.className.getBytes(UTF8_CHARSET);
            this.replaceLocations = new ArrayList<>();

            if (loadClassBuffer(className)) {
                findNameLocations();
            }
        }

        public void loadAnotherClass() throws ClassNotFoundException {
            String className = String.format("%s%06d", baseName, classesLoaded++);
            sink = loadClass(className);
        }

        protected byte[] streamToByteArray(InputStream input) throws IOException {
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            int n;
            byte[] buffer = new byte[4096];
            while (-1 != (n = input.read(buffer))) {
                output.write(buffer, 0, n);
            }
            return output.toByteArray();
        }

        protected boolean loadClassBuffer(String className) {
            InputStream stream = getResourceAsStream(className.replace('.', '/') + ".class");
            try {
                classBytes = streamToByteArray(stream);
                return true;
            } catch (IOException e) {
            } finally {
                try {
                    stream.close();
                } catch (IOException e) {
                }
            }

            return false;
        }

        protected void findNameLocations() {
            int matchCount = 0;

            if (classNameBytes.length > 3) {
                for (int position = 0; position < classBytes.length; position++) {
                    if (classNameBytes[matchCount] == classBytes[position]) {
                        matchCount++;

                        if (matchCount == classNameBytes.length) {
                            replaceLocations.add(position - matchCount + 1);
                            matchCount = 0;
                        }
                    } else {
                        matchCount = 0;
                    }
                }
            }
        }

        protected boolean renameClassBufferTo(final String requestedName) {
            if (classBytes == null || requestedName.length() != className.length()) {
                return false;
            }

            byte[] requestedNameBytes = requestedName.replace('.', '/').getBytes(UTF8_CHARSET);

            if (requestedNameBytes.length != classNameBytes.length) {
                return false;
            }

            for (int replaceStart : replaceLocations) {
                System.arraycopy(requestedNameBytes, 0, classBytes, replaceStart, classNameBytes.length);
            }

            return true;
        }

        @Override
        protected Class<?> findClass(final String name) throws ClassNotFoundException {
            Class<?> result;

            try {
                result = super.findClass(name);
            } catch (ClassNotFoundException e) {
                synchronized (this) {
                    if (renameClassBufferTo(name)) {
                        result = defineClass(name, classBytes, 0, classBytes.length);
                    } else {
                        throw e;
                    }
                }
            }

            return result;
        }
    }

    // Kudos to @tagir_valeev for this approach: https://habrahabr.ru/post/245333/
    public static class CombinatorialExplosion_XXXXXX {{
        int a;
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
        try {a=0;} finally {
            a=0;
        }}}}}}}}}}
    }}

    public static long getPid() {
        return ProcessHandle.current().pid();
    }

    public static double getMemoryUsage(long pid) {
        try {
            Process p = new ProcessBuilder()
                    .command("jcmd", Long.toString(pid), "VM.metaspace")
                    .start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String usage = reader.readLine();
            double committed = 0;

            while(usage != null) {
               usage = usage.trim();
               if (usage.indexOf("Non-class space") >= 0 || usage.indexOf("Class space") >= 0) {
                  String [] cc = usage.split("  *");
                  double mul = 1e-6; // kb
                  if (cc[6].equals("MB")) {
                     mul = 1e-3;
                  } else if (cc[6].equals("GB")) {
                     mul = 1.0;
                  }
                  committed += Double.parseDouble(cc[5]) * mul;
               }
               usage = reader.readLine();
            }

            p.destroy();

            return committed;
        } catch(Exception e) {
            throw new AssertionError(e);
        }
    }
}
