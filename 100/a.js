'use strict';

const zero = f => x => x;
const succ = g => f => x => g(f)(f(x));
const one = succ(zero);
const two = succ(one);

const add = m => m(succ);
const mul = m => n => n(add(m))(zero);
const exp = m => n => n(mul(m))(one);

const five = succ(add(two)(two));

const bits = [zero, one];
const intToNum = i => exp(two)(five)(n => {
  const k = i >>> 31;
  i <<= 1;
  return bits[k](succ)(add(n)(n));
})(zero);

intToNum(1024)(x => {
  x++;
  console.log(x);
  return x;
})(0);
