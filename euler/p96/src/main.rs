use std::collections::HashMap;
use std::env;
use std::fs;
use std::io;

fn rows(_row: usize, col: usize) -> Vec<(usize, usize)> {
    (0..9).map(|r| (r, col)).collect()
}

fn cols(row: usize, _col: usize) -> Vec<(usize, usize)> {
    (0..9).map(|c| (row, c)).collect()
}

fn cell(row: usize, col: usize) -> Vec<(usize, usize)> {
    let core_r = (row / 3) * 3;
    let core_c = (col / 3) * 3;
    (core_r..core_r+3).flat_map(move |r| {
        (core_c..core_c+3).map(move |c| (r, c))
    }).collect()
}

fn cover(field: &Vec<u16>, cells: &Vec<(usize, usize)>) -> HashMap<u16, usize> {
    // collect the number of cells that can be used to cover exactly a certain bit pattern
    let mut cover_sets: HashMap<u16, usize> = HashMap::from([(0, 0)]);

    for (r, c) in cells {
        let j = r * 9 + c;
        let w = field[j];
        for k in cover_sets.clone().keys() {
            cover_sets.insert(k | w, 0);
        }
    }

    for (r, c) in cells {
        let j = r * 9 + c;
        let w = field[j];
        for k in cover_sets.clone().keys() {
            if (k & w) != w {
                continue;
            }

            cover_sets.entry(*k)
                .and_modify(|c| *c += 1);
        }
    }

    cover_sets
}

fn mark(changes: &Vec<(usize, usize)>, field: &mut Vec<u16>) -> Vec<(usize, usize)> {
    let mut new_ch: HashMap<(usize, usize), bool> = HashMap::new();
    for &(row, col) in changes {
        let i = row * 9 + col;
        let v = field[i];
        let field_was = field.clone();

        for f in [rows, cols, cell] {
            let cells = f(row, col);
            let mut cover_sets = cover(field, &cells);

            //print_cover_sets(&cover_sets);

            // keep only those that are able to cover the changed cell entirely
            cover_sets.retain(|k, w| {
                (k & v) == v && k.count_ones() == *w as u32
            });

            // now find the key with min count_ones
            let cover = cover_sets.keys().min_by_key(|k| k.count_ones());
            if cover.is_none() {
                continue
            }

            let cover = cover.unwrap();
            for (r, c) in &cells {
                let j = r * 9 + c;
                let w = field[j];
                let b = w & cover;
                if b == 0 || b == w {
                    // skip, if this is a cell that forms the cover set (b == w), or if it will not
                    // be modified by excluding the cover set
                    continue;
                }

                field[j] = w & !cover;
                new_ch.insert((*r, *c), true);
            }
        }

        //print_transition(&field_was, &field, row, col);
    }

    new_ch.into_keys().collect()
}

fn print_transition(field_was: &Vec<u16>, field: &Vec<u16>, row: usize, col: usize) {
    let m = HashMap::from([((row, col), true)]);
    println!("============================================================================================");
    for r in 0..9 {
        if r == 3 || r == 6 {
            println!("----------------------------------               -----------------------------------");
        } else {
            println!();
        }

        for rr in 0..3 {
            let s1 = print_row(&field_was, &m, r, rr);
            let s2 = print_row(&field, &m, r, rr);
            println!("{}         {}", s1, s2);
        }
    }
}

fn print_cover_sets(cover_sets: &HashMap<u16, usize>) {
    println!("::::::::::::::::::::::::::::::::");

    let mut keys: Vec<_> = cover_sets.keys().collect();
    keys.sort_by_key(|k| (k.count_ones(), *k));
    let mut s = String::new();
    for k in keys {
        s.push_str(", ");
        for i in 0..9 {
            if (k & (1 << i)) != 0 {
                s.push(' ');
                s.push(char::from_digit(i + 1, 16).unwrap());
            }
        }
        s.push_str(" -> ");
        s.push_str(format!("{}", cover_sets[k]).as_str());
    }

    if s.len() > 0 {
        s.remove(0);
        s.remove(0);
    }
    println!("{}", s);
}

fn print_row(field: &Vec<u16>, changes: &HashMap<(usize, usize), bool>, row: usize, rr: u32) -> String {
    let mut s = String::new();

    for c in 0..9 {
        if c == 3 || c == 6 {
            s.push_str(" |");
        }

        let mut v = field[row * 9 + c] >> (3 * rr);

        if !changes.get(&(row, c)).is_none() {
            s.push('>');
        } else {
            s.push(' ');
        }

        for cc in 1..4 {
          if (v & 1) == 0 {
              s.push(' ');
          } else {
              s.push(char::from_digit(cc + 3 * rr, 10).unwrap());
          }
          v = v >> 1;
        }
    }

    s
}

fn print_field(changes: &Vec<(usize, usize)>, field: &Vec<u16>) {
    println!("=========================================");

    let mut m: HashMap<(usize, usize), bool> = HashMap::new();
    for &(r, c) in changes {
        m.insert((r, c), true);
    }

    for r in 0..9 {
        if r == 3 || r == 6 {
            println!("-----------------------------------------");
        } else {
            println!();
        }

        for rr in 0..3 {
            let s = print_row(field, &m, r, rr);
            println!("{}", s);
        }
    }
}

