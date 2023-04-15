// practice Algorithm X
use std::env;
use std::fs;
use std::io;

struct Cell {
    data:     isize, // column head: count of ones; other cells: what choice this row corresponds to
    prev_col: usize,
    next_col: usize,
    prev_row: usize,
    next_row: usize
}

// creates a matrix of choices and constraints, with special layout to simplify lookup of choices:
// the first 9x9x9 cells are heads of rows of choices.
fn init_cells(cell_rows: usize, cell_cols: usize) -> Vec<Cell> {
    // because we have to have cell_w * cell_h digits in any column, cell_w * cell_cols == cell_rows * cell_h == cell_w * cell_h
    let cell_w = cell_rows;
    let cell_h = cell_cols;

    let rows = cell_rows * cell_h;
    let cols = cell_cols * cell_w;
    let digits = cell_h * cell_w;
    let c_head = -(digits as isize) - 1;

    let mut choices = Vec::new();

    // insert constraints that each cell can have only one number
    // ...inserting cells first
    for r in 0..rows {
        for c in 0..cols {
            for d in 0..digits {
                let id: usize = d + digits * (c + cols * r);
                let next_row = if d == (digits - 1) { id + 1 - digits } else { id + 1 };
                let prev_row = if d == 0 { id + digits - 1 } else { id - 1 };

                choices.push(Cell{data: id as isize, prev_col: id, next_col: id, prev_row: prev_row, next_row: next_row});
            }
        }
    }

    // insert a cell pointing to the head of columns
    let col_head = choices.len();
    append_node(&mut choices, 0, col_head, col_head);

    // ...inserting constraints now
    for r in 0..rows {
        for c in 0..cols {
            append_node(&mut choices, c_head, col_head, digits * (c + cols * r));
        }
    }

    // insert constraints that each row can have only 1 digit each
    for r in 0..rows {
        for d in 0..digits {
            let constraint_head = choices.len();
            append_node(&mut choices, c_head, col_head, constraint_head);

            for c in 0..cols {
                let id: usize = d + digits * (c + cols * r);
                append_node(&mut choices, id as isize, id, constraint_head);
            }
        }
    }

    // insert constraints that each column can have only 1 digit each
    for c in 0..cols {
        for d in 0..digits {
            let constraint_head = choices.len();
            append_node(&mut choices, c_head, col_head, constraint_head);

            for r in 0..rows {
                let id: usize = d + digits * (c + cols * r);
                append_node(&mut choices, id as isize, id, constraint_head);
            }
        }
    }

    // insert constraints that each square can have only 1 digit each
    for core_r in (0..rows).step_by(cell_h) {
        for core_c in (0..cols).step_by(cell_w) {
            for d in 0..digits {
                let constraint_head = choices.len();
                append_node(&mut choices, c_head, col_head, constraint_head);

                for r in core_r..core_r + cell_h {
                    for c in core_c..core_c + cell_w {
                        let id: usize = d + digits * (c + cols * r);
                        append_node(&mut choices, id as isize, id, constraint_head);
                    }
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
                        assert!(i != k, "oops, somehow wrapped around and hit the bottom of the list");
                    }
                    puzzle[i].data += 1;
                    assert!(puzzle[i].data < 0, "oops, overflow occurred: {} at {}, {}, {}, {}, {}", puzzle[i].data, cell, c, r, k, i);

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
        c = puzzle[c].prev_col;

        let mut r = puzzle[c].prev_row;
        while r != c {
            if puzzle[r].data < 0 {
                let i = puzzle[r].prev_col;
                assert!(puzzle[i].next_col == puzzle[r].next_col, "oops, restoring incorrect next_col pointer");
                puzzle[i].next_col = r;

                let i = puzzle[r].next_col;
                assert!(puzzle[i].prev_col == puzzle[r].prev_col, "oops, restoring incorrect prev_col pointer");
                puzzle[i].prev_col = r;
            } else {
                let mut k = puzzle[r].prev_col;
                while k != r {
                    let i = puzzle[k].next_row;
                    assert!(puzzle[i].prev_row == puzzle[k].prev_row, "oops, restoring incorrect prev_row pointer");
                    puzzle[i].prev_row = k;

                    let i = puzzle[k].prev_row;
                    assert!(puzzle[i].next_row == puzzle[k].next_row, "oops, restoring incorrect next_row pointer");
                    puzzle[i].next_row = k;

                    let mut i = i;
                    while puzzle[i].data >= 0 {
                        i = puzzle[i].prev_row;
                        assert!(i != k, "oops, somehow wrapped around and hit the bottom of the list");
                    }

                    puzzle[i].data -= 1;
                    assert!(puzzle[i].data >= -10, "oops, somehow went over more than 9 choices");

                    k = puzzle[k].prev_col;
                }
            }

            r = puzzle[r].prev_row;
        }

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

        choose(puzzle, i);

        let r = alg_x(puzzle, col_head, choices);
        if r.is_none() {
            return None;
        }

        restore(puzzle, choices.pop().unwrap());
        c = puzzle[c].next_row;
    }

    return Some((1, 1));
}

fn validate(puzzle: &Vec<Cell>, col_head: usize) {
    let mut c = puzzle[col_head].next_col;
    let mut cols = 0;
    while c != col_head {
        assert!(puzzle[c].data == -10, "oops, col {} got {}", cols, puzzle[c].data);

        let mut r = puzzle[c].next_row;
        let mut rows = 0;
        while r != c {
            assert!(puzzle[r].data >= 0, "oops, col {}, row {} got {}", cols, rows, puzzle[r].data);
            rows+=1;
            r = puzzle[r].next_row;
        }

        assert!(rows == 9, "oops, col {} got {} rows, not 9", cols, rows);

        cols+=1;

        c = puzzle[c].next_col;
    }
    assert!(cols == 324, "oops, got {} cols, not 9", cols);
}

fn deduce_backtrack(field: &mut Vec<u32>) -> Option<(usize, usize)> {
    let mut puzzle = init_cells(3, 3);

    let col_head = puzzle[puzzle[0].prev_row].prev_col;

    validate(&puzzle, col_head);

    let mut choices = Vec::new();
    for (rc, &v) in field.iter().enumerate() {
        if v == 0 {
            continue;
        }

        let d = v - 1;
        let i = rc * 9 + (d as usize);

        choices.push(i);
        //println!("got {} ({}, {}) = {}", rc, rc / 9, rc % 9, d);
        choose(&mut puzzle, i);
    }

    let r = alg_x(&mut puzzle, col_head, &mut choices);
    if let Some(_) = r {
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

#[cfg(test)]
mod tests {
    use super::*;

    struct BitMx {
        mx: Vec<Vec<u128>>,
        cols: Vec<u128>
    }

    impl BitMx {
        fn mx_append(&mut self, row: usize, col: usize) {
            let (r, c) = (col / 128, col % 128);

            while self.cols.len() <= r {
                self.cols.push(0);
            }
            self.cols[r] |= 1 << c;

            while self.mx.len() <= row {
                self.mx.push(Vec::new());
            }

            while self.mx[row].len() <= r {
                self.mx[row].push(0);
            }

            self.mx[row][r] |= 1 << c;
        }

        fn new(cell_rows: usize, cell_cols: usize) -> Self {
            let mut bit_mx = Self{ mx: Vec::new(), cols: Vec::new() };
            let mut col = 0;

            let cell_w = cell_cols;
            let cell_h = cell_rows;
            let digits = cell_w * cell_h;

            let rows = cell_h * cell_rows;
            let cols = cell_cols * cell_w;

            for r in 0..rows {
                for c in 0..cols {
                    for d in 0..digits {
                        let i = d + digits * (c + cols * r);
                        bit_mx.mx_append(i, col);
                    }
                    col += 1;
                }
            }

            for r in 0..rows {
                for d in 0..digits {
                    for c in 0..cols {
                        let i = d + digits * (c + cols * r);
                        bit_mx.mx_append(i, col);
                    }
                    col += 1;
                }
            }

            for c in 0..cols {
                for d in 0..digits {
                    for r in 0..rows {
                        let i = d + digits * (c + cols * r);
                        bit_mx.mx_append(i, col);
                    }
                    col += 1;
                }
            }

            for core_r in (0..rows).step_by(cell_h) {
                for core_c in (0..cols).step_by(cell_w) {
                    for d in 0..digits {
                        for r in core_r..core_r + cell_h {
                            for c in core_c..core_c + cell_w {
                                let i = d + digits * (c + cols * r);
                                bit_mx.mx_append(i, col);
                            }
                        }
                        col += 1;
                    }
                }
            }

            bit_mx
        }
    }

    #[test]
    fn init_works() {
        init_cells(3, 3);
    }
}
