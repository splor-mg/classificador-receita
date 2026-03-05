// Atalhos de "Ano Corrente" para campos de vigência no Django Admin.
// Funciona para qualquer formulário que tenha os campos:
//   - data_vigencia_inicio
//   - data_vigencia_fim
// usando os widgets padrão de data do admin (vDateField).

(function () {
  // Log básico para confirmar que o script foi carregado.
  try {
    console.log("[bitemporal-date-shortcuts] script carregado.");
  } catch (e) {
    // Ambiente sem console — ignora.
  }
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
    // Campos de vigência na tela de confirmação (com vDateField para o admin).
    var inputs = document.querySelectorAll(
      'input.vDateField[name^="edit_vig_inicio_"], input.vDateField[name^="edit_vig_fim_"]'
    );
    if (!inputs.length) {
      return;
    }

    // Se o admin já anexou o calendário (DateTimeShortcuts), o ícone abre direto
    // a tabela de mês. Só acrescentamos "Indefinida" e "Ano Corrente" no span.
    var useDjangoCalendar =
      window.DateTimeShortcuts &&
      typeof DateTimeShortcuts.addCalendar === "function";

    function prependLink(container, label, handler, className) {
      var link = document.createElement("a");
      link.href = "#";
      link.textContent = label;
      if (className) link.className = className;
      link.style.textDecoration = "none";
      link.style.borderBottom = "none";
      link.style.cursor = "pointer";
      link.addEventListener("click", function (evt) {
        evt.preventDefault();
        handler();
      });
      container.insertBefore(document.createTextNode(" | "), container.firstChild);
      container.insertBefore(link, container.firstChild);
    }

    inputs.forEach(function (input) {
      if (input.dataset && input.dataset.bitemporalShortcutsAttached === "1") {
        return;
      }
      if (input.dataset) input.dataset.bitemporalShortcutsAttached = "1";

      var name = input.name || "";
      var shortcuts = findShortcutsSpan(input);

      if (useDjangoCalendar && !shortcuts) {
        DateTimeShortcuts.addCalendar(input);
        if (typeof DateTimeShortcuts.addTimezoneWarning === "function") {
          DateTimeShortcuts.addTimezoneWarning(input);
        }
        shortcuts = findShortcutsSpan(input);
      }

      if (shortcuts) {
        if (shortcuts.style.marginLeft !== "0.5rem") {
          shortcuts.style.marginLeft = "0.5rem";
        }
        // Evitar duplicar nossos links ao trocar de estratégia e re-renderizar.
        if (shortcuts.querySelector(".date-current-year")) {
          return;
        }
        if (name.indexOf("edit_vig_fim_") === 0) {
          prependLink(shortcuts, "Indefinida", function () {
            input.value = formatDateBR(31, 12, 9999);
            if (input.classList) input.classList.remove("invalid");
            try { input.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
          }, "date-indefinida");
        }
        prependLink(shortcuts, "Ano Corrente", function () {
          var today = new Date();
          var year = today.getFullYear();
          input.value =
            name.indexOf("edit_vig_inicio_") === 0
              ? formatDateBR(1, 1, year)
              : formatDateBR(31, 12, year);
          if (input.classList) input.classList.remove("invalid");
          try { input.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
        }, "date-current-year");
        return;
      }

      // Fallback: DateTimeShortcuts não disponível; criar span e atalhos manualmente
      // (incluindo popup com input type="date").
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
      function openCalendarPopup(targetInput) {
        var overlay = document.createElement("div");
        overlay.className = "bitemporal-calendar-overlay";
        var box = document.createElement("div");
        box.className = "bitemporal-calendar-box bitemporal-calendar-grid";
        var monthNames = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
          "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
        var weekDays = ["D", "S", "T", "Q", "Q", "S", "S"];
        var currentVal = (targetInput && targetInput.value) || "";
        var viewDate = new Date();
        if (currentVal) {
          var parts = currentVal.split("/");
          if (parts.length === 3) {
            var d = parseInt(parts[0], 10);
            var m = parseInt(parts[1], 10) - 1;
            var y = parseInt(parts[2], 10);
            if (!isNaN(d) && !isNaN(m) && m >= 0 && m <= 11 && !isNaN(y)) {
              viewDate = new Date(y, m, d);
            }
          }
        }
        function setAndClose(day, month, year) {
          if (targetInput) {
            targetInput.value = formatDateBR(day, month + 1, year);
            if (targetInput.classList) targetInput.classList.remove("invalid");
            try { targetInput.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
          }
          if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        }
        function renderMonth() {
          gridBody.innerHTML = "";
          var y = viewDate.getFullYear();
          var m = viewDate.getMonth();
          var first = new Date(y, m, 1);
          var last = new Date(y, m + 1, 0);
          var startDay = first.getDay();
          var daysInMonth = last.getDate();
          var today = new Date();
          var row = document.createElement("tr");
          for (var i = 0; i < startDay; i++) {
            var empty = document.createElement("td");
            empty.className = "bitemporal-cal-noday";
            empty.textContent = "\u00A0";
            row.appendChild(empty);
          }
          for (var day = 1; day <= daysInMonth; day++) {
            if (row.children.length === 7) {
              gridBody.appendChild(row);
              row = document.createElement("tr");
            }
            var td = document.createElement("td");
            var a = document.createElement("a");
            a.href = "#";
            a.textContent = day;
            var isToday = today.getDate() === day && today.getMonth() === m && today.getFullYear() === y;
            if (isToday) td.className = "bitemporal-cal-today";
            (function (d, mon, yr) {
              a.addEventListener("click", function (evt) {
                evt.preventDefault();
                setAndClose(d, mon, yr);
              });
            })(day, m, y);
            td.appendChild(a);
            row.appendChild(td);
          }
          while (row.children.length < 7 && row.children.length > 0) {
            var empty = document.createElement("td");
            empty.className = "bitemporal-cal-noday";
            empty.textContent = "\u00A0";
            row.appendChild(empty);
          }
          if (row.children.length) gridBody.appendChild(row);
          titleEl.textContent = monthNames[m] + " " + y;
        }
        var nav = document.createElement("div");
        nav.className = "bitemporal-cal-nav";
        var prev = document.createElement("a");
        prev.href = "#";
        prev.textContent = "\u2039";
        prev.addEventListener("click", function (e) {
          e.preventDefault();
          viewDate.setMonth(viewDate.getMonth() - 1);
          renderMonth();
        });
        var titleEl = document.createElement("span");
        titleEl.className = "bitemporal-cal-title";
        var next = document.createElement("a");
        next.href = "#";
        next.textContent = "\u203A";
        next.addEventListener("click", function (e) {
          e.preventDefault();
          viewDate.setMonth(viewDate.getMonth() + 1);
          renderMonth();
        });
        nav.appendChild(prev);
        nav.appendChild(titleEl);
        nav.appendChild(next);
        box.appendChild(nav);
        var table = document.createElement("table");
        table.className = "bitemporal-cal-table";
        var thead = document.createElement("thead");
        var trHead = document.createElement("tr");
        weekDays.forEach(function (w) {
          var th = document.createElement("th");
          th.textContent = w;
          trHead.appendChild(th);
        });
        thead.appendChild(trHead);
        table.appendChild(thead);
        var gridBody = document.createElement("tbody");
        table.appendChild(gridBody);
        box.appendChild(table);
        var shortcuts = document.createElement("div");
        shortcuts.className = "bitemporal-cal-shortcuts";
        var yesterday = document.createElement("a");
        yesterday.href = "#";
        yesterday.textContent = "Ontem";
        yesterday.addEventListener("click", function (e) {
          e.preventDefault();
          var t = new Date();
          t.setDate(t.getDate() - 1);
          setAndClose(t.getDate(), t.getMonth(), t.getFullYear());
        });
        var todayLink = document.createElement("a");
        todayLink.href = "#";
        todayLink.textContent = "Hoje";
        todayLink.addEventListener("click", function (e) {
          e.preventDefault();
          var t = new Date();
          setAndClose(t.getDate(), t.getMonth(), t.getFullYear());
        });
        var tomorrow = document.createElement("a");
        tomorrow.href = "#";
        tomorrow.textContent = "Amanhã";
        tomorrow.addEventListener("click", function (e) {
          e.preventDefault();
          var t = new Date();
          t.setDate(t.getDate() + 1);
          setAndClose(t.getDate(), t.getMonth(), t.getFullYear());
        });
        shortcuts.appendChild(yesterday);
        shortcuts.appendChild(document.createTextNode(" | "));
        shortcuts.appendChild(todayLink);
        shortcuts.appendChild(document.createTextNode(" | "));
        shortcuts.appendChild(tomorrow);
        box.appendChild(shortcuts);
        var cancelP = document.createElement("p");
        cancelP.className = "bitemporal-cal-cancel";
        var cancelLink = document.createElement("a");
        cancelLink.href = "#";
        cancelLink.textContent = "Cancelar";
        cancelLink.addEventListener("click", function (e) {
          e.preventDefault();
          if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        });
        cancelP.appendChild(cancelLink);
        box.appendChild(cancelP);
        overlay.appendChild(box);
        overlay.addEventListener("click", function (evt) {
          if (evt.target === overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
          }
        });
        document.body.appendChild(overlay);
        renderMonth();
      }
      var fallbackSpan = createShortcutsContainer(input);
      if (!fallbackSpan) return;
      if (name.indexOf("edit_vig_fim_") === 0) {
        addShortcutLink(fallbackSpan, "Indefinida", function () {
          input.value = formatDateBR(31, 12, 9999);
          if (input.classList) input.classList.remove("invalid");
          try { input.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
        });
      }
      addShortcutLink(fallbackSpan, "Ano Corrente", function () {
        var today = new Date();
        var year = today.getFullYear();
        input.value =
          name.indexOf("edit_vig_inicio_") === 0
            ? formatDateBR(1, 1, year)
            : formatDateBR(31, 12, year);
        if (input.classList) input.classList.remove("invalid");
        try { input.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
      });
      addShortcutLink(fallbackSpan, "Hoje", function () {
        var d = new Date();
        input.value = formatDateBR(d.getDate(), d.getMonth() + 1, d.getFullYear());
        if (input.classList) input.classList.remove("invalid");
        try { input.dispatchEvent(new Event("change", { bubbles: true })); } catch (e) {}
      });
      var calLink = document.createElement("a");
      calLink.href = "#";
      calLink.title = "Calendário";
      calLink.style.textDecoration = "none";
      calLink.style.borderBottom = "none";
      calLink.style.cursor = "pointer";
      calLink.addEventListener("click", function (evt) {
        evt.preventDefault();
        openCalendarPopup(input);
      });
      var calIcon = document.createElement("span");
      calIcon.className = "date-icon";
      calIcon.setAttribute("aria-hidden", "true");
      calLink.appendChild(calIcon);
      fallbackSpan.appendChild(document.createTextNode(" | "));
      fallbackSpan.appendChild(calLink);
    });
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

