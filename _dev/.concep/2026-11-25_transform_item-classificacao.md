**Created:** `2026-11-25`
**Linked:** `—`
**Status:** `draft`
**Related-epic:** `—`
**Related-branch:** `—`

# Shape an item file to the classification schema

## 1. Context and motivation

An item vintage arrives as a table of codes and names. The item schema expects a fixed set of columns, in a fixed order, plus three values that are consequences of the code: the item identifier, the hierarchical level, and the parent item. Record time is not part of that preparation. It is written later, when the vintage is imported, together with `item_ref`, which depends on identifiers already stored in the database.

The level of a code is not a fixed slice of a 10-digit string. It is the deepest segment of the mask that belongs to the item's `classificacao_id`. The level seed records that mask in `estrutura_codigo` and `numero_digitos`. A 10-digit mask and a 13-digit mask cut the same idea in different places. A code whose length is not the width of its mask, such as an 8-digit code on the 10-digit mask, is not a code of that classification.

Column names in the files under preparation are the schema names. A header that is not a schema name is not accepted.

---

## 2. Vision and purpose

A person can point at one item file and receive that same file with the schema columns, in schema order, without the two record-time columns. `item_id`, `nivel_id`, and `parent_item_id` are filled from the code and from the open mask of `classificacao_id`. `item_ref` is left empty. A file that does not belong to its mask is left unchanged, and the failure is named.

---

## 3. Objectives

- One path, one item file, rewritten in place.
- The column set and the column order of `schemas/item_classificacao.yaml`, excluding `data_registro_inicio` and `data_registro_fim`.
- `item_id` equal to `IT-` followed by `receita_cod`.
- `nivel_id` taken from the open mask of the row's `classificacao_id`.
- `parent_item_id` equal to the `item_id` of the parent code in the same file, or the schema's missing mark when the level is 1.
- A refusal, with the file unchanged, when the code length, the mask, the parent, or the headers do not fit.

---

## 4. Conceptual scope

### In scope

- One item file per run.
- The open rows of the level seed: those whose record end is the sentinel `9999-12-31`.
- Deriving `item_id`, `nivel_id`, and `parent_item_id`.
- Creating a missing schema column, other than the two record-time columns, and leaving it empty when this protocol does not derive it.
- Reordering columns to the schema order.
- Removing the two record-time columns when the file already contains them.

### Out of scope

- Filling `item_ref`. That value is assigned at import, from identifiers already in the database.
- Filling validity dates, `matriz`, or `item_gerado` when the file does not already contain them.
- Choosing a mask by a date argument. The mask is the one selected by `classificacao_id`.
- Importing the vintage into the seed, or loading the seed into the database.
- Accepting a header that is not the schema name. `rec_cod`, `rec_nome`, and `rec_especificacao` are not columns of this protocol.

---

## 5. High-level requirements

### The file

The protocol receives the path of the file. It rewrites that file. It does not write a second copy.

`receita_cod` and `classificacao_id` are already present. Without them the run stops and the file stays as it was.

Every other schema column, except the two record-time columns, is created when it is absent. A value already in the file is kept. Empty created columns stay empty. `item_ref` is one of those empty columns when the file does not bring it.

A column whose name is not in the schema refuses the file. The two record-time columns are the exception that is removed rather than refused.

The resulting order is:

`item_id`, `item_ref`, `classificacao_id`, `receita_cod`, `matriz`, `receita_nome`, `receita_descricao`, `base_legal_tecnica_id`, `base_legal_tecnica_referencia`, `destinacao_legal`, `informacoes_gerenciais`, `nivel_id`, `parent_item_id`, `item_gerado`, `data_vigencia_inicio`, `data_vigencia_fim`.

### The item identifier

`item_id` is `IT-` followed by the digits of `receita_cod`. The code `1000000000` becomes `IT-1000000000`. The identifier uses the code as written. The protocol does not pad and does not trim.

### The mask

`classificacao_id` selects the mask from the open rows of the level seed.

The open rows whose `classificacao_id` equals the item's classification determine the digit width of `estrutura_codigo`. Every open level row with that same digit width joins the mask, including a level stored under a neighbouring classification that shares the width. In the level seed the 10-digit width joins the union levels 1 to 6 with the Minas Gerais level 7. The 13-digit width joins the 2018 union levels 1 to 7 with the Minas Gerais levels 8 and 9.