fn validate(field: &Vec<u16>) -> Option<(usize, usize)> {
    for row in 0..9 {
        let mut s = 0;
        for col in 0..9 {
            let i = row * 9 + col;
            let v = field[i];
            if v.count_ones() != 1 {
                return Some((row, 9));
            }

            s |= v;
        }

        if s != 0x1ff {
            return Some((row, 9));
        }
    }

    for col in 0..9 {
        let mut s = 0;
        for row in 0..9 {
            let i = row * 9 + col;
            let v = field[i];
            s |= v;
        }

        if s != 0x1ff {
            return Some((9, col));
        }
    }

    for rr in 0..3 {
        for cc in 0..3 {
            let mut s = 0;

            for r in 0..3 {
                let r = rr * 3 + r;

                for c in 0..3 {
                    let c = cc * 3 + c;
                    let i = r * 9 + c;
                    let v = field[i];
                    s |= v;
                }
            }

            if s != 0x1ff {
                return Some((rr * 3, cc * 3));
            }
        }
    }

    None
}

// assuming there is still work to do, find a cell with the smallest number of choices -
// or indicate that it is a broken puzzle, eg backtrack is needed.
fn best_cover(field: &Vec<u16>) -> Result<(usize, usize), (usize, usize)> {
    let mut res = Vec::new();

    let p = |vec: Vec<(u32, u32, u16, usize, usize)>| {
        vec.into_iter().min_by_key(|&(o, v, k, _r, _c)| (o >= v, v, k))
    };
    let f = |cells, r, c| {
        let cover_set = cover(field, &cells);
        let keys: Vec<_> = cover_set.keys()
                                    .map(|k| (k.count_ones(), cover_set[k] as u32, *k, r, c))
                                    .collect();

        // find a key for which there are more entries than the size of the cover set
        // otherwise, stick to just a key with the smallest number of contributors
        p(keys).unwrap_or((0, 1, 0, r, c))
    };

    for row in 0..9 {
        res.push(f(cols(row, 0), row, 0));
    }

    for col in 0..9 {
        res.push(f(rows(0, col), 0, col));
    }

    for r in 0..3 {
        let r = r * 3;
        for c in 0..3 {
            let c = c * 3;
            res.push(f(cell(r, c), r + 1, c + 1));
        }
    }

    let (o, v, _k, r, c) = p(res).unwrap_or((0, 1, 0, 0, 0));
    if o < v {
        return Err((r, c));
    }

    Ok((r, c))
}

fn deduce_backtrack(changes: Vec<(usize, usize)>, field: &mut Vec<u16>) -> Option<(usize, usize)> {
    let mut changes = changes;

    while changes.len() > 0 {
        //print_field(&changes, &field);
        changes = mark(&changes, field);
    }

    let v = validate(field);
    if v.is_none() {
        return None;
    }
    
    let (r, c) = match best_cover(field) {
        Ok(rc) => rc,
        Err(rc) => return Some(rc)
    };
    let cells = if r == 0 { rows(r, c) } else if c == 0 { cols(r, c) } else { cell(r, c) };
    let (r, c) = cells.into_iter().min_by_key(|&(r, c)| {
            let ones = field[r * 9 + c].count_ones();
            if ones == 1 { 10 } else { ones }
        }).unwrap();

    let v = field[r * 9 + c];
    let old_field = field.clone();
    for i in 0..9 {
        if v & (1 << i) == 0 {
            continue;
        }

        field[r * 9 + c] = 1 << i;
        let changes = vec!((r, c));
        let res = deduce_backtrack(changes, field);

        if res.is_none() {
            return None;
        }

        field.copy_from_slice(&old_field);
    }

    Some((r, c))
}

fn solve(name: &str, task: Vec<&str>) -> Vec<String> {
    println!("solving {}", name);
    let mut field = vec! [0x1ffu16; 81];
    let mut changes = Vec::new();

    for (row, &it) in task.iter().enumerate() {
        for (col, ch) in it.chars().enumerate() {
            let d = ch.to_digit(10).expect("wanted a decimal digit");
            if d == 0 {
                continue;
            }

            field[row * 9 + col] = 1 << (d-1);
            changes.push((row, col));
        }
    }

    let v = deduce_backtrack(changes, &mut field);
    if let Some((row, col)) = v {
        if row == 9 {
            println!("bad solution: column {} is broken", col);
        } else if col == 9 {
            println!("bad solution: row {} is broken", row);
        } else {
            println!("bad solution: cell ({}, {})..({}, {}) is broken", row, col, row+2, col+2);
        }
    }

    let mut res = Vec::new();
    for (i, &v) in field.iter().enumerate() {
        let row = i / 9;
        let col = i % 9;
        let v = if v.count_ones() > 1 {
            0
        } else {
            v.trailing_zeros() + 1
        };

        if col == 0 && (row == 3 || row == 6) {
            res.push(String::from("---+---+---"));
        }

        let last_row = res.len().wrapping_sub(1);
        if col == 3 || col == 6 {
            res[last_row].push('|');
        }

        let ch = char::from_digit(v, 16).unwrap(); // radix 16, to capture fault types
        if col == 0 {
            res.push(String::from(ch));
        } else {
            res[last_row].push(ch);
        }
    }

    res
}

fn main() -> io::Result<()> {
    let f = env::args().nth(1)
        .ok_or_else(|| io::Error::new(io::ErrorKind::Other, "oops, pass a file name"))?;

    let f = fs::read_to_string(f)?;

    let mut v = Vec::new();
    let mut sum = 0;

    for (i, ln) in f.lines().enumerate() {
        v.push(ln);

        if i % 10 == 9 {
            let name = v.remove(0);
            let r = solve(name, v);
            
            println!("{}", name);
            for ln in &r {
                println!("{}", ln);
            }

            sum += r[0][0..3].parse::<u32>().expect("Not a number");

            v = Vec::new();
        }
    }

    println!("{}", sum);

    Ok(())
}
