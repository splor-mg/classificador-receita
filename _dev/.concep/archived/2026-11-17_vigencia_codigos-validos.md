- Related-epic: `_dev/.epic/.epic-02_0-vigencia-assistente.md`
**Created:** `2026-11-17`
**Linked:** `2026-11-17`
**Status:** `used`
**Related-epic:** `_dev/.epic/.epic-02_0-vigencia-assistente.md`
**Related-branch:** `migracao`

# Validity window for classification codes

## 1. Context and motivation

The classifier keeps each code on two clocks. Validity time says when the code is true in the budget world. Record time says when the system held that row as known.

The changelists for series, classifications, hierarchical levels, and classification items can already narrow by record status, including rows whose record end is the sentinel. They do not offer one question that means "which codes cover this date, this period, this version, or the span between two versions, as known now or as known on a given day."

A person maintaining or reading the classifier has to reconstruct that window by hand. The same question is needed from the lists and from an inquiry that is not the list.

The examples in this conception use 2026 as the current year. The rule itself is "the current year," not a frozen calendar year.

---

## 2. Vision and purpose

A person can ask which codes are valid for a chosen window, and the series list, the classification list, the level list, and the item list can apply that same question.

The window is a date, a period, a registered version, or the span between two registered versions. Prefixed budget marks, LDO and LOA-PPAG, are dates, not rows of the version table. Record time stays on the sentinel unless the person, or one of those marks, names a day.

---

## 3. Objectives

- One meaning of "valid for this window," shared by the inquiry and by the four changelists.
- A search on each of those lists that states the assumed window before the filter runs.
- A refusal, with a message, when the request cannot be interpreted.
- An explicit notice when the product reorders a period so the earlier date comes first.

---

## 4. Conceptual scope

### In scope

- Series of classifications, classifications of revenue, hierarchical levels, and classification items.
- A validity window expressed as one date, a period, one registered version, or two registered versions.
- The prefixed marks LDO and LOA-PPAG.
- Record time as either the sentinel or an as-of day.
- The inquiry and the four lists using that same resolution.

### Out of scope

- Abbreviation lists, legal bases, classification variants, and the version list itself as targets of this search.
- Choosing which stored version row is "the" bridge from a version identity to a pair of dates. That bridge is still open.
- Replacing the existing record-status filter. This search is applied when the person runs it.
- Creating, editing, or closing a code.

---

## 5. High-level requirements

### Functional expectations

- The inquiry accepts dates or registered versions. A request that carries both is refused. LDO and LOA-PPAG are prefixed dates, so they travel with the year of the validity date and do not count as a registered version.
- One side of the validity date is a point. Two sides are a period. A period must be covered for its whole length: validity start on or before the first assumed date, and validity end on or after the second.
- An empty day becomes the last day of the selected month. An empty month becomes December of the selected year. An empty year becomes the current year. February without a day is 28, or 29 in a leap year.
- A day that does not exist in the stated month, such as 31 April, stops the search. The message names the day field.
- When both assumed dates exist and the left one is later, the product orders them from earlier to later, tells the person the order it applied, and then filters.
- Both the validity dates and the version slots empty means the window is 31 December of the current year, any version, and record end equal to the sentinel.
- An empty record date means record end equals the sentinel `31/12/9999`. A filled record date means record start on or before that day and record end on or after that day.
- LDO fixes month and day to 15 May of the assumed year, and fixes the record day to that same date, including when the record field was filled with another day. LOA-PPAG does the same with the date stated in the source note, 31 September of the assumed year.
- A registered version, or a span of two registered versions, selects codes whose validity is comprised in that version or in that span, with record end on the sentinel unless a record day was also supplied. The date fields stay unused.

### Quality and policy expectations

- The assumed window is visible: assumed validity, assumed version, and assumed record day.
- A reorder and a refusal are both told to the person. A reorder still runs the search. A refusal does not.
- The four lists and the inquiry do not answer the same inputs with two different windows.

### Worked cases

Each case states the filled controls, the window the product assumes, and the filter that follows. `2026` stands for the current year of the note. An empty version means any version. The sentinel record end is `31/12/9999`.

1. Everything empty. Empty validity and empty version become 31 December of the current year.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/12/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 31/12/2026` and validity end `>= 31/12/2026` and record end `= sentinel`

2. Month only.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/03/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 31/03/2026` and validity end `>= 31/03/2026` and record end `= sentinel`

3. Year only.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/12/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 31/12/2024` and validity end `>= 31/12/2024` and record end `= sentinel`

4. Year and month.

```
Vigência
Data Vigência                                                          |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/03/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 31/03/2024` and validity end `>= 31/03/2024` and record end `= sentinel`

5. Year, month, and day.

```
Vigência
Data Vigência                                                            |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ 03 ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `15/03/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 15/03/2024` and validity end `>= 15/03/2024` and record end `= sentinel`

6. Month and day, year empty.

