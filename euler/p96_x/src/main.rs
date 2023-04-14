// practice Algorithm X
use std::collections::HashMap;
use std::env;
use std::fs;
use std::io;

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

struct Cell {
    data:     isize, // column head: count of ones; other cells: what choice this row corresponds to
    prev_col: usize,
    next_col: usize,
    prev_row: usize,
    next_row: usize
}

// creates a matrix of choices and constraints, with special layout to simplify lookup of choices:
// the first 9x9x9 cells are heads of rows of choices.
fn init_cells() -> Vec<Cell> {
    let mut choices = Vec::new();

    // insert constraints that each cell can have only one number
    // ...inserting cells first
    for r in 0..9 {
        for c in 0..9 {
            for d in 0..9 {
                let id: usize = d + 9 * (c + 9 * r);
                let next_row = if d == 8 { id - 8 } else { id + 1 };
                let prev_row = if d == 0 { id + 8 } else { id - 1 };

                choices.push(Cell{data: id as isize, prev_col: id, next_col: id, prev_row: prev_row, next_row: next_row});
            }
        }
    }

    // insert a cell pointing to the head of columns
    let col_head = choices.len();
    append_node(&mut choices, 0, col_head, col_head);

    // ...inserting constraints now
    for r in 0..9 {
        for c in 0..9 {
            append_node(&mut choices, -10, col_head, 9 * (c + 9 * r));
        }
    }

    // insert constraints that each row can have only 1 digit each
    for r in 0..9 {
        for d in 0..9 {
            let constraint_head = choices.len();
            append_node(&mut choices, -10, col_head, constraint_head);

            for c in 0..9 {
                let id: usize = d + 9 * (c + 9 * r);
                append_node(&mut choices, id as isize, id, constraint_head);
            }
        }
    }

    // insert constraints that each column can have only 1 digit each
    for c in 0..9 {
        for d in 0..9 {
            let constraint_head = choices.len();
            append_node(&mut choices, -10, col_head, constraint_head);

            for r in 0..9 {
                let id: usize = d + 9 * (c + 9 * r);
                append_node(&mut choices, id as isize, id, constraint_head);
            }
        }
    }

    // insert constraints that each square can have only 1 digit each
    for cell in 0..9 {
        let core_r = cell / 3;
        let core_c = cell % 3;

        for d in 0..9 {
            let constraint_head = choices.len();
            append_node(&mut choices, -10, col_head, constraint_head);

            for r in core_r..core_r + 3 {
                for c in core_c..core_c + 3 {
                    let id: usize = d + 9 * (c + 9 * r);
                    append_node(&mut choices, id as isize, id, constraint_head);
                }
            }
        }
    }

    choices
}

fn append_node(cells: &mut Vec<Cell>, data: isize, row_head: usize, col_head: usize) {
    let id = cells.len();
    cells.push(Cell{data, prev_col: id, next_col: row_head, prev_row: id, next_row: col_head});

    let i = cells[row_head].prev_col;
    cells[i].next_col = id;
    cells[id].prev_col = cells[row_head].prev_col;
    cells[row_head].prev_col = id;

    let i = cells[col_head].prev_row;
    cells[i].next_row = id;
    cells[id].prev_row = cells[col_head].prev_row;
    cells[col_head].prev_row = id;
}

fn del_col(puzzle: &mut Vec<Cell>, col_head: usize) {
    let mut r = col_head;
    loop {
        let i = puzzle[r].prev_col;
        puzzle[i].next_col = puzzle[r].next_col;
        let i = puzzle[r].next_col;
        puzzle[i].prev_col = puzzle[r].prev_col;

        r = puzzle[r].next_row;

        if r == col_head {
            break;
        }
    }
}

fn restore_col(puzzle: &mut Vec<Cell>, col_head: usize) {
    let mut r = col_head;
    loop {
        let i = puzzle[r].prev_col;
        puzzle[i].next_col = r;
        let i = puzzle[r].next_col;
        puzzle[i].prev_col = r;

        r = puzzle[r].next_row;

        if r == col_head {
            break;
        }
    }
}

