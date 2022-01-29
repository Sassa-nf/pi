#include<stdio.h>

char even(int);

char odd(int x) {
   return x && even(x - 1);
}

char even(int x) {
   return odd(x - 1);
}

char odd_loop(int* x) {
   for(;;) {
      (*x)--;
      if (!(*x)) {
         return 1;
      }
      (*x)--;
   }
}

char collatz(int x, int* c, char *done) {
   int cc = *c;
   while(!(*done)) {
      if (x == 1) {
         *c = cc;
         return 1;
      }

      cc++;

      if (x & 1) {
         x = x + x + x + 1;
      } else {
         x = x >> 1;
      }
   }
   *c = cc;
   return 0;
}

int main(int argc, char** argv) {
   int x = 2;
   char done = 0;
//   printf("1 is odd: %d\n", odd(1));
   printf("2 is odd: %d %d\n", odd_loop(&x), x);

   x = 0;
   collatz(20, &x, &done); // collatz is implemented correctly
   printf("collatz converges in %d\n", x);
}
