// Atalhos de "Ano Corrente" para campos de vigência no Django Admin.
// Funciona para qualquer formulário que tenha os campos:
//   - data_vigencia_inicio
//   - data_vigencia_fim
// usando os widgets padrão de data do admin (vDateField).

(function () {
  function formatDateBR(day, month, year) {
    var dd = String(day).padStart(2, "0");
    var mm = String(month).padStart(2, "0");
    return dd + "/" + mm + "/" + year;
  }

  function findShortcutsSpan(input) {
    if (!input) {
      return null;
    }
    // Estrutura típica: <input> seguido de <span class="datetimeshortcuts">...</span>
    var sibling = input.nextElementSibling;
    while (sibling) {
      if (
        sibling.classList &&
        sibling.classList.contains("datetimeshortcuts")
      ) {
        return sibling;
      }
      sibling = sibling.nextElementSibling;
    }
    // Fallback: procurar dentro do mesmo container
    if (input.parentElement) {
      var fallback = input.parentElement.querySelector(".datetimeshortcuts");
      if (!fallback) {
        try {
          console.log(
            "[bitemporal-date-shortcuts] nenhum .datetimeshortcuts encontrado para",
            input.name || input.id
          );
        } catch (e) {}
      }
      return fallback;
    }
    return null;
  }

  function addCurrentYearShortcut(input, mode) {
    var shortcuts = findShortcutsSpan(input);
    if (!shortcuts) {
      try {
        console.log(
          "[bitemporal-date-shortcuts] abortando: sem shortcuts span para",
          input.name || input.id
        );
      } catch (e) {}
      return;
    }

    // Aumentar o recuo entre o campo e o bloco de atalhos.
    if (!shortcuts.style.marginLeft) {
      shortcuts.style.marginLeft = "0.5rem";
    }

    // Evitar adicionar duplicado
    if (shortcuts.querySelector(".date-current-year")) {
      try {
        console.log(
          "[bitemporal-date-shortcuts] já existe link Ano Corrente para",
          input.name || input.id
        );
      } catch (e) {}
      return;
    }

    var link = document.createElement("a");
    link.href = "#";
    link.className = "date-current-year";
    link.textContent = "Ano Corrente";
    // Remover sublinhado padrão e manter aparência discreta.
    link.style.textDecoration = "none";
    link.style.borderBottom = "none";
    link.style.cursor = "pointer";
    link.addEventListener("click", function (evt) {
      evt.preventDefault();
      var today = new Date();
      var year = today.getFullYear();
      var value;
      if (mode === "inicio") {
        value = formatDateBR(1, 1, year);
      } else {
        value = formatDateBR(31, 12, year);
      }
      input.value = value;
      var event = new Event("change", { bubbles: true });
      input.dispatchEvent(event);
    });

    // Inserir no início para obter ordem: (talvez "Indefinida | ") Ano Corrente | Hoje | calendário
    shortcuts.insertBefore(document.createTextNode(" | "), shortcuts.firstChild);
    shortcuts.insertBefore(link, shortcuts.firstChild);

    try {
      console.log(
        "[bitemporal-date-shortcuts] link Ano Corrente adicionado para",
        input.name || input.id
      );
    } catch (e) {}
  }

  function addIndefinidaShortcut(input) {
    var shortcuts = findShortcutsSpan(input);
    if (!shortcuts) {
      return;
    }

    // Evitar adicionar duplicado
    if (shortcuts.querySelector(".date-indefinida")) {
      return;
    }

    // Aumentar o recuo entre o campo e o bloco de atalhos.
    if (!shortcuts.style.marginLeft) {
      shortcuts.style.marginLeft = "0.5rem";
    }

    var link = document.createElement("a");
    link.href = "#";
    link.className = "date-indefinida";
    link.textContent = "Indefinida";
    link.style.textDecoration = "none";
    link.style.borderBottom = "none";
    link.style.cursor = "pointer";
    link.addEventListener("click", function (evt) {
      evt.preventDefault();
      // Valor sentinela alinhado com VALID_TIME_SENTINEL (9999-12-31)
      input.value = formatDateBR(31, 12, 9999);
      var event = new Event("change", { bubbles: true });
      input.dispatchEvent(event);
    });

    // Inserir no início para obter ordem: Indefinida | (Ano Corrente | ...) | Hoje | calendário
    shortcuts.insertBefore(document.createTextNode(" | "), shortcuts.firstChild);
    shortcuts.insertBefore(link, shortcuts.firstChild);

    try {
      console.log(
        "[bitemporal-date-shortcuts] link Indefinida adicionado para",
        input.name || input.id
      );
    } catch (e) {}
  }

  function enhanceChangeFormVigencia() {
    var body = document.body || document.getElementsByTagName("body")[0];
    if (!body || !body.classList.contains("change-form")) {
      return;
    }

    var inicio = document.querySelector(
      'input.vDateField[name$="data_vigencia_inicio"]'
    );
    var fim = document.querySelector(
      'input.vDateField[name$="data_vigencia_fim"]'
    );
    if (!inicio || !fim) {
      return;
    }

    [inicio, fim].forEach(function (input) {
      input.readOnly = true;
      input.classList.add("bitemporal-vigencia-readonly");
      try {
        input.style.backgroundColor = "#f5f5f5";
        input.style.cursor = "default";
      } catch (e) {}

      // Esconde atalhos padrão do Django admin ("Hoje" e ícone de calendário)
      var shortcuts = findShortcutsSpan(input);
      if (shortcuts) {
        shortcuts.style.display = "none";
      }
    });

    function createEditButton() {
      var btn = document.createElement("button");
      btn.type = "submit";
      btn.name = "_edit_vigencia";
      btn.value = "1";
      btn.className = "button bitemporal-edit-vigencia";
      btn.textContent = "✎";
      btn.title = "Editar intervalo de vigência (início e fim)";
      btn.style.marginLeft = "0.5rem";
      return btn;
    }

    [inicio, fim].forEach(function (input) {
      var wrapper = input.parentElement;
      if (!wrapper) {
        return;
      }

      // Evitar duplicar o botão caso o script rode mais de uma vez.
      if (wrapper.querySelector(".bitemporal-edit-vigencia")) {
        return;
      }

      // Garantir que o input e o botão fiquem lado a lado, com o botão
      // colado à borda direita do campo de data.
      if (!wrapper.style.display) {
        wrapper.style.display = "inline-flex";
        wrapper.style.alignItems = "center";
        wrapper.style.gap = "0.25rem";
      }

      var btn = createEditButton();

      // Ajustar altura para acompanhar o campo de data e evitar
      // que o ícone de lápis fique "achatado".
      var h = input.offsetHeight;
      if (h && h > 0) {
        btn.style.height = h + "px";
        btn.style.display = "inline-flex";
        btn.style.alignItems = "center";
        btn.style.justifyContent = "center";
        btn.style.padding = "0 6px";
        btn.style.fontSize = "14px";
        btn.style.lineHeight = "1";
      }

      input.insertAdjacentElement("afterend", btn);
    });
  }

  function enhanceConfirmVigenciaPreview() {
    // Campos de vigência na tela de confirmação (pré-visualização).
    var inputs = document.querySelectorAll(
      'input.vDateField[name^="edit_vig_inicio_"], input.vDateField[name^="edit_vig_fim_"]'
    );
    if (!inputs.length) {
      return;
    }

    // Para a tela de confirmação, sempre criamos nosso próprio container
    // de atalhos ao lado do input, independente de DateTimeShortcuts.
    function createShortcutsContainer(inp) {
      var parent = inp.parentElement;
      if (!parent) return null;
      var existing = parent.querySelector(".bitemporal-preview-shortcuts");
      if (existing) return existing;
      var span = document.createElement("span");
      span.className = "datetimeshortcuts bitemporal-preview-shortcuts";
      span.style.marginLeft = "0.5rem";
      parent.appendChild(span);
      return span;
    }
    function addShortcutLink(container, label, handler) {
      var link = document.createElement("a");
      link.href = "#";
      link.textContent = label;
      link.style.textDecoration = "none";
      link.style.borderBottom = "none";
      link.style.cursor = "pointer";
      link.addEventListener("click", function (evt) {
        evt.preventDefault();
        handler();
      });
      if (container.childNodes.length) {
        container.appendChild(document.createTextNode(" | "));
      }
      container.appendChild(link);
    }
    inputs.forEach(function (input) {
      var name = input.name || "";
      var container = createShortcutsContainer(input);
      if (!container) return;
      // Evitar duplicação: se já existem links (ex.: segunda chamada de enhance), não adicionar de novo.
      if (container.querySelector("a")) return;

      if (name.indexOf("edit_vig_fim_") === 0) {
        addShortcutLink(container, "Indefinida", function () {
          input.value = formatDateBR(31, 12, 9999);
          if (input.classList) input.classList.remove("invalid");
          try {
            input.dispatchEvent(new Event("change", { bubbles: true }));
          } catch (e) {}
        });
      }

      addShortcutLink(container, "Ano Corrente", function () {
        var today = new Date();
        var year = today.getFullYear();
        input.value =
          name.indexOf("edit_vig_inicio_") === 0
            ? formatDateBR(1, 1, year)
            : formatDateBR(31, 12, year);
        if (input.classList) input.classList.remove("invalid");
        try {
          input.dispatchEvent(new Event("change", { bubbles: true }));
        } catch (e) {}
      });

      addShortcutLink(container, "Hoje", function () {
        var d = new Date();
        input.value = formatDateBR(
          d.getDate(),
          d.getMonth() + 1,
          d.getFullYear()
        );
        if (input.classList) input.classList.remove("invalid");
        try {
          input.dispatchEvent(new Event("change", { bubbles: true }));
        } catch (e) {}
      });

      // Ícone de calendário: abre popup para escolher data
      if (container.childNodes.length) {
        container.appendChild(document.createTextNode(" | "));
      }
      var calLink = document.createElement("a");
      calLink.href = "#";
      calLink.title = "Abrir calendário";
      calLink.style.textDecoration = "none";
      calLink.style.borderBottom = "none";
      calLink.style.cursor = "pointer";
      calLink.style.display = "inline-block";
      calLink.style.verticalAlign = "middle";
      var calIcon = document.createElement("span");
      calIcon.className = "date-icon";
      calIcon.setAttribute("aria-label", "Calendário");
      calLink.appendChild(calIcon);
      calLink.addEventListener("click", function (evt) {
        evt.preventDefault();
        openConfirmCalendarPopup(input);
      });
      container.appendChild(calLink);
    });
  }

  function openConfirmCalendarPopup(input) {
    var overlay = document.createElement("div");
    overlay.className = "bitemporal-calendar-overlay";
    var box = document.createElement("div");
    box.className = "bitemporal-calendar-box";
    overlay.appendChild(box);

    var grid = document.createElement("div");
    grid.className = "bitemporal-calendar-grid";
    box.appendChild(grid);

    var monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    var weekDays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

    var current = new Date();
    var value = (input.value || "").trim();
    if (value && /^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
      var p = value.split("/");
      current = new Date(parseInt(p[2], 10), parseInt(p[1], 10) - 1, parseInt(p[0], 10));
      if (isNaN(current.getTime())) current = new Date();
    }

    var year = current.getFullYear();
    var month = current.getMonth();

    function renderMonth() {
      grid.innerHTML = "";
      var nav = document.createElement("div");
      nav.className = "bitemporal-cal-nav";
      var prev = document.createElement("a");
      prev.href = "#";
      prev.textContent = "< ";
      prev.addEventListener("click", function (e) {
        e.preventDefault();
        month--;
        if (month < 0) {
          month = 11;
          year--;
        }
        renderMonth();
      });
      var next = document.createElement("a");
      next.href = "#";
      next.textContent = " >";
      next.addEventListener("click", function (e) {
        e.preventDefault();
        month++;
        if (month > 11) {
          month = 0;
          year++;
        }
        renderMonth();
      });
      var label = document.createElement("span");
      label.textContent = monthNames[month] + " " + year;
      nav.appendChild(prev);
      nav.appendChild(label);
      nav.appendChild(next);
      grid.appendChild(nav);

      var table = document.createElement("table");
      table.className = "bitemporal-cal-table";
      var thead = document.createElement("thead");
      var trHead = document.createElement("tr");
      weekDays.forEach(function (d) {
        var th = document.createElement("th");
        th.textContent = d;
        trHead.appendChild(th);
      });
      thead.appendChild(trHead);
      table.appendChild(thead);
      var tbody = document.createElement("tbody");
      table.appendChild(tbody);

      var first = new Date(year, month, 1);
      var last = new Date(year, month + 1, 0);
      var startOffset = first.getDay();
      var daysInMonth = last.getDate();
      var today = new Date();

      var row = document.createElement("tr");
      var dayCount = 0;
      for (var i = 0; i < startOffset; i++) {
        var empty = document.createElement("td");
        empty.className = "bitemporal-cal-noday";
        empty.innerHTML = " ";
        row.appendChild(empty);
        dayCount++;
      }
      for (var d = 1; d <= daysInMonth; d++) {
        if (dayCount === 7) {
          tbody.appendChild(row);
          row = document.createElement("tr");
          dayCount = 0;
        }
        var td = document.createElement("td");
        var a = document.createElement("a");
        a.href = "#";
        a.textContent = d;
        if (today.getFullYear() === year && today.getMonth() === month && today.getDate() === d) {
          td.className = "bitemporal-cal-today";
        }
        a.addEventListener("click", function (evt) {
          evt.preventDefault();
          var dayNum = parseInt(this.textContent, 10);
          input.value = formatDateBR(dayNum, month + 1, year);
          if (input.classList) input.classList.remove("invalid");
          try {
            input.dispatchEvent(new Event("change", { bubbles: true }));
          } catch (e) {}
          overlay.remove();
        });
        td.appendChild(a);
        row.appendChild(td);
        dayCount++;
      }
      while (dayCount < 7) {
        var empty = document.createElement("td");
        empty.className = "bitemporal-cal-noday";
        empty.innerHTML = " ";
        row.appendChild(empty);
        dayCount++;
      }
      tbody.appendChild(row);
      grid.appendChild(table);

      var cancelRow = document.createElement("div");
      cancelRow.className = "bitemporal-cal-cancel";
      var cancelLink = document.createElement("a");
      cancelLink.href = "#";
      cancelLink.textContent = "Fechar";
      cancelLink.addEventListener("click", function (e) {
        e.preventDefault();
        overlay.remove();
      });
      cancelRow.appendChild(cancelLink);
      grid.appendChild(cancelRow);
    }

    renderMonth();
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) overlay.remove();
    });
    document.body.appendChild(overlay);
  }

  function init() {
    var body = document.body || document.getElementsByTagName("body")[0];
    var isAddForm = body && body.classList.contains("add-form");

    // Mantém atalhos de data apenas em formulários de adição.
    if (isAddForm) {
      var inputs = document.querySelectorAll("input.vDateField");
      try {
        console.log(
          "[bitemporal-date-shortcuts] iniciando. vDateField encontrados:",
          inputs.length
        );
      } catch (e) {}
      inputs.forEach(function (input) {
        var name = input.name || "";
        try {
          console.log(
            "[bitemporal-date-shortcuts] analisando input:",
            "name=" + name,
            "id=" + input.id
          );
        } catch (e) {}
        if (name.endsWith("data_vigencia_inicio")) {
          // Apenas "Ano Corrente" para início da vigência.
          addCurrentYearShortcut(input, "inicio");
        } else if (name.endsWith("data_vigencia_fim")) {
          // Para fim da vigência: "Indefinida" + "Ano Corrente".
          addCurrentYearShortcut(input, "fim");
          addIndefinidaShortcut(input);
        }
      });
    }

    // Em formulários de alteração, tornamos vigência somente leitura
    // e adicionamos o botão de edição que leva à tela de confirmação.
    enhanceChangeFormVigencia();

    // Em telas de confirmação bitemporal, adicionamos atalhos de data
    // aos campos de pré-visualização de vigência.
    enhanceConfirmVigenciaPreview();
  }

  function scheduleInit() {
    // Roda após DateTimeShortcuts.init() (também em load) para que o calendário
    // do admin já esteja anexado aos vDateField na tela de confirmação.
    setTimeout(init, 10);
  }

  // Usamos o evento load para garantir que o JS padrão do admin
  // (que adiciona "Hoje" e o ícone de calendário) já tenha rodado.
  if (document.readyState === "complete") {
    scheduleInit();
  } else {
    window.addEventListener("load", scheduleInit);
  }

  // Permite que a tela de confirmação chame os atalhos após re-renderizar a tabela.
  window.bitemporalEnhanceConfirmVigencia = enhanceConfirmVigenciaPreview;
})();