The levels of that width are ordered by `nivel_numero`. Each level contributes `numero_digitos` digits. The sum of those widths is the only length the code may have.

A code of another length is an error. An 8-digit code on the 10-digit mask is an error, even though eight digits cover the union levels 1 to 6. The mask's own width is 10.

Two open masks of different widths for the same `classificacao_id` are an error. Two open rows that assign different `numero_digitos` to the same `nivel_numero` inside one width are an error.

### The level

The code is cut from the left into the segments of the mask. The level is the last segment that is not all zeros. A 1-digit segment is zero when it is `0`. A 2-digit segment is zero when it is `00`. A 3-digit segment is zero when it is `000`.

On the 10-digit mask the segments are 1, 1, 1, 1, 2, 2, 2. The code `1110000000` is `1|1|1|0|00|00|00`, so the level is `NIVEL-3`. The code `1000000000` is `NIVEL-1`. The code `1110000015` is `NIVEL-7`.

On the 13-digit mask the segments are 1, 1, 1, 1, 2, 1, 1, 2, 3. The code `1112000000000` is `1|1|1|2|00|0|0|00|000`, so the level is `NIVEL-4`. The same ten digits that meant `NIVEL-3` on the old mask are not a code of this mask, because the length is 10 rather than 13.

A code whose every segment is zero has no level. That row is an error.

### The parent

The parent code keeps the digits of every segment before the item's level and replaces the remaining digits with zeros, out to the mask width.

On the 10-digit mask, the parent of a `NIVEL-3` code `1110000000` is `1100000000`. On the 13-digit mask, the parent of a `NIVEL-6` code keeps the first 6 digits and pads to 13. The old 10-digit parent slices are the special case of this rule, not a second rule.

`parent_item_id` is the `item_id` of the row in the same file whose `receita_cod` is that parent code.

A `NIVEL-1` item has no parent. `parent_item_id` is `-`, the schema's missing mark. It is not an item identifier, and it is not `--`.

When the parent code is not in the file, the row is an error. The protocol does not invent a parent.

When two rows share the same `receita_cod`, the parent cannot be chosen. The file is an error.

### Refusal

Any error refuses the whole run. The file stays as it was. The message names the row and the reason: unknown header, missing `receita_cod` or `classificacao_id`, code length, mask conflict, a zero code, a missing parent, or a duplicated code.

---

## 6. Macrocomponents

### Column frame

Makes the file carry the schema columns except record time, in schema order. It creates what is missing, keeps what is present, and rejects a foreign header.

### Mask

Resolves one digit width from `classificacao_id` and the open level rows, and cuts each code into that width's segments.

### Identity and parent

Writes `item_id` from the code, `nivel_id` from the last non-zero segment, and `parent_item_id` from the zero-padded parent code in the same file.

---

## 7. Assumptions and constraints

### Assumptions

- The level seed's open rows are the mask. Closed history in that seed is not a mask.
- A shared digit width means one mask, even when two classifications own different levels of that width.
- `-` remains the way a CSV writes a missing `parent_item_id`, matching the schema's missing values and the current item seed.
- `item_ref` stays empty until import.

### Constraints

- The protocol rewrites the given file or it writes nothing.
- It does not pad a short code out to the mask width.
- It does not derive `matriz`, `item_gerado`, or the validity dates.
- It does not read record time and does not write it.

---

## 8. Success criteria

- A 10-digit file whose `classificacao_id` selects the 10-digit mask gains `item_id`, `nivel_id`, and `parent_item_id` as in the worked cases, and its columns stand in schema order without the record-time pair.
- An 8-digit code on that mask leaves the file unchanged and names the length.
- A 13-digit code on the 2018 mask uses the 13-digit segments, not the 10-digit slices.
- A level-1 row stores `-` as `parent_item_id`.
- A missing parent, a duplicated code, an unknown header, or a missing `classificacao_id` leaves the file unchanged.
- `item_ref` is empty whenever the source file did not already contain it.

---

## 9. Open questions

