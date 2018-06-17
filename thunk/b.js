'use strict';

let j = 0;
const box = x => ({x: x, j: j++});
const thunk = (boxed, cont) => ({x: boxed, f: cont, j: j++});
const lazy = cont => thunk(box(), cont);
// unboxing apply
const uap = f => x => thunk(x, f);

const dbg = t => ({x: typeof t.x === 'object' && t.x.x? dbg(t.x): t.x,
                   i: t.i,
                   f: !!t.f});

const introspect = (t, j) => {
  j = j || 5;
  if (typeof t !== 'object') {
   const v = {};
   v[typeof t] = t;
   return v;
  }
  if (t.f) {
    return {thunk: introspect(t.x, j), j: t.j};
  }
  if (t.x) {
    return {box: introspect(t.x, j), j: t.j};
  }
  if (t.cons) {
    return {list: t.cons === 'Cons'? introspect(t.h): '[]', i: t.i,
            t: t.i >= j ? '...': (t.t && introspect(t.t, j || t.i))};
  }
  return {object: t};
};

const compute = (thunk) => {
  let p = thunk;
  while(p && p.f) {
    const xf = typeof p.x === 'object' && p.x.f;
    if (!xf) {
      const r = p.f(p.x.x);
      if (r.f) {
        p.f = box;
        r.p = p;
        p = r;
        p.computing = true;
        continue;
      }

      p.x = r.x;
      const pp = p.p;
      if (pp) {
        pp.x = box(p.x);
      }
      delete p.f; // not a thunk anymore
      delete p.p; // no need to refer to parent anymore
      delete p.computing; // not computing anymore
      p = pp;
    } else {
      const pp = p.x;
      if (pp.computing) {
        throw new Error('doh! loop');
      }
      pp.p = p; // point back to parent
      pp.computing = true;
      p = pp;
    }
  }
  return thunk.x;
};

let i = 0;
const cons = h => t => box({cons: 'Cons', h: h, t: t, i: i++});
const nil = box({cons: 'Nil'});

const foldr = f => z => uap(l => l.cons === 'Cons'?
                                    f(l.h)(foldr(f)(z)(l.t)):
                                    z);
const map = f => foldr(h => cons(f(h)))(nil);
const head = uap(l => {
  if (l.cons === 'Cons') {
    return l.h;
  }
  throw new Error('head of empty list');
});
const tail = uap(l => {
  if (l.cons === 'Cons') {
    return l.t;
  }
  throw new Error('tail of empty list');
});
const tails = xs => uap(l => l.cons === 'Cons'?
                                cons(xs)(tails(l.t)):
                                cons(nil)(nil))(xs);
const drop = n => xs => uap(x => x === 0?
                                  xs:
                                  uap(l => l.cons === 'Cons'?
                                             drop(box(x-1))(l.t):
                                             nil)(xs))(n);
const closure = {};
closure.fibs = lazy(() => cons(box(0))
                    (cons(box(1))
                         (map(ts => uap(h => uap(t => (console.log('working out', h+t),box(h+t)))
                                                (head(tail(ts))))
                                       (head(ts)))
                             (tails(closure.fibs)))));

const fib7 = lazy(() => head(drop(box(7))(closure.fibs)));
const fib5 = lazy(() => head(drop(box(5))(closure.fibs)));
const fib4 = lazy(() => head(drop(box(4))(closure.fibs)));
console.log(compute(fib5));
console.log('I', i, 'J', j);
console.log(compute(fib4));
console.log('I', i, 'J', j);
console.log(compute(fib7));
console.log('I', i, 'J', j);
