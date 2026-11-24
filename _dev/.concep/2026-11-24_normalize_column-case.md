**Created:** `2026-11-24`
**Linked:** `—`
**Status:** `draft`
**Related-epic:** `—`
**Related-branch:** `—`

# Title case for one text column

## 1. Context and motivation

Classification names and other labels in the classifier's CSV seeds arrive with uneven casing. A cell may be all lowercase, all uppercase, or a mixture, and a sigla inside it may not match the casing recorded for that abbreviation.

A person who prepares those files needs one reading of a chosen text column: Portuguese title case, with function words left lowercase, and with any span that is already an abbreviation kept in the casing of the abbreviation list. The source cell stays as it was. The reading appears beside it, in the same file, so the person can compare the two before anything else consumes the text.

The abbreviation list is `docs/assets/seed_lista_abreviacoes.csv`. The casing authority is the column `abreviacao`, not the expanded term in `termo_nome`.

---

## 2. Vision and purpose

A person can point at one CSV and one text column and receive, in that same file, a sibling column that states the title-case reading of every cell.

The reading is stable. The same cell, the same abbreviation list, and the same function-word class produce the same text. Ordinary words take a capital initial and a lowercase remainder. Function words that Portuguese title style leaves lowercase stay lowercase. A span that matches an abbreviation keeps that abbreviation's letters as the list records them, so `Rgps` becomes `RGPS` because the list records `RGPS`, and `RECEITA TRIBUTÁRIA` becomes `Receita Tributária`.

---

## 3. Objectives

- One title-case reading of a single named text column, written beside the source column in the same CSV.
- Function words of Portuguese title style remain entirely lowercase.
- A span that matches an abbreviation keeps the casing of that abbreviation, including a sigla whose source letters were in the wrong case.
- A request that names a missing column, or that meets a cell which is not text, stops and tells the person what failed. The file stays as it was.

---

## 4. Conceptual scope

### In scope

- One CSV file and one column per request. The column is named by the person.
- A new column immediately to the right of that column, named `<column>_normalized`.
- Title case of the source text, the Portuguese function-word class, and abbreviation casing from `abreviacao`.
- A refusal, with a message, when the named column is absent or a cell in it is not text.

### Out of scope

- More than one source column in the same request.
- A file that is not CSV.
- Replacing the source column with the reading.
- Expanding an abbreviation into `termo_nome`, or editing the abbreviation list.
- Loading the result into the database, or changing what a changelist displays.
- Choosing which rows of a seed are current for any purpose other than the casing of `abreviacao`.

---

## 5. High-level requirements

### Functional expectations

- The request carries a path to one CSV and the name of one column.
- The named column is present in the header, and every cell in it is text. An empty cell is text and yields an empty reading.
- The sibling column is inserted immediately to the right of the source column. Columns that already stood further right stay further right, after the new column.
- Each ordinary word in the reading begins with an uppercase letter. The rest of that word is lowercase. Accents stay.
- A function word is entirely lowercase. The class is the words Portuguese title style leaves lowercase: the articles `a`, `o`, `as`, `os`, `um`, `uma`, `uns`, `umas`; the conjunctions `e` and `ou`; the prepositions and contractions `de`, `da`, `do`, `das`, `dos`, `em`, `na`, `no`, `nas`, `nos`, `por`, `para`, `com`, `sem`, `sobre`, `ao`, `aos`, `à`, `às`, `pelo`, `pela`, `pelos`, `pelas`. The illustrative set `e`, `da`, `de`, `do`, `para`, `sobre`, `com` belongs to this class.
- An abbreviation span is a stretch of the source cell that equals an `abreviacao` value when case is ignored, on whole-word boundaries. Punctuation that belongs to the abbreviation, such as the period in `Adm.`, belongs to the span. Punctuation that merely sits beside the span does not.
- When two spans overlap, or one contains the other, the longer span is the one that counts.
- When several rows of the abbreviation list share the same `abreviacao` text, the casing is the casing of the first of those rows. `RGPS` occurs more than once, always as `RGPS`.
- Inside an abbreviation span, the reading copies the list's casing and does not apply title case or the function-word rule. Outside those spans, title case and the function-word rule apply.
- The source column is unchanged. The sibling column holds the reading. The file is written back only when every cell of the named column has been read as text.

Worked readings:

| Source                           | Reading                          |
| -------------------------------- | -------------------------------- |
| `receita tributária`             | `Receita Tributária`             |
| `RECEITA TRIBUTÁRIA`             | `Receita Tributária`             |
| `imposto de renda`               | `Imposto de Renda`               |
| `receita do regime próprio Rgps` | `Receita do Regime Próprio RGPS` |
| `assist. farmacêutica`           | `Assist. Farmacêutica`           |

### Quality and policy expectations

- The same source text and the same abbreviation list yield the same reading.
- A refusal names the missing column, or the cell that is not text, and leaves the file unchanged.
- The CSV remains a CSV with a header row. The person can open it and compare the source column with the sibling column.

---

## 6. Macrocomponents

### Request

The person's choice of one CSV and one column name. It bounds the run to that column and to that file.

### Title form

The reading of ordinary words and of function words. It applies only outside abbreviation spans.

### Abbreviation form

The casing taken from `abreviacao` for spans that already match an abbreviation. It does not expand the span into the full term. It overrides title form wherever a span was recognized.

### Refusal

The stop that protects the file when the column is missing or a cell is not text. It tells the person what failed.

---

## 7. Evolution stages

### Stage 1 — One column, one CSV, one sibling reading

A person obtains `<column>_normalized` immediately to the right of one text column, under the title-form and abbreviation-form rules above, or is told why the file was left unchanged.

Later stages are not part of this conception.

---

## 8. Assumptions and constraints

### Assumptions

- The target file has a header row, is comma-separated, and is UTF-8 text, in the same CSV shape as the classifier seeds. A file in another encoding, or without a header, falls outside this conception.
- Empty text is a legitimate cell and normalizes to empty text.
- The first row that carries a given `abreviacao` string is a sufficient casing source for every later row that repeats that string.

### Constraints

- One column per request.
- The sibling column is written in the same file, immediately to the right of the source.
- The abbreviation list is read, not rewritten.
- A missing column or a non-text cell ends the request with a message and without a write.

---

## 9. Success criteria

- `receita tributária` and `RECEITA TRIBUTÁRIA` both read `Receita Tributária`.
- `imposto de renda` reads `Imposto de Renda`, and `receita do regime próprio Rgps` reads `Receita do Regime Próprio RGPS`.
- A multi-word abbreviation such as `assist. farmacêutica` reads `Assist. Farmacêutica`, and a shorter abbreviation does not replace a longer one that covers the same stretch.
- After a successful request, the source column is intact, the sibling column sits immediately to its right, and the rest of the header follows the sibling.
- After a refused request, the file's bytes are unchanged and the message identifies the column or the cell.

---

## 10. Open questions

- When the first word of a cell is a function word, does the reading capitalize that word because it opens the cell, or leave it lowercase? `de renda` is the case in point.
- When the cell already has a column named `<column>_normalized`, does a later request replace that column, or refuse?
- Does an abbreviation row whose record end is not the sentinel still supply casing?
- In a hyphenated compound, is each side a separate word for title case?

---

## References

- `docs/assets/seed_lista_abreviacoes.csv` — column `abreviacao` is the casing authority. `RGPS` is recorded there, more than once, as `RGPS`.
- The function-word class used when a classification name is abbreviated is the same linguistic class this conception adopts for title case. The illustrative words in the request are a subset of that class.