- `matriz` and `item_gerado` are required by the schema and are not derived here. When the file does not bring them, the transformed file has those columns empty. Which later protocol fills them?
- The validity columns are created empty when the file does not bring them. The import protocol is the one that writes vintage dates. Is an empty validity column the intended hand-off, or must the file already carry those two dates before transformation?

---

## 10. Worked cases

The 10-digit mask has segment widths 1, 1, 1, 1, 2, 2, 2. The 13-digit mask has segment widths 1, 1, 1, 1, 2, 1, 1, 2, 3. Unless a case says otherwise, the file uses the 10-digit classification, and a parent row for the zero-padded prefix is present.

### Case 1 — a third-level code

`receita_cod` is `1110000000`.

| Column           | Value           |
| ---------------- | --------------- |
| `item_id`        | `IT-1110000000` |
| `nivel_id`       | `NIVEL-3`       |
| `parent_item_id` | `IT-1100000000` |

The parent code is `1100000000`.

### Case 2 — the first level

`receita_cod` is `1000000000`. `item_id` is `IT-1000000000`. `nivel_id` is `NIVEL-1`. `parent_item_id` is `-`.

### Case 3 — the seventh level on the 10-digit mask

`receita_cod` is `1110000015`. The last segment `15` is not `00`, so `nivel_id` is `NIVEL-7`. The parent code keeps the first 8 digits and pads two zeros: `1110000000`. `parent_item_id` is `IT-1110000000`.

### Case 4 — eight digits on the 10-digit mask

`receita_cod` is `11100000`. The mask width is 10. The run stops. The file is unchanged. This is the 2004 file as it stands: those codes have 8 digits and the mask they belong to has 10.

### Case 5 — the 2018 mask

`classificacao_id` selects the 13-digit mask. `receita_cod` is `1112000000000`, cut as `1|1|1|2|00|0|0|00|000`. `nivel_id` is `NIVEL-4`. The parent keeps the first 3 digits and pads to 13: `1110000000000`. `parent_item_id` is `IT-1110000000000`.

The code `1110000000` in this same file is an error. Its length is 10, and the mask width is 13.

### Case 6 — a sixth-level parent on the 2018 mask

`receita_cod` is `1112121000000`, cut as `1|1|1|2|12|1|0|00|000`. The last non-zero segment is the single `1` of the sixth level. `nivel_id` is `NIVEL-6`. The parent keeps the first 6 digits and pads to 13: `1112120000000`. The 10-digit habit of keeping 6 digits and padding 4 zeros does not apply.

### Case 7 — the parent row is absent

Case 1's file has `1110000000` and does not have `1100000000`. The run stops. The file is unchanged. `parent_item_id` is not `--`.

### Case 8 — headers

The file has `receita_nome` and lacks `receita_descricao` and `item_ref`. The protocol creates those two columns empty and orders every column as in the list above. A file that instead has `rec_cod` is refused. `rec_cod` is not a schema name.

A file that already contains `data_registro_inicio` loses that column. The protocol does not fill it.

### Case 9 — `item_ref` stays empty

The source has no `item_ref`. After a successful run the column exists and every cell is empty. Import assigns the number later.

### Case 10 — a mask conflict

The open level seed, for one `classificacao_id`, yields both a 10-digit width and a 13-digit width. The run stops before any code is cut. The file is unchanged.

### Case 11 — a duplicated code

Two rows have `receita_cod` `1100000000`. The parent of `1110000000` cannot be chosen. The run stops. The file is unchanged.

### Case 12 — a zero code

`receita_cod` is `0000000000` on the 10-digit mask. Every segment is zero. The run stops. The file is unchanged.

---

## References

- `schemas/item_classificacao.yaml` — column names, order, the `IT-` identifier, and `-` as a missing value.
- `docs/assets/seed_nivel_hierarquico.csv` — open masks. The 10-digit family is widths 1, 1, 1, 1, 2, 2, 2. The 13-digit family is widths 1, 1, 1, 1, 2, 1, 1, 2, 3.
- `docs/assets/seed_item_classificacao.csv` — level-1 parents stored as `-`, and `item_id` equal to `IT-` plus `receita_cod`.
- `_dev/.concep/2026-11-25_import_serie-bitemporal.md` — the later protocol that writes vintage dates and `item_ref`.