```
Vigência
Data Vigência                                                            |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ 03 ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]     |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `15/03/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 15/03/2026` and validity end `>= 15/03/2026` and record end `= sentinel`

7. Day only. An empty month becomes December. An empty year becomes the current year.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `15/12/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 15/12/2026` and validity end `>= 15/12/2026` and record end `= sentinel`

8. Year and day, month empty.

```
Vigência
Data Vigência                                                          |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ ]  Dia: [ 15 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `15/12/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 15/12/2024` and validity end `>= 15/12/2024` and record end `= sentinel`

9. February without a day, non-leap year. The assumed day is the last day of the month.

```
Vigência
Data Vigência                                                          |  Versão           |  Data Registro
  Ano: [ 2026 ]  Mês: [ 02 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `28/02/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 28/02/2026` and validity end `>= 28/02/2026` and record end `= sentinel`

10. February without a day, leap year.

```
Vigência
Data Vigência                                                          |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ 02 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `29/02/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 29/02/2024` and validity end `>= 29/02/2024` and record end `= sentinel`

11. A day that does not exist in the stated month.

```
Vigência
Data Vigência                                                             |  Versão           |  Data Registro
  Ano: [ 2026 ]  Mês: [ 04 ]  Dia: [ 31 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: none (`31/04/2026` does not exist)
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: none. The search does not run while the day does not exist in the month. The message names the day field.

12. A period with both dates complete. The code covers the whole interval.

```
Vigência
Data Vigência                                                                              |  Versão           |  Data Registro
  Ano: [ 2024 ]  Mês: [ 01 ]  Dia: [ 01 ] .. Ano: [ 2024 ]  Mês: [ 06 ]  Dia: [ 30 ]       |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `01/01/2024` .. `30/06/2024`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 01/01/2024` and validity end `>= 30/06/2024` and record end `= sentinel`

13. A period with only the months, on both sides.

```
Vigência
Data Vigência                                                        |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ 01 ]  Dia: [ ] .. Ano: [ ]  Mês: [ 06 ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/01/2026` .. `30/06/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 31/01/2026` and validity end `>= 30/06/2026` and record end `= sentinel`

14. Only the right-hand date. One side remains a point, not a period.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ 06 ]  Dia: [ ]   |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `30/06/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Filter: validity start `<= 30/06/2026` and validity end `>= 30/06/2026` and record end `= sentinel`

15. An inverted period. The assumed date on the left falls after the one on the right. The product orders the dates from earlier to later and says that it did so.

```
Vigência
Data Vigência                                                                  |  Versão           |  Data Registro
  Ano: [ 2026 ]  Mês: [ 08 ]  Dia: [ ] .. Ano: [ 2026 ]  Mês: [ 03 ]  Dia: [ ] |    [ ] .. [ ]     |    [ ]
```

- Assumed validity: `31/03/2026` .. `31/08/2026`
- Assumed version: none (any version)
- Assumed record date: `31/12/9999` (sentinel)
- Notice: the stated period was reordered from `31/08/2026` .. `31/03/2026` to `31/03/2026` .. `31/08/2026`
- Filter: validity start `<= 31/03/2026` and validity end `>= 31/08/2026` and record end `= sentinel`

16. A point date and a filled record date. The record slice is what was known on that day, not the sentinel.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ ] .. [ ]     |    [ 15/05/2024 ]
```

- Assumed validity: `31/03/2026`
- Assumed version: none (any version)
- Assumed record date: `15/05/2024`
- Filter, as written in the source note: validity start `<= 31/03/2026` and validity end `>= 31/03/2026` and record start `<= 15/05/2025` and record end `>= 15/05/2024`. The year `2025` on the record start is unresolved; see open questions.

17. Record date only. Empty validity and empty version still become 31 December of the current year.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ ] .. [ ]     |    [ 15/05/2024 ]
```

- Assumed validity: `31/12/2026`
- Assumed version: none (any version)
- Assumed record date: `15/05/2024`
- Filter: validity start `<= 31/12/2026` and validity end `>= 31/12/2026` and record start `<= 15/05/2024` and record end `>= 15/05/2024`

18. One registered version. A registered version and a validity date do not combine, so the date stays unused.

```
Vigência
Data Vigência                                                       |  Versão                         |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ VERSAO-BRA-2018 ] .. [ ]   |    [ ]
```

- Assumed validity: unused
- Assumed version: `VERSAO-BRA-2018`
- Assumed record date: `31/12/9999` (sentinel)
- Filter: codes whose validity is comprised in `VERSAO-BRA-2018`, and record end `= sentinel`

19. Two registered versions.

```
Vigência
Data Vigência                                                       |  Versão                                              |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ VERSAO-BRA-ATE2017 ] .. [ VERSAO-BRA-2018 ]     |    [ ]
```

- Assumed validity: unused
- Assumed version: `VERSAO-BRA-ATE2017` .. `VERSAO-BRA-2018`
- Assumed record date: `31/12/9999` (sentinel)
- Filter: codes whose validity is comprised in the span from `VERSAO-BRA-ATE2017` through `VERSAO-BRA-2018`, and record end `= sentinel`

