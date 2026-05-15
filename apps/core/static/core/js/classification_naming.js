/**
 * Radical do nome a partir do item mãe (admin — criação de ItemClassificacao).
 * Mensagens vêm do elemento #classification-naming-config (json_script).
 */
(function () {
  'use strict';

  function getFieldRow(input) {
    return input ? input.closest('.form-row') || input.closest('div') : null;
  }

  function parseMessages() {
    var el = document.getElementById('classification-naming-config');
    if (!el) return null;
    var raw = (el.textContent || '').trim();
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  function clearReceitaNomeMessages(receitaNomeInput) {
    if (!receitaNomeInput) return;
    var row = getFieldRow(receitaNomeInput);
    if (!row) return;
    var sel =
      '.receita-nome-autofill-info, .receita-nome-autofill-warning, .receita-nome-autofill-error';
    row.querySelectorAll(sel).forEach(function (node) {
      node.remove();
    });
  }

  function showReceitaNomeInfo(receitaNomeInput, text) {
    if (!receitaNomeInput || !text) return;
    var row = getFieldRow(receitaNomeInput);
    if (!row) return;
    clearReceitaNomeMessages(receitaNomeInput);
    var ul = document.createElement('ul');
    ul.className = 'messagelist receita-nome-autofill-info';
    ul.style.marginTop = '6px';
    var li = document.createElement('li');
    li.className = 'info';
    li.textContent = text;
    ul.appendChild(li);
    row.appendChild(ul);
  }

  function showReceitaNomeWarning(receitaNomeInput, text) {
    if (!receitaNomeInput || !text) return;
    var row = getFieldRow(receitaNomeInput);
    if (!row) return;
    clearReceitaNomeMessages(receitaNomeInput);
    var ul = document.createElement('ul');
    ul.className = 'messagelist receita-nome-autofill-warning';
    ul.style.marginTop = '6px';
    var li = document.createElement('li');
    li.className = 'warning';
    li.textContent = text;
    ul.appendChild(li);
    row.appendChild(ul);
  }

  function showReceitaNomeError(receitaNomeInput, text) {
    if (!receitaNomeInput || !text) return;
    var row = getFieldRow(receitaNomeInput);
    if (!row) return;
    clearReceitaNomeMessages(receitaNomeInput);
    var ul = document.createElement('ul');
    ul.className = 'errorlist receita-nome-autofill-error';
    var li = document.createElement('li');
    li.textContent = text;
    ul.appendChild(li);
    row.insertBefore(ul, row.firstChild);
  }

  function removeTopErrorNote(formEl) {
    if (!formEl) return;
    var existing = formEl.querySelector('.classification-naming-errornote');
    if (existing) {
      existing.remove();
    }
  }

  function showTopErrorNote(formEl, text) {
    if (!formEl || !text) return;
    removeTopErrorNote(formEl);
    var note = document.createElement('p');
    note.className = 'errornote classification-naming-errornote';
    note.textContent = text;
    formEl.insertBefore(note, formEl.firstChild);
  }

  function escapeRegExp(s) {
    return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  /** Em character class RegExp (hífen, en dash, em dash). */
  var HYPHEN_CLASS_FRAGMENT = '\\-\\u2013\\u2014';

  /**
   * Remove radical + separador flexível no início do texto. Sem match → null.
   */
  function stripLeadingParentRadical(rawValue, parentBase) {
    var raw = String(rawValue || '');
    var base = String(parentBase || '').trim();
    if (!base) return null;
    var re = new RegExp(
      '^' + escapeRegExp(base) + '\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*'
    );
    if (re.test(raw)) {
      return raw.replace(re, '');
    }
    return null;
  }

  function extractParentNameFromLabel(parentItemIdInput) {
    if (!parentItemIdInput) return '';
    var link = document.getElementById(parentItemIdInput.id + '_label_link');
    var text = link && link.textContent ? link.textContent.trim() : '';
    if (!text) return '';
    var separator = ' - ';
    var idx = text.indexOf(separator);
    if (idx < 0) return '';
    return text.slice(idx + separator.length).trim();
  }

  function scheduleApplyFromParentLookupLabel(parentItemIdInput, receitaNomeInput, applyFn) {
    if (!receitaNomeInput || !parentItemIdInput || !(parentItemIdInput.value || '').trim()) return;
    var tentativas = 0;
    var maxTentativas = 20;
    function tentar() {
      tentativas += 1;
      var nome = extractParentNameFromLabel(parentItemIdInput);
      if (nome) {
        applyFn(nome);
        return;
      }
      if (tentativas < maxTentativas) {
        window.setTimeout(tentar, 50);
      }
    }
    window.setTimeout(tentar, 0);
  }

  /**
   * @param {boolean} isAddMode
   */
  window.initClassificationNaming = function initClassificationNaming(isAddMode) {
    var msgs = parseMessages();
    if (!isAddMode || !msgs) return;

    var receitaNomeInput = document.querySelector('input[name="receita_nome"][type="text"]');
    var parentItemIdInput = document.getElementById('id_parent_item_id');
    if (!receitaNomeInput || !parentItemIdInput) return;
    var adminForm = receitaNomeInput.form;
    /* Hidden do ModelForm não pode dividir nome com radios (mesmo name quebra radios no HTML). */
    var baseModeHiddenInput = null;
    if (adminForm) {
      baseModeHiddenInput = document.getElementById('id_receita_nome_base_mode');
      if (
        !baseModeHiddenInput ||
        baseModeHiddenInput.getAttribute('name') !== 'receita_nome_base_mode'
      ) {
        baseModeHiddenInput = adminForm.querySelector(
          'input[type="hidden"][name="receita_nome_base_mode"]'
        );
      }
    }
    if (!baseModeHiddenInput && adminForm) {
      baseModeHiddenInput = document.createElement('input');
      baseModeHiddenInput.type = 'hidden';
      baseModeHiddenInput.name = 'receita_nome_base_mode';
      baseModeHiddenInput.id = 'id_receita_nome_base_mode_fallback';
      adminForm.appendChild(baseModeHiddenInput);
    }

    var currentParentNameBase = '';
    var radioUseParentName = null;
    var radioNoParentName = null;

    function parentNamePrefix() {
      return currentParentNameBase ? currentParentNameBase + ' - ' : '';
    }

    function nomeReceitaEhSugestaoIncompletaDoRadicalDoPai(nome, radicalDoPai) {
      var n = String(nome || '').trim();
      var b = String(radicalDomãe || '').trim();
      if (!n || !b) return false;
      var withSpaceDashSpace = (b + ' - ').trimEnd();
      var withSpaceDash = b + ' -';
      return n === withSpaceDashSpace || n === withSpaceDash || n === (b + ' - ');
    }

    /** Aviso azul de sugestão só quando o texto é apenas radical do mãe + traço (sem complemento). */
    function refreshReceitaNomeSugestaoInfoMensagem() {
      var radical = String(currentParentNameBase || '').trim();
      if (
        nomeReceitaEhSugestaoIncompletaDoRadicalDoPai(receitaNomeInput.value, radical)
      ) {
        showReceitaNomeInfo(receitaNomeInput, msgs.receita_nome_sugestao_info);
      } else if (radical && receitaNomeInput) {
        var row = getFieldRow(receitaNomeInput);
        if (!row) return;
        row.querySelectorAll('.receita-nome-autofill-info').forEach(function (node) {
          node.remove();
        });
      }
    }

    function setBaseModeValue(mode) {
      if (!baseModeHiddenInput) return;
      baseModeHiddenInput.value = mode || '';
    }

    function applyReceitaNomeBaseFromParent(parentName) {
      if (!parentName) return;
      var normalizedName = String(parentName).trim();
      if (!normalizedName) return;
      currentParentNameBase = normalizedName;
      receitaNomeInput.value = parentNamePrefix();
      if (radioUseParentName) radioUseParentName.checked = true;
      if (radioNoParentName) radioNoParentName.checked = false;
      setBaseModeValue('base_pai');
      refreshReceitaNomeSugestaoInfoMensagem();
    }

    /**
     * Se o campo já veio preenchido (ex.: POST após erro) mas o estado JS ainda não
     * tem radical do pai: tenta o trecho antes do primeiro " - ".
     */
    function inferParentBaseFromReceitaNomeIfEligible() {
      if (currentParentNameBase || !(parentItemIdInput.value || '').trim()) return;
      var raw = receitaNomeInput.value || '';
      var m = raw.match(new RegExp('^(.+?)\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*'));
      if (!m || !(m[1] || '').trim()) return;
      currentParentNameBase = m[1].trim();
    }

    function removeReceitaNomeBaseIfPresent() {
      ensureParentNameBaseFromUi();
      if (!currentParentNameBase) {
        inferParentBaseFromReceitaNomeIfEligible();
      }
      var raw = receitaNomeInput.value || '';
      var baseTrim = String(currentParentNameBase || '').trim();
      if (!baseTrim) return;

      var stripped = stripLeadingParentRadical(raw, baseTrim);
      if (stripped !== null) {
        receitaNomeInput.value = stripped;
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }

      /* Fallback estrito igual ao formato do admin ( espaço traço espaço ). */
      var canonicalPrefix = baseTrim + ' - ';
      if (raw.indexOf(canonicalPrefix) === 0) {
        receitaNomeInput.value = raw.slice(canonicalPrefix.length);
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }

      /*
       * Só alerta quando ainda há radical no início esperado mas o separador falhou em bater:
       * evita falso positivo se removeReceitaNomeBaseIfPresent rodar em sequência após já ter limpado.
       */
      if (raw.indexOf(baseTrim) !== 0) {
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }
      showReceitaNomeWarning(receitaNomeInput, msgs.remove_base_prefix_mismatch);
    }

    function ensureParentNameBaseFromUi() {
      if (currentParentNameBase) return currentParentNameBase;
      if (!(parentItemIdInput.value || '').trim()) return '';
      var fromLabel = extractParentNameFromLabel(parentItemIdInput);
      if (fromLabel) {
        currentParentNameBase = fromLabel;
      }
      return currentParentNameBase;
    }

    function setupReceitaNomeBaseOptions() {
      var row = getFieldRow(receitaNomeInput);
      if (!row || row.querySelector('.receita-nome-base-options')) return;

      var container = document.createElement('div');
      container.className = 'receita-nome-base-options';
      container.style.marginTop = '6px';
      container.style.marginBottom = '2px';
      container.style.display = 'block';
      container.style.clear = 'both';
      container.style.width = '100%';
      var optionsInline = document.createElement('div');
      optionsInline.style.display = 'inline-flex';
      optionsInline.style.alignItems = 'center';
      optionsInline.style.gap = '18px';
      var radioUiName = '__classification_naming_base_mode_ui';
      container.innerHTML =
        '<label style="display:inline-flex; align-items:center; margin:0;"><input style="margin-right:6px;" type="radio" name="' +
        radioUiName +
        '" value="base_pai"> Radical Baseado no item pai</label>' +
        '<label style="display:inline-flex; align-items:center; margin:0;"><input style="margin-right:6px;" type="radio" name="' +
        radioUiName +
        '" value="sem_base"> Sem Nome Base</label>';
      optionsInline.innerHTML = container.innerHTML;
      container.innerHTML = '';
      container.appendChild(optionsInline);

      var helpEl = row.querySelector('p.help, .help, .helptext');
      var infoMsg = row.querySelector(
        '.receita-nome-autofill-info, .receita-nome-autofill-warning, .receita-nome-autofill-error'
      );
      if (helpEl && infoMsg && infoMsg.parentNode === row) {
        row.insertBefore(container, infoMsg);
      } else if (helpEl && helpEl.parentNode === row) {
        helpEl.insertAdjacentElement('afterend', container);
      } else if (infoMsg && infoMsg.parentNode === row) {
        row.insertBefore(container, infoMsg);
      } else {
        row.appendChild(container);
      }

      try {
        var rowRect = row.getBoundingClientRect();
        var inputRect = receitaNomeInput.getBoundingClientRect();
        var leftOffset = Math.max(0, Math.round(inputRect.left - rowRect.left));
        container.style.paddingLeft = leftOffset + 'px';
      } catch (e) {}

      radioUseParentName = container.querySelector('input[value="base_pai"]');
      radioNoParentName = container.querySelector('input[value="sem_base"]');

      if (radioUseParentName) {
        function onRadicalOptionSelected() {
          if (!radioUseParentName.checked) return;
          setBaseModeValue('base_pai');
          ensureParentNameBaseFromUi();
          if (!currentParentNameBase) return;
          var prefix = parentNamePrefix();
          if ((receitaNomeInput.value || '').indexOf(prefix) !== 0) {
            receitaNomeInput.value = prefix + (receitaNomeInput.value || '');
          }
          refreshReceitaNomeSugestaoInfoMensagem();
        }
        radioUseParentName.addEventListener('change', onRadicalOptionSelected);
        radioUseParentName.addEventListener('click', function () {
          window.setTimeout(function () {
            if (radioUseParentName.checked) {
              onRadicalOptionSelected();
            }
          }, 0);
        });
      }
      if (radioNoParentName) {
        radioNoParentName.addEventListener('change', function () {
          if (!radioNoParentName.checked) return;
          setBaseModeValue('sem_base');
          removeReceitaNomeBaseIfPresent();
        });
      }

      var persistedMode = (baseModeHiddenInput && baseModeHiddenInput.value
        ? baseModeHiddenInput.value
        : '').trim();
      if (persistedMode === 'base_pai' && radioUseParentName) {
        radioUseParentName.checked = true;
      } else if (persistedMode === 'sem_base' && radioNoParentName) {
        radioNoParentName.checked = true;
      }
    }

    function clearReceitaNomeBaseSelection() {
      currentParentNameBase = '';
      if (radioUseParentName) radioUseParentName.checked = false;
      if (radioNoParentName) radioNoParentName.checked = false;
      setBaseModeValue('');
    }

    setupReceitaNomeBaseOptions();

    /**
     * Mantém radical do mãe sincronizado com o formulário já repovoado pelo servidor,
     * sem sobrescrever receita_nome.
     */
    function scheduleHydrateParentNameBaseOnLoad() {
      if (!(parentItemIdInput.value || '').trim()) return;
      var nomeTemConteudo = !!((receitaNomeInput.value || '').trim());
      if (!nomeTemConteudo) return;

      var tentativas = 0;
      var maxTentativas = 20;

      function umPasso() {
        tentativas += 1;
        ensureParentNameBaseFromUi();
        if (!currentParentNameBase) {
          inferParentBaseFromReceitaNomeIfEligible();
        }
        if (currentParentNameBase || tentativas >= maxTentativas) {
          return;
        }
        window.setTimeout(umPasso, 50);
      }

      window.setTimeout(umPasso, 0);
    }

    scheduleHydrateParentNameBaseOnLoad();

    parentItemIdInput.addEventListener('change', function () {
      window.setTimeout(function () {
        var hasParent = !!((parentItemIdInput.value || '').trim());
        if (!hasParent) {
          clearReceitaNomeBaseSelection();
          clearReceitaNomeMessages(receitaNomeInput);
          return;
        }
        scheduleApplyFromParentLookupLabel(parentItemIdInput, receitaNomeInput, applyReceitaNomeBaseFromParent);
      }, 0);
    });

    receitaNomeInput.addEventListener('input', function () {
      receitaNomeInput.setCustomValidity('');
      clearReceitaNomeMessages(receitaNomeInput);
      removeTopErrorNote(adminForm);
    });

    window.setTimeout(function () {
      if (
        (parentItemIdInput.value || '').trim() &&
        !(receitaNomeInput.value || '').trim()
      ) {
        scheduleApplyFromParentLookupLabel(parentItemIdInput, receitaNomeInput, applyReceitaNomeBaseFromParent);
      }
    }, 0);

    window.validateClassificationNamingOnSubmit = function validateClassificationNamingOnSubmit() {
      if (!isAddMode || !receitaNomeInput) return true;
      var nomeAtual = (receitaNomeInput.value || '').trim();
      ensureParentNameBaseFromUi();
      if (!currentParentNameBase) {
        inferParentBaseFromReceitaNomeIfEligible();
      }
      var radicalServidor = String(currentParentNameBase || '').trim();
      var bloquearPorNomeSomenteRadicalAutomatico =
        !!radicalServidor &&
        nomeReceitaEhSugestaoIncompletaDoRadicalDoPai(nomeAtual, radicalServidor);

      if (bloquearPorNomeSomenteRadicalAutomatico) {
        var nomeMsg = msgs.receita_nome_submit_incompleto_error || '';
        receitaNomeInput.setCustomValidity(nomeMsg);
        showReceitaNomeError(receitaNomeInput, nomeMsg);
        showTopErrorNote(adminForm, 'Por favor corrija o erro abaixo.');
        return false;
      }
      receitaNomeInput.setCustomValidity('');
      clearReceitaNomeMessages(receitaNomeInput);
      removeTopErrorNote(adminForm);
      return true;
    };
  };
})();
