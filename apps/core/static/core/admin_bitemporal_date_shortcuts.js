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
  }

  function scheduleInit() {
    // Deixa o DateTimeShortcuts.init() rodar primeiro (ele também usa window.load)
    setTimeout(init, 0);
  }

  // Usamos o evento load para garantir que o JS padrão do admin
  // (que adiciona "Hoje" e o ícone de calendário) já tenha rodado.
  if (document.readyState === "complete") {
    scheduleInit();
  } else {
    window.addEventListener("load", scheduleInit);
  }
})();

