'use strict';

const parseError = (msg, pos) => [{
  err: new Error(`Parse error: expected ${msg} at line ${pos.line}, column ${pos.col}`)
}, pos];

const or = (l, ...r) => (str, pos) => {
  let res;
  let end;
  for(const p of [l].concat(r)) {
    [res, end] = p(str, pos);
    if (!res.err) {
      return [res, end];
    }
  }

  return [res, pos];
};

const and = (...r) => (str, pos) => {
  let res = [];
  for(const p of r) {
    const [value, end] = p(str, pos);
    if (value.err) {
      return [value, pos];
    }
    pos = end;
    res = res.concat(value);
  }
  return [res, pos];
};

const empty = and();

const maybe = (p) => or(p, empty);

const nl = (str, pos) => pos.line < str.length - 1 && str[pos.line].length === pos.col ?
      [[], {line: pos.line+1, col: 0}]:
      parseError('LF', pos);

const eof = (str, pos) => pos.line === str.length - 1 && str[pos.line].length === pos.col ?
      [[], pos]:
      parseError('EOF', pos);

const lift = (f) => (x) => (str, pos) => [f(x), pos];

const bind = (p, ...f) => (str, pos) => {
  let res;
  for(const g of [() => p].concat(f)){
    const [value, end] = g(res)(str, pos);
    if (value.err) {
      return [value, pos];
    }
    pos = end;
    res = value;
  }
  return [res, pos];
};

const asstr = (...p) => bind(and.apply(null, p),
			     lift((res) => [res.join('')]));

const skip = (p) => bind(p, lift(() => []));

// have to make a reference to zeromore(p) lazy
const onemore = (p) => and(p, (str, pos) => zeromore(p)(str, pos));

const zeromore = (p) => maybe(onemore(p));

const anychr = (str, pos) => pos.col < str[pos.line].length ?
      [[str[pos.line][pos.col]], {line: pos.line, col: pos.col + 1}]:
      parseError('no LF', pos);

const chr = (c) => (str, pos) => bind(anychr,
                                      res => (str, end) => res[0] !== c ?
                                      parseError(`'${c}'`, pos):
                                      [res, end])(str, pos);

const twochr = (c, d) => (str, pos) => bind(anychr,
                                            res => (str, end) => res[0] < c || res[0] > d ?
                                            parseError(`a char in range '${c}'..'${d}'`, pos):
                                            [res, end])(str, pos);

const range = (s) => {
  const [parsers, end] = and(onemore(or(bind(and(anychr, skip(chr('.')), skip(chr('.')), anychr),
                                             lift((res) => [twochr.apply(null, res)])),
                                        bind(anychr,
                                             lift((res) => [chr(res[0])])))),
                             eof)([s], {line: 0, col: 0});
  parsers.push((str, pos) => parseError(`a char from range '${s}'`, pos));
  return or.apply(null, parsers);
};

const decimal = range('0..9');
const hex = or(decimal, range('a..fA..F'));

const unesc = (str, pos) => {
  const c = str[pos.line][pos.col];
  if (!c || c.codePointAt(0) < 32 || c === '"') {
    return chr('\\')(str, pos);
  }

  const [r, end] = chr(c)(str, pos);
  if (c !== '\\') {
    return [r, end];
  }

  return or(range('"\\/'),
            nl,
            bind(range('bfnrtuBFNRTU'),
                 lift((res) => [{
                   b: '\b',
                   f: '\f',
                   n: '\n',
                   r: '\r',
                   t: '\t'
                 }[res[0].toLowerCase()]]),
                 (res) => res[0] ? (str, pos) => [res, pos]:
                 bind(asstr(hex, hex, hex, hex),
                      lift((res) => [String.fromCharCode(parseInt(res[0], 16))])))
           )(str, end);
};

const string = asstr(skip(chr('"')),
                     zeromore(unesc),
                     skip(chr('"'))
                    );

const number = bind(asstr(maybe(range('+-')),
                          onemore(decimal),
                          maybe(chr('.')),
                          zeromore(decimal),
                          maybe(and(range('eE'),
                                    maybe(range('+-')),
                                    onemore(decimal)))),
                    lift((res) => [res[0].indexOf('.') >= 0 ||
                                   res[0].indexOf('e') >= 0 ||
                                   res[0].indexOf('E') >= 0 ?
                                   parseFloat(res[0]):
                                   parseInt(res[0])]));

const symbol = bind(asstr(onemore(range('a..zA..Z+-*/!^:_=0..9'))),
                    lift((res) => [Symbol.for(res[0])]));

const list = (str, pos) => bind(and(skip(chr('(')),
                                    or(expressions, skip(zeromore(space))),
                                    skip(chr(')'))),
                                lift((res) => [res]))(str, pos);

const quote = (x) => typeof x === 'symbol' ? [Symbol.for('quote'), x]:
      Array.isArray(x) ? [Symbol.for('list')].concat(x.map(quote)):
      x;

const quoted = and(skip(chr("'")),
                   bind(or(symbol,
                           list),
                        lift((res) => res.map(quote))));

const comment = bind(chr(';'),
                     () => (str, pos) => [[str[pos.line].substring(pos.col)],
                                          {line: pos.line < str.length - 1? pos.line+1: pos.line, col: 0}]);
const space = or(nl,
                 comment,
                 range(' \t'));

const expression = or(string, number, symbol, list, quoted);

const expressions = and(skip(zeromore(space)),
                        expression,
                        zeromore(and(skip(onemore(space)),
	                             expression)),
                        skip(zeromore(space)));

exports.parse = (str) => {
  const lines = str.split('\n');
  const [res, pos] = and(expressions,
                         eof)(lines, {line: 0, col: 0});
  if (!res.err) {
    
  }
  return res;
};