20. LDO, year empty. Month and day are fixed at 15 May. The record day is that same date.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]      |    [ LDO ] .. [ ] |    [ ]
```

- Assumed validity: `15/05/2026`
- Assumed version: `LDO`
- Assumed record date: `15/05/2026`
- Filter: validity start `<= 15/05/2026` and validity end `>= 15/05/2026` and record start `<= 15/05/2026` and record end `>= 15/05/2026`

21. LDO with year, month, and day filled. The stated month and day are overwritten.

```
Vigência
Data Vigência                                                             |  Versão           |  Data Registro
  Ano: [ 2025 ]  Mês: [ 03 ]  Dia: [ 01 ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LDO ] .. [ ] |    [ ]
```

- Assumed validity: `15/05/2025`
- Assumed version: `LDO`
- Assumed record date: `15/05/2025`
- Filter: validity start `<= 15/05/2025` and validity end `>= 15/05/2025` and record start `<= 15/05/2025` and record end `>= 15/05/2025`

22. LOA-PPAG with a year. The fixed date is the one in the rule, 31 September.

```
Vigência
Data Vigência                                                       |  Versão                |  Data Registro
  Ano: [ 2025 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LOA-PPAG ] .. [ ] |    [ ]
```

- Assumed validity: `31/09/2025`
- Assumed version: `LOA-PPAG`
- Assumed record date: `31/09/2025`
- Filter: validity start `<= 31/09/2025` and validity end `>= 31/09/2025` and record start `<= 31/09/2025` and record end `>= 31/09/2025`

23. LDO with a record date filled separately. The assumed record date remains 15 May of the year.

```
Vigência
Data Vigência                                                       |  Versão           |  Data Registro
  Ano: [ 2025 ]  Mês: [ ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ] |    [ LDO ] .. [ ] |    [ 01/01/2025 ]
```

- Assumed validity: `15/05/2025`
- Assumed version: `LDO`
- Assumed record date: `15/05/2025`
- Filter: validity start `<= 15/05/2025` and validity end `>= 15/05/2025` and record start `<= 15/05/2025` and record end `>= 15/05/2025`

24. A registered version and a validity date filled together.

```
Vigência
Data Vigência                                                       |  Versão                         |  Data Registro
  Ano: [ ]  Mês: [ 03 ]  Dia: [ ] .. Ano: [ ]  Mês: [ ]  Dia: [ ]   |    [ VERSAO-BRA-2018 ] .. [ ]   |    [ ]
```

- Assumed validity: unused
- Assumed version: unused
- Assumed record date: unused
- Filter: none. The search does not run when a validity date and a registered version are supplied together. The product reports the error.

---

## 6. Macrocomponents

### Window resolution

Turns a partial date, a period, a prefixed mark, or a registered version into the window the filter will use, including completion, refusal, and reorder.

### Record slice

Chooses the sentinel or an as-of day. Prefixed marks set that day even when the record field is empty or holds another day.

### Inquiry

Asks the same question without the list: dates or registered versions, and an optional as-of record day.

### List search

On each of the four changelists, a control named Vigência with validity date, version, and record date. A search action applies the resolution. The version control offers the registered active versions and, fixed at the top, LDO and LOA-PPAG.

---

## 7. Evolution stages

### Stage 1 — One window

The project can state, for a date, a period, a version, or a version span, which codes are valid and under which record slice. Refusals and reorders are part of that statement.

### Stage 2 — The four lists

Series, classifications, levels, and items can each run that statement from the Vigência search.

---

## 8. Assumptions and constraints

### Assumptions

- "Current year" in the examples is 2026 only because that was the year of the note. The behavior follows the year in which the person asks.
- "Active version" means a version row the product already treats as active. The precise predicate is the one the version list already uses.
- A period is covered only when the code's validity contains the whole interval. A code that overlaps the interval on some days and not others is outside the result.

### Constraints

- Date input and a registered version are mutually exclusive.
- LDO and LOA-PPAG overwrite month and day. They keep the year, or the current year when the year is empty.
- An impossible day does not become the last valid day of the month.
- The search does not invent a calendar date for 31 September.

---

## 9. Success criteria

- For each worked case in § 5, the assumed validity, the assumed version, the assumed record day, and the filter match that case.
- An impossible day produces no result list and a message on the day field.
- A reversed period produces a result list for the earlier-to-later window and a notice of the reorder.
- Date together with a registered version produces no result list and a message that the two were combined.
- The same inputs yield the same window from the inquiry and from each of the four lists.

---

## 10. Open questions

- Item 8 of the source note asks for one version dropdown. The layout and the examples ask for two slots, so a span between two registered versions can be expressed. Which of those is the control?
- What does "validity comprised in a version" use as the version's interval? The version row has its own validity and a launch date. Neither has been chosen as the bridge.
- LOA-PPAG is specified as 31 September. That day does not exist. Which calendar day should the mark use?
- Case 16 writes the record start against `15/05/2025` while the filled record day is `15/05/2024`. Is the `2025` a slip?

---

## References

- `_dev/toDo.md`, section "assistênte de vigência" — origin of the twenty-four cases now written in § 5. Exploratory. The conflicts in § 10 stay open.
