**Created:** `2026-11-25`
**Linked:** `—`
**Status:** `draft`
**Related-epic:** `—`
**Related-branch:** `—`

# Bitemporal import of one classification vintage

## 1. Context and motivation

Each classification seed keeps two clocks. Validity time says when a row is true in the budget world. Record time says when the seed held that row as known. An open row ends at the sentinel `9999-12-31`. Record time is that calendar day at midnight, as the seeds already write it.

A new vintage, such as the 2004 union revenue list, arrives as a file of codes and names. The seed already holds an earlier vintage, such as the 2002 series. Loading the new file by replacement would erase the earlier vintage. The seed of hierarchical levels already shows the other outcome: the open row is closed in record time, a copy keeps the old attributes with a shortened validity, and the new vintage is appended.

The 2004 file uses fewer columns, and different headers, than the item seed. The current item seed and the 2002 rewrite also use codes of different lengths for the same economic idea. The protocol has to say which columns it reads, which row is the same item, and which dates come from the vintage rather than from the file.

---

## 2. Vision and purpose

One vintage can be applied to the seed of one named table. The seed keeps every earlier vintage. The row that remains open in record time is the one the vintage declares as current. A later load of the database reads that seed; this protocol does not perform that load.

---

## 3. Objectives

- A declared column contract for each table the protocol accepts.
- A vintage named by a validity start, a validity end, a record start, and a record end.
- One comparison, against the open row of the same key, using only the columns the contract reads.
- A closed record, a shortened validity, and a new open row when a compared column changes.
- The open row left as it is when every compared column is equal.
- A refusal when the vintage would invert a period or when the file breaks the contract.

---

## 4. Conceptual scope

### In scope

- The seed of the table named in the invocation.
- One input file for one vintage of that table.
- The four vintage dates, and the sentinel when an end date is omitted.
- Rows whose record end is the sentinel. Already closed rows stay untouched.

### Out of scope

- Loading the seed into the database.
- Creating, editing, or closing a row through the admin.
- Rewriting a vintage that is already closed in record time.
- Inventing a code, a parent, or an identifier the file does not bring and the contract does not derive.
- Tables that have no column contract.

---

## 5. High-level requirements

### The invocation

The protocol receives the path of the file and the name of the destination table. It may also receive a validity start, a validity end, a record start, and a record end:

```text
python import.py .import/receita-2024.csv ItemClassificacao --valid-init 2004-01-01 --valid-end 9999-12-31 --system-init 2004-01-01 --system-end 9999-12-31
```

Validity start and record start are independent. In the level seed, the 2018 change is recorded on `2017-12-31` and becomes valid on `2018-01-01`. The day before the validity start is `2017-12-31`. That day is not computed from the record start.

An omitted validity end, or an omitted record end, is the sentinel `9999-12-31`. An omitted validity start, or an omitted record start, refuses the run. There is then no day at which the open row can be closed.

### The column contract

Each accepted table declares three lists.

- The key columns identify the same item from one vintage to the next.
- The read columns are the only columns taken from the file. Any other column in the file is ignored. The four date columns are never read from the file.
- The required columns must be present in the file. A missing required column refuses that row.

A destination column that is not in the read list and is not required is `NULL` only when the key is new. When the key already exists, that column is copied from the open row. A file that simply does not mention a description must not wipe the description already stored.

The comparison uses the read columns, against the single open row of that key. The open row is the one whose record end is the sentinel.

### When a compared column changes

Take an open item whose validity is `2002-01-01` → `9999-12-31` and whose record is `2002-01-01` → `9999-12-31`. The vintage is validity `2004-01-01` → `9999-12-31` and record `2004-01-01` → `9999-12-31`. One compared column differs.

The seed then holds three rows for that key.

| Row | What it is                                                                                                            | Validity                    | Record                      |
| --- | --------------------------------------------------------------------------------------------------------------------- | --------------------------- | --------------------------- |
| 1   | The former open row. Only the record end changes. Attributes and validity stay.                                       | `2002-01-01` → `9999-12-31` | `2002-01-01` → `2004-01-01` |
| 2   | A copy of the old attributes. Validity start stays. Validity end is the day before the validity start of the vintage. | `2002-01-01` → `2003-12-31` | `2004-01-01` → `9999-12-31` |
| 3   | The imported row.                                                                                                     | `2004-01-01` → `9999-12-31` | `2004-01-01` → `9999-12-31` |

Row 1 is what the seed believed until the new record. Row 2 is the same belief, now known to have ended the day before the new validity. Row 3 is the vintage.