// remove all columns - i.e. remove all constraints that this choice satisfies;
// then also remove all rows that would have satisfied the same constraints.
// Keep the columns only detached, so they can be restored.
fn choose(puzzle: &mut Vec<Cell>, cell: usize) {
    let mut c = cell;
    loop {
        let mut r = puzzle[c].next_row;
        while r != c {
            if puzzle[r].data < 0 { // it's a column header - delete column
                let i = puzzle[r].next_col;
                puzzle[i].prev_col = puzzle[r].prev_col;

                let i = puzzle[r].prev_col;
                puzzle[i].next_col = puzzle[r].next_col;
            } else { // it's a row - delete the row
                let mut k = puzzle[r].next_col;
                while k != r {
                    let i = puzzle[k].next_row;
                    puzzle[i].prev_row = puzzle[k].prev_row;

                    let i = puzzle[k].prev_row;
                    puzzle[i].next_row = puzzle[k].next_row;

                    // update column counter, too
                    let mut i = i;
                    while puzzle[i].data >= 0 {
                        i = puzzle[i].prev_row;
                    }
                    puzzle[i].data += 1;

                    k = puzzle[k].next_col;
                }
            }

            r = puzzle[r].next_row;
        }

        c = puzzle[c].next_col;
        if c == cell {
            break;
        }
    }
}

// do the reverse of choose: restore the links in the reverse order
fn restore(puzzle: &mut Vec<Cell>, cell: usize) {
    let mut c = cell;
    loop {
        let mut r = puzzle[c].prev_row;
        while r != c {
            if puzzle[r].data < 0 {
                let i = puzzle[r].prev_col;
                puzzle[i].next_col = r;

                let i = puzzle[r].next_col;
                puzzle[i].prev_col = r;
            } else {
                let mut k = puzzle[r].prev_col;
                while k != r {
                    let i = puzzle[k].next_row;
                    puzzle[i].prev_row = k;

                    let i = puzzle[k].prev_row;
                    puzzle[i].next_row = k;

                    let mut i = i;
                    while puzzle[i].data >= 0 {
                        i = puzzle[i].prev_row;
                    }

                    puzzle[i].data -= 1;

                    k = puzzle[k].prev_col;
                }
            }
        }

        c = puzzle[c].prev_col;
        if c == cell {
            break;
        }
    }
}

fn alg_x(puzzle: &mut Vec<Cell>, col_head: usize, choices: &mut Vec<usize>) -> Option<(usize, usize)> {
    if puzzle[col_head].next_col == col_head {
        return None;
    }

    let mut c = puzzle[col_head].next_col;
    let mut min_c = c;
    while c != col_head {
        if puzzle[c].data > puzzle[min_c].data {
            min_c = c;
        }

        c = puzzle[c].next_col;
    }

    let min_c = min_c;

    if puzzle[min_c].data == -1 { // ok, time to backtrack
        return Some((0, 0));
    }

    c = puzzle[min_c].next_row;

    while c != min_c {
        let i = puzzle[c].data as usize;
        choices.push(i);

        choose(puzzle, i as usize);

        let r = alg_x(puzzle, col_head, choices);
        if r.is_none() {
            return None;
        }

        restore(puzzle, choices.pop().unwrap());
        c = puzzle[min_c].next_row;
    }

    return Some((1, 1));
}

fn deduce_backtrack(field: &mut Vec<u32>) -> Option<(usize, usize)> {
    let mut puzzle = init_cells();

    let col_head = puzzle[puzzle[0].prev_row].prev_col;

    let mut choices = Vec::new();
    for (rc, &v) in field.iter().enumerate() {
        if v == 0 {
            continue;
        }

        let d = v - 1;
        let i = rc * 9 + (d as usize);

        choices.push(i);
        choose(&mut puzzle, i);
    }

    let r = alg_x(&mut puzzle, col_head, &mut choices);
    if let Some(rc) = r {
        return r;
    }

    for i in choices {
        let (rc, d) = (i / 9, i % 9);
        field[rc] = (d + 1) as u32;
    }

    for (i, &v) in field.iter().enumerate() {
        if v == 0 {
            let (r, c) = (i / 9, i % 9);
            return Some((r, c));
        }
    }

    None
}

fn solve(name: &str, task: Vec<&str>) -> Vec<String> {
    println!("solving {}", name);
    let mut field = vec! [0; 81];

    for (row, &it) in task.iter().enumerate() {
        for (col, ch) in it.chars().enumerate() {
            let d = ch.to_digit(10).expect("wanted a decimal digit");
            field[row * 9 + col] = d;
        }
    }

    let v = deduce_backtrack(&mut field);
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
