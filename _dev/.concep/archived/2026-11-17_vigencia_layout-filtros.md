- Status: used
**Created:** `2026-11-17`
**Linked:** `—`
**Status:** `draft`
**Related-epic:** `—`
**Related-branch:** `—`

# Validity filter bar on the changelist

## 1. Context and motivation

The changelist shows a section named **Vigência**. It holds Ano, Mês, Dia, Versão, Data Registro, and the button Pesquisar. Those controls are used together to filter the records on the list.

The screenshot of the current bar is the reference for that arrangement. What is wanted is a clearer presentation, a clearer organization, and an easier use of that same bar. The meaning of the filters stays as it is.

---

## 2. Vision and purpose

The bar should read as one filter component, not as a set of independent controls. Its appearance should be modern, clean, balanced, and professional, in the discreet manner of an institutional administrative system: light, without an excess of borders, colors, or decoration, and distinct from the rest of the page. Typography, color, borders, radii, and control states stay consistent with one another.

---

## 3. Objectives

- One coherent visual group, with the title **Vigência** kept as the name of that group.
- A logical and intuitive order of the controls.
- Labels that stay with their own controls, and do not look displaced or tied to a different field.
- A balanced use of the horizontal space, with field widths fitted to the content each control expects.
- A bar that remains organized and easy to use when the screen is smaller.

---

## 4. Conceptual scope

### In scope

- The visual and structural refinement of the **Vigência** filter bar on the changelist.
- The controls already on that bar: Ano, Mês, Dia, Versão, Data Registro, and Pesquisar.

### Out of scope

- Any change to what the filters do.
- Field names and identifiers.
- The GET parameters used to filter.
- The values the person selected, once a search has run.
- The behavior of Ano, Mês, Dia, Versão, and Data Registro.
- What Pesquisar does.
- The integration with the changelist filter.
- Compatibility with the templates and components that already exist.
- Models, queries, views, forms, and business rules. A change there belongs in this work only when it is indispensable for the visual presentation, and only after that necessity has been justified.

---

## 5. High-level requirements

### Functional expectations

- The filters continue to work exactly as they do now.
- Names, identifiers, GET parameters, selected values, control behavior, Pesquisar, and the changelist filter stay intact.

### Quality and policy expectations

- The controls form one coherent section. Their sequence is logical and intuitive. Each label belongs to its own control.
- Vertical alignment is consistent across the controls. Labels sit in a uniform place, preferably above their fields. Horizontal and vertical spacing is even: neither excessive nor compressed. The fields and Pesquisar share a harmonious height.
- Each field is as wide as its expected content, neither excessively wide nor excessively narrow. Pesquisar is proportional to the other controls. The bar uses the horizontal space that is available.
- The aesthetic is discreet, elegant, and functional. The group is visually distinct from the rest of the page. Typography, colors, borders, radii, and control states are consistent.
- On a smaller resolution the controls may move onto more than one line. They do not overlap, they are not cut off, and they do not force an unnecessary horizontal scrollbar. Organization and ease of use remain.
- The refinement reuses components and patterns the project already has. It does not add a dependency or a framework. Styling stays organized, simple, and maintainable, and it respects styles inherited from Django Admin and from any visual framework the project already uses, without leaving a custom style in conflict with those native styles. Inline style is avoided unless it is already an established pattern in the project.
- The result is one harmonious composition. Isolated alignment fixes are not enough.

---

## 6. Macrocomponents

### Validity filter bar

The bar is one visual component on the changelist. Its responsibility is to present **Vigência** and the controls Ano, Mês, Dia, Versão, Data Registro, and Pesquisar as a single group used together to filter the list. It does not own the meaning of the filter.

---

## 7. Assumptions and constraints

### Assumptions

- The bar already shows the controls named above, and those controls already filter the changelist together.
- Styles inherited from Django Admin, and from any visual framework the project already uses, are part of how the bar is drawn today.

### Constraints

- This work is a visual and structural refinement only.
- Filter processing stays as it is.
- No additional dependency or framework.
- Styling stays simple and maintainable, and prefers patterns the project already uses, including the choice to avoid inline style unless that is already the project pattern.
- Models, queries, views, forms, and business rules stay untouched unless a change is indispensable for the presentation. That necessity is justified before the change.

---

## 8. Success criteria

- Every control is visually aligned and organized.
- Each label is clearly tied to its own control.
- Widths and spacing look balanced, and Pesquisar is proportional to the other controls.
- The section has one uniform, professional visual identity, distinct from the rest of the page.
- The layout still works at different resolutions, including a reflow onto more than one line without overlap, clipping, or an unnecessary horizontal scrollbar.
- Every filter still works exactly as before, including names, identifiers, GET parameters, and the values selected after a search.
- The styling and the templates stay simple and easy to maintain.
- The controls read as one filter component.

---