This is the shape of `NIVEL-1` in the level seed. There the record start of the change is `2017-12-31`, the new validity starts on `2018-01-01`, and the shortened row ends on `2017-12-31`.

### When nothing compared has changed

The open row remains the valid row. The protocol writes no copy and no new row.

### When the key is new

The protocol writes one row. Validity and record are the vintage dates. A destination column that the file does not bring, and that is not required, is `NULL`.

### When the seed has a key the file does not

That open row stays as it is. Absence from the file is not a closure.

### A later vintage touches only the open row

`NIVEL-2` already has a closed pair for `2002-01-01` → `2009-12-31` and an open row for `2010-01-01`. A vintage whose validity starts on `2018-01-01` and whose record starts on `2017-12-31` leaves the 2002 pair untouched. It closes the record end of the 2010 open row, copies that 2010 row with validity end `2017-12-31`, and appends the 2018 row. The level seed shows that result.

### Refusals

The protocol refuses, and does not write, when:

- the validity start falls on or before the validity start of the open row
- the record start falls before the record start of the open row
- the same key has two rows whose record end is the sentinel
- a required column is missing from the file
- the table has no column contract

A refused row does not close its open neighbour.

### Quality

- Dates in the seed stay calendar days. Record time stays midnight of that day.
- The protocol reads a comma-separated file or a semicolon-separated file.
- The same vintage dates apply to every row of that run.
- A second run of a later vintage sees the rows the first run closed, and does not open them again.

---

## 6. Macrocomponents

### Column contract

Declares, for one table, the key, the columns read from the file, and the columns the file must bring. The item table and the level table each have their own contract. A table without a contract is outside the protocol.

### Vintage

The four dates of one run, with the sentinel standing in for an omitted end. The file does not override them.

### Open-row comparison

Finds the one sentinel-ended row of the key and compares the read columns. Equal columns leave that row. A difference produces the three-row shape. No open row produces one new row.

---

## 7. Assumptions and constraints

### Assumptions

- The destination of the protocol is the seed of the named table, as `seed_item_classificacao.csv` is the seed of the item table and `seed_nivel_hierarquico.csv` is the seed of the level table.
- The sentinel date is `9999-12-31`, and the sentinel record time is midnight of that day.
- The day before `2004-01-01` is `2003-12-31`.

### Constraints

- Already closed rows are not rewritten.
- Columns outside the read list are not taken from the file.
- An existing key keeps destination values the file does not mention.
- A new key receives `NULL` for a destination column the file does not mention and the contract does not require.
- Validity start and record start may be different days. The shortened validity end is the day before the validity start.

---

## 8. Success criteria

- A changed open item, with validity start `2004-01-01` and record start `2004-01-01`, yields the three rows in the table above, and the previous closed rows of that key stay byte for byte.
- An open item whose read columns all match the file is unchanged.
- A key present only in the file becomes one open row, with `NULL` in each non-required column the file omitted.
- A key present only in the seed stays open with its previous dates and attributes.
- A second vintage, applied to a seed that already contains a closed pair, changes only the current open row and appends the new vintage, as `NIVEL-2` does between 2010 and 2018.
- A validity start on or before the open validity start writes nothing for that key.
- A file column outside the read list never changes the seed.
- An omitted end date is stored as `9999-12-31`.

---

## 9. Open questions

- Which columns are the key of an item when one vintage writes an 8-digit code, another a 10-digit code, and the current seed a 14-digit code for the same economic place? `receita_cod` does not match across those lengths, and `item_id` in the 2002 rewrite is not the `item_id` in the current seed.
- The 2004 file headers are `rec_cod`, `rec_nome`, `rec_nome_normalized`, and `rec_especificacao`. The item seed headers are `receita_cod`, `receita_nome`, and `receita_descricao`. Does a header that is not the destination name refuse the file, or does the contract alias it?
- When the file does not bring `item_id`, `item_ref`, or `parent_item_id`, and the contract marks any of them required, every row is refused. May the contract derive any of those from the code, or must the file bring them?
- `rec_nome_normalized` has no column on the item seed. Is it ignored as a column outside the read list, or does a destination column still have to be chosen for it?

---

## 10. Worked cases

The destination in cases 1 to 6 is an item seed. The contract reads `receita_cod`, `receita_nome`, and `receita_descricao`. The key is `receita_cod`. Those three columns are required. Every other destination column is optional. The open row before the run is:

| receita_cod | receita_nome       | receita_descricao | data_vigencia_inicio | data_vigencia_fim | data_registro_inicio | data_registro_fim |
| ----------- | ------------------ | ----------------- | -------------------- | ----------------- | -------------------- | ----------------- |
| 10000000    | Receitas Correntes | Registra o total. | 2002-01-01           | 9999-12-31        | 2002-01-01           | 9999-12-31        |

Unless a case says otherwise, the vintage is `--valid-init 2004-01-01 --valid-end 9999-12-31 --system-init 2004-01-01 --system-end 9999-12-31`.

### Case 1 — one compared column changes

The file row is `10000000`, `Receitas Correntes`, `Novo texto.`

| Row             | receita_nome       | receita_descricao | Validity                    | Record                      |
| --------------- | ------------------ | ----------------- | --------------------------- | --------------------------- |
| Former open row | Receitas Correntes | Registra o total. | `2002-01-01` → `9999-12-31` | `2002-01-01` → `2004-01-01` |
| Shortened copy  | Receitas Correntes | Registra o total. | `2002-01-01` → `2003-12-31` | `2004-01-01` → `9999-12-31` |
| Vintage         | Receitas Correntes | Novo texto.       | `2004-01-01` → `9999-12-31` | `2004-01-01` → `9999-12-31` |

### Case 2 — every compared column matches

The file repeats `10000000`, `Receitas Correntes`, `Registra o total.` The open row stays the only row of that key. Dates stay `2002-01-01` → `9999-12-31` on both clocks.

### Case 3 — the key is new

The file brings `12000000` and `Receita de Contribuições`, with a description. `destinacao_legal` is optional and absent from the file. One row is written, validity and record as the vintage, and `destinacao_legal` is `NULL`.

### Case 4 — the seed has a key the file omits

The seed also has open `13000000`. The file has no `13000000`. That row stays open, with validity and record still ending at the sentinel.

### Case 5 — a later vintage leaves closed rows alone

After case 1, a further vintage uses validity start `2010-01-01` and record start `2009-12-31`, and changes the description again. The two rows whose record end is already `2004-01-01` or whose validity already ends on `2003-12-31` stay as case 1 wrote them. The open vintage row of case 1 is closed at record end `2009-12-31`, copied with validity end `2009-12-31`, and the 2010 row is appended. This is the passage from the 2010 pair to the 2018 row of `NIVEL-2`.

### Case 6 — record start and validity start differ

The vintage uses record start `2003-12-31` and validity start `2004-01-01`. The former open row receives record end `2003-12-31`. The copy ends validity on `2003-12-31` and opens its record on `2003-12-31`. The imported row is valid from `2004-01-01` and recorded from `2003-12-31`. This is the spacing of `NIVEL-1` between `2017-12-31` and `2018-01-01`.

### Case 7 — the validity start does not move forward

The open validity already starts on `2004-01-01`, and the vintage also starts on `2004-01-01`. The protocol writes nothing for that key.

### Case 8 — the record start moves backward

The open record starts on `2004-06-01`, and the vintage records from `2004-01-01`. The protocol writes nothing for that key.

### Case 9 — two open rows share a key

Two rows of `10000000` both end their record at the sentinel. The protocol writes nothing for that key.

### Case 10 — a required column is missing

The file has `receita_cod` and `receita_nome` and no `receita_descricao`. The row is refused. The open row stays open.

### Case 11 — the file brings a column outside the contract

The file includes `rec_nome_normalized`. The contract does not read it. The seed column set is unchanged by that field. Cases 1 to 4 still apply to the columns the contract does read.

### Case 12 — an end date is omitted

The invocation gives the two starts and omits both ends. Stored ends are `9999-12-31`.

### Case 13 — a start date is omitted

The invocation omits `--valid-init` or `--system-init`. The run is refused before any row is written.

### Case 14 — the file itself carries dates

A column `data_vigencia_inicio` in the file, if the contract does not read it, is ignored. The vintage flags are the dates that are stored.

---

## References

- `docs/assets/seed_nivel_hierarquico.csv` — the observed three-row change, and a second vintage that leaves the earlier pair closed.
- `docs/assets/seed_item_classificacao.csv` — the current item seed, with 14-digit codes.
- `docs/assets/seed_item_classificacao_2.xlsx` — the 2002 rewrite, with 10-digit codes and the same four date columns.
- `_dev/.archive/receitas-uniao_2004.csv` — a vintage file with four semicolon-separated columns and 8-digit codes.
