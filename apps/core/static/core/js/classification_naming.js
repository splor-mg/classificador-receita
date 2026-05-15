/**
 * Radical do nome a partir do item mãe (admin — criação de ItemClassificacao).
 * Mensagens: #classification-naming-config (json_script).
 * Spec: _dev/spec_itemClassificacao_criar_nome.md
 */
(function () {
  'use strict';

  var SUFIXO_CANONICO = ' - ';
  var HYPHEN_CLASS_FRAGMENT = '\\-\\u2013\\u2014';

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
    if (existing) existing.remove();
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

  function normalizeBaseMode(mode) {
    var m = String(mode || '').trim();
    if (m === 'base_pai') return 'base_pai_completo';
    return m;
  }

  /** **G1.2** — paridade com classification_naming_validation.py */
  function receitaNomeEhSugestaoIncompleta(nome, radical) {
    var n = String(nome || '').trim();
    var b = String(radical || '').trim();
    if (!n || !b) return false;
    if (n === b) return true;
    var re = new RegExp(
      '^' + escapeRegExp(b) + '\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*$',
      'u'
    );
    return re.test(n);
  }

  function stripLeadingParentRadical(rawValue, radicalBase) {
    var raw = String(rawValue || '');
    var base = String(radicalBase || '').trim();
    if (!base) return null;
    var re = new RegExp(
      '^' + escapeRegExp(base) + '\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*'
    );
    if (re.test(raw)) {
      return raw.replace(re, '');
    }
    return null;
  }

  function extractNomeMaeFromLabel(parentItemIdInput) {
    if (!parentItemIdInput) return '';
    var link = document.getElementById(parentItemIdInput.id + '_label_link');
    var text = link && link.textContent ? link.textContent.trim() : '';
    if (!text) return '';
    var separator = ' - ';
    var idx = text.indexOf(separator);
    if (idx < 0) return '';
    return text.slice(idx + separator.length).trim();
  }

  /** **A9.2** — complemento após primeiro separador flexível (N7). */
  function extrairComplementoPreservado(rawValue) {
    var raw = String(rawValue || '');
    var re = new RegExp('^(.+?)\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*(.+)$', 'u');
    var m = raw.match(re);
    if (!m) return '';
    var tail = (m[2] || '').trim();
    if (!tail || !/\S/.test(tail)) return '';
    return tail;
  }

  function nomeMaeIgual(a, b) {
    return String(a || '').trim().toLowerCase() === String(b || '').trim().toLowerCase();
  }

  function formatSugestaoInfoAbrev(template, nomeMae) {
    var escaped = String(nomeMae || '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
    return String(template || '').replace('{nome_mae}', escaped);
  }

  /** **(N9)** — prefixo com sufixo canônico (N5). */
  function prefixoComSufixoCanonico(radical) {
    var r = String(radical || '').trim();
    return r ? r + SUFIXO_CANONICO : '';
  }

  function valorComecaPorPrefixoCanonico(val, prefixo) {
    return !!prefixo && String(val || '').indexOf(prefixo) === 0;
  }

  /**
   * **A9.2 / A9.3** — remove radical conhecido (N7) e repõe novo prefixo + complemento.
   * Quando o strip pelo radical reconhecido **corresponde** mas não resta texto (**M1.5**
   * só sugestão incompleta), **não** usar ``extrairComplementoPreservado`` no valor inteiro —
   * nomes multi-segmento teriam o primeiro traço interno confundido com início do complemento.
   */
  function reporRadicalPreservandoComplemento(val, novoPrefixo, radicalRemover) {
    var complemento = '';
    if (radicalRemover) {
      var stripped = stripLeadingParentRadical(val, radicalRemover);
      if (stripped !== null) {
        complemento = String(stripped).trim();
        return complemento ? novoPrefixo + complemento : novoPrefixo;
      }
    }
    complemento = extrairComplementoPreservado(val).trim();
    return complemento ? novoPrefixo + complemento : novoPrefixo;
  }

  function scheduleApplyFromParentLookupLabel(parentItemIdInput, applyFn) {
    if (!parentItemIdInput || !(parentItemIdInput.value || '').trim()) return;
    var tentativas = 0;
    var maxTentativas = 20;
    function tentar() {
      tentativas += 1;
      var nome = extractNomeMaeFromLabel(parentItemIdInput);
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
   * @param {string} abbrevLookupUrl
   */
  window.initClassificationNaming = function initClassificationNaming(isAddMode, abbrevLookupUrl) {
    var msgs = parseMessages();
    if (!isAddMode || !msgs) return;

    var receitaNomeInput = document.querySelector('input[name="receita_nome"][type="text"]');
    var parentItemIdInput = document.getElementById('id_parent_item_id');
    if (!receitaNomeInput || !parentItemIdInput) return;

    var adminForm = receitaNomeInput.form;
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

    var nomeMae = '';
    var radicalAbreviado = '';
    var radicalConhecidoRemocao = '';
    var ultimoParentPkAplicado = '';
    var radioAbrev = null;
    var radioCompleto = null;
    var radioSemBase = null;

    function getBaseMode() {
      return normalizeBaseMode(
        baseModeHiddenInput ? baseModeHiddenInput.value : ''
      );
    }

    function setBaseModeValue(mode) {
      if (!baseModeHiddenInput) return;
      baseModeHiddenInput.value = mode || '';
    }

    function radicalEfetivoGuardrail() {
      var mode = getBaseMode();
      if (mode === 'base_pai_completo') {
        return String(nomeMae || '').trim();
      }
      if (mode === 'base_pai_abrev') {
        return String(radicalAbreviado || '').trim();
      }
      return '';
    }

    function fetchRadicalAbreviado(nomeMaeVal, callback) {
      if (!abbrevLookupUrl || !nomeMaeVal) {
        callback(null, []);
        return;
      }
      var url =
        abbrevLookupUrl +
        '?nome_mae=' +
        encodeURIComponent(nomeMaeVal);
      var pk = (parentItemIdInput.value || '').trim();
      if (pk) {
        url += '&parent_item_id=' + encodeURIComponent(pk);
      }
      fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          if (!data || !data.ok) {
            callback(null, data && data.lexico_alertas ? data.lexico_alertas : []);
            return;
          }
          callback(
            {
              radical: String(data.radical || '').trim(),
              sugerido: String(data.receita_nome_sugerido || '').trim(),
            },
            data.lexico_alertas || []
          );
        })
        .catch(function () {
          callback(null, []);
        });
    }

    function showLexicoAlertas(alertas) {
      if (!alertas || !alertas.length) return;
      alertas.forEach(function (text) {
        if (text) showReceitaNomeWarning(receitaNomeInput, text);
      });
    }

    function refreshReceitaNomeSugestaoInfoMensagem() {
      var b = radicalEfetivoGuardrail();
      var mode = getBaseMode();
      if (
        b &&
        (mode === 'base_pai_completo' || mode === 'base_pai_abrev') &&
        receitaNomeEhSugestaoIncompleta(receitaNomeInput.value, b)
      ) {
        if (mode === 'base_pai_completo') {
          showReceitaNomeInfo(
            receitaNomeInput,
            msgs.receita_nome_sugestao_info_completo || ''
          );
        } else {
          showReceitaNomeInfo(
            receitaNomeInput,
            formatSugestaoInfoAbrev(
              msgs.receita_nome_sugestao_info_abrev_template,
              nomeMae
            )
          );
        }
      } else if (b && receitaNomeInput) {
        var row = getFieldRow(receitaNomeInput);
        if (!row) return;
        row.querySelectorAll('.receita-nome-autofill-info').forEach(function (node) {
          node.remove();
        });
      }
    }

    /**
     * **P-mãe.2-bis / A9.2-bis:** na troca de mãe, não preservar prefixo se o valor
     * atual for só sugestão incompleta (G1.2) da mãe anterior.
     */
    function complementoPreservadoNaTrocaItemMae(nomeMaeNovo, nomeMaeAnterior) {
      var raw = receitaNomeInput.value || '';
      var bAntigo = radicalEfetivoGuardrail();
      if (
        nomeMaeAnterior &&
        nomeMaeNovo &&
        !nomeMaeIgual(nomeMaeAnterior, nomeMaeNovo) &&
        bAntigo &&
        receitaNomeEhSugestaoIncompleta(raw, bAntigo)
      ) {
        return '';
      }
      return extrairComplementoPreservado(raw);
    }

    /** **P-mãe** */
    function applyProtocoloItemMae(nomeMaeVal, parentPkOpt) {
      var nomeMaeNovo = String(nomeMaeVal || '').trim();
      if (!nomeMaeNovo) return;

      var nomeMaeAnterior = nomeMae;
      var complemento = complementoPreservadoNaTrocaItemMae(nomeMaeNovo, nomeMaeAnterior);
      nomeMae = nomeMaeNovo;
      if (parentPkOpt) {
        ultimoParentPkAplicado = String(parentPkOpt);
      } else if ((parentItemIdInput.value || '').trim()) {
        ultimoParentPkAplicado = String(parentItemIdInput.value).trim();
      }

      fetchRadicalAbreviado(nomeMae, function (result, alertas) {
        clearReceitaNomeMessages(receitaNomeInput);

        if (result && result.radical) {
          radicalAbreviado = result.radical;
        } else {
          radicalAbreviado = nomeMae;
        }
        radicalConhecidoRemocao = radicalAbreviado;

        var prefixo = radicalAbreviado + SUFIXO_CANONICO;
        receitaNomeInput.value = complemento ? prefixo + complemento : prefixo;

        if (radioAbrev) radioAbrev.checked = true;
        if (radioCompleto) radioCompleto.checked = false;
        if (radioSemBase) radioSemBase.checked = false;
        setBaseModeValue('base_pai_abrev');

        showLexicoAlertas(alertas);
        refreshReceitaNomeSugestaoInfoMensagem();
      });
    }

    /** **M1.3 / M1.5 / A9.3.1** */
    function applyModoCompletoCore() {
      setBaseModeValue('base_pai_completo');
      radicalConhecidoRemocao = nomeMae;
      var pCompleto = prefixoComSufixoCanonico(nomeMae);
      var pAbrev = prefixoComSufixoCanonico(radicalAbreviado);
      var val = receitaNomeInput.value || '';

      if (valorComecaPorPrefixoCanonico(val, pCompleto)) {
        refreshReceitaNomeSugestaoInfoMensagem();
        return;
      }

      if (
        pAbrev &&
        valorComecaPorPrefixoCanonico(val, pAbrev) &&
        !valorComecaPorPrefixoCanonico(val, pCompleto)
      ) {
        receitaNomeInput.value = reporRadicalPreservandoComplemento(
          val,
          pCompleto,
          radicalAbreviado
        );
        refreshReceitaNomeSugestaoInfoMensagem();
        return;
      }

      if (stripLeadingParentRadical(val, nomeMae) !== null) {
        receitaNomeInput.value = reporRadicalPreservandoComplemento(
          val,
          pCompleto,
          nomeMae
        );
        refreshReceitaNomeSugestaoInfoMensagem();
        return;
      }

      if (
        !valorComecaPorPrefixoCanonico(val, pCompleto) &&
        !(pAbrev && valorComecaPorPrefixoCanonico(val, pAbrev))
      ) {
        receitaNomeInput.value = pCompleto + val;
      }
      refreshReceitaNomeSugestaoInfoMensagem();
    }

    function applyModoCompleto() {
      ensureNomeMaeFromUi();
      if (!nomeMae) return;
      if (radicalAbreviado) {
        applyModoCompletoCore();
        return;
      }
      fetchRadicalAbreviado(nomeMae, function (result) {
        if (result && result.radical) {
          radicalAbreviado = result.radical;
        } else if (nomeMae) {
          radicalAbreviado = nomeMae;
        }
        applyModoCompletoCore();
      });
    }

    /** **M1.3 (Abreviado) / A9.3.2** */
    function applyModoAbreviadoCore(alertas) {
      setBaseModeValue('base_pai_abrev');
      radicalConhecidoRemocao = radicalAbreviado;
      var pAbrev = prefixoComSufixoCanonico(radicalAbreviado);
      var pCompleto = prefixoComSufixoCanonico(nomeMae);
      var val = receitaNomeInput.value || '';

      if (valorComecaPorPrefixoCanonico(val, pAbrev)) {
        showLexicoAlertas(alertas);
        refreshReceitaNomeSugestaoInfoMensagem();
        return;
      }

      if (
        valorComecaPorPrefixoCanonico(val, pCompleto) ||
        stripLeadingParentRadical(val, nomeMae) !== null
      ) {
        receitaNomeInput.value = reporRadicalPreservandoComplemento(
          val,
          pAbrev,
          nomeMae
        );
        showLexicoAlertas(alertas);
        refreshReceitaNomeSugestaoInfoMensagem();
        return;
      }

      if (
        !valorComecaPorPrefixoCanonico(val, pCompleto) &&
        !valorComecaPorPrefixoCanonico(val, pAbrev)
      ) {
        receitaNomeInput.value = pAbrev + val;
      }
      showLexicoAlertas(alertas);
      refreshReceitaNomeSugestaoInfoMensagem();
    }

    function removeReceitaNomeBaseIfPresent() {
      var raw = receitaNomeInput.value || '';
      var baseTrim = String(radicalConhecidoRemocao || nomeMae || radicalAbreviado || '').trim();
      if (!baseTrim) {
        inferRadicalFromReceitaNomeIfEligible();
        baseTrim = String(radicalConhecidoRemocao || '').trim();
      }
      if (!baseTrim) return;

      var stripped = stripLeadingParentRadical(raw, baseTrim);
      if (stripped !== null) {
        receitaNomeInput.value = stripped;
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }

      var canonicalPrefix = baseTrim + SUFIXO_CANONICO;
      if (raw.indexOf(canonicalPrefix) === 0) {
        receitaNomeInput.value = raw.slice(canonicalPrefix.length);
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }

      if (raw.indexOf(baseTrim) !== 0) {
        clearReceitaNomeMessages(receitaNomeInput);
        return;
      }
      showReceitaNomeWarning(receitaNomeInput, msgs.remove_base_prefix_mismatch);
    }

    function ensureNomeMaeFromUi() {
      if (nomeMae) return nomeMae;
      if (!(parentItemIdInput.value || '').trim()) return '';
      var fromLabel = extractNomeMaeFromLabel(parentItemIdInput);
      if (fromLabel) nomeMae = fromLabel;
      return nomeMae;
    }

    function inferRadicalFromReceitaNomeIfEligible() {
      if (radicalConhecidoRemocao || !(parentItemIdInput.value || '').trim()) return;
      var raw = receitaNomeInput.value || '';
      var m = raw.match(new RegExp('^(.+?)\\s*[' + HYPHEN_CLASS_FRAGMENT + ']\\s*'));
      if (!m || !(m[1] || '').trim()) return;
      radicalConhecidoRemocao = m[1].trim();
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
      optionsInline.innerHTML =
        '<label style="display:inline-flex; align-items:center; margin:0;">' +
        '<input style="margin-right:6px;" type="radio" name="' +
        radioUiName +
        '" value="base_pai_abrev"> Radical Baseado no Item Mãe - Abreviado</label>' +
        '<label style="display:inline-flex; align-items:center; margin:0;">' +
        '<input style="margin-right:6px;" type="radio" name="' +
        radioUiName +
        '" value="base_pai_completo"> Radical Baseado no Item Mãe - Completo</label>' +
        '<label style="display:inline-flex; align-items:center; margin:0;">' +
        '<input style="margin-right:6px;" type="radio" name="' +
        radioUiName +
        '" value="sem_base"> Sem Nome Base</label>';

      container.appendChild(optionsInline);

      var helpEl = row.querySelector('p.help, .help, .helptext');
      if (helpEl && helpEl.parentNode === row) {
        helpEl.insertAdjacentElement('afterend', container);
      } else {
        row.appendChild(container);
      }

      try {
        var rowRect = row.getBoundingClientRect();
        var inputRect = receitaNomeInput.getBoundingClientRect();
        var leftOffset = Math.max(0, Math.round(inputRect.left - rowRect.left));
        container.style.paddingLeft = leftOffset + 'px';
      } catch (e) {}

      radioAbrev = optionsInline.querySelector('input[value="base_pai_abrev"]');
      radioCompleto = optionsInline.querySelector('input[value="base_pai_completo"]');
      radioSemBase = optionsInline.querySelector('input[value="sem_base"]');

      if (radioAbrev) {
        radioAbrev.addEventListener('change', function () {
          if (!radioAbrev.checked) return;
          ensureNomeMaeFromUi();
          if (!nomeMae) return;
          clearReceitaNomeMessages(receitaNomeInput);
          fetchRadicalAbreviado(nomeMae, function (result, alertas) {
            if (result && result.radical) radicalAbreviado = result.radical;
            else radicalAbreviado = nomeMae;
            applyModoAbreviadoCore(alertas);
          });
        });
      }

      if (radioCompleto) {
        radioCompleto.addEventListener('change', function () {
          if (!radioCompleto.checked) return;
          if (radioAbrev) radioAbrev.checked = false;
          applyModoCompleto();
        });
      }

      if (radioSemBase) {
        radioSemBase.addEventListener('change', function () {
          if (!radioSemBase.checked) return;
          setBaseModeValue('sem_base');
          removeReceitaNomeBaseIfPresent();
        });
      }

      var persisted = normalizeBaseMode(
        baseModeHiddenInput ? baseModeHiddenInput.value : ''
      );
      if (persisted === 'base_pai_abrev' && radioAbrev) {
        radioAbrev.checked = true;
      } else if (persisted === 'base_pai_completo' && radioCompleto) {
        radioCompleto.checked = true;
      } else if (persisted === 'sem_base' && radioSemBase) {
        radioSemBase.checked = true;
      }
    }

    function clearReceitaNomeBaseSelection() {
      nomeMae = '';
      radicalAbreviado = '';
      radicalConhecidoRemocao = '';
      if (radioAbrev) radioAbrev.checked = false;
      if (radioCompleto) radioCompleto.checked = false;
      if (radioSemBase) radioSemBase.checked = false;
      setBaseModeValue('');
    }

    function scheduleHydrateOnLoad() {
      if (!(parentItemIdInput.value || '').trim()) return;
      if (!(receitaNomeInput.value || '').trim()) return;
      var tentativas = 0;
      function umPasso() {
        tentativas += 1;
        ensureNomeMaeFromUi();
        var mode = getBaseMode();
        if (mode === 'base_pai_abrev' && nomeMae) {
          fetchRadicalAbreviado(nomeMae, function (result) {
            if (result && result.radical) {
              radicalAbreviado = result.radical;
              radicalConhecidoRemocao = radicalAbreviado;
            }
          });
        } else if (mode === 'base_pai_completo' && nomeMae) {
          radicalConhecidoRemocao = nomeMae;
        } else {
          inferRadicalFromReceitaNomeIfEligible();
        }
        if (nomeMae || tentativas >= 20) {
          refreshReceitaNomeSugestaoInfoMensagem();
          return;
        }
        window.setTimeout(umPasso, 50);
      }
      window.setTimeout(umPasso, 0);
    }

    setupReceitaNomeBaseOptions();
    scheduleHydrateOnLoad();

    parentItemIdInput.addEventListener('change', function () {
      window.setTimeout(function () {
        if (!(parentItemIdInput.value || '').trim()) {
          clearReceitaNomeBaseSelection();
          ultimoParentPkAplicado = '';
          clearReceitaNomeMessages(receitaNomeInput);
          return;
        }
        var pkAtual = String(parentItemIdInput.value || '').trim();
        if (ultimoParentPkAplicado === pkAtual && nomeMae) {
          return;
        }
        scheduleApplyFromParentLookupLabel(parentItemIdInput, function (nome) {
          applyProtocoloItemMae(nome, pkAtual);
        });
      }, 0);
    });

    /** **P-orq.3 / I5** — chamada explícita após syncHierarchyFromCode */
    window.applyClassificationNamingAfterParentResolved = function (
      parentPk,
      nomeMaeFromApi
    ) {
      var pk = String(parentPk || '').trim();
      var nome = String(nomeMaeFromApi || '').trim();
      if (!pk || !nome) return;
      var pkMudou = ultimoParentPkAplicado !== pk;
      var nomeMudou = nomeMae && !nomeMaeIgual(nomeMae, nome);
      if (!pkMudou && !nomeMudou && ultimoParentPkAplicado === pk) {
        return;
      }
      applyProtocoloItemMae(nome, pk);
    };

    receitaNomeInput.addEventListener('input', function () {
      receitaNomeInput.setCustomValidity('');
      clearReceitaNomeMessages(receitaNomeInput);
      removeTopErrorNote(adminForm);
      refreshReceitaNomeSugestaoInfoMensagem();
    });

    window.setTimeout(function () {
      if (
        (parentItemIdInput.value || '').trim() &&
        !(receitaNomeInput.value || '').trim()
      ) {
        scheduleApplyFromParentLookupLabel(
          parentItemIdInput,
          applyProtocoloItemMae
        );
      }
    }, 0);

    window.validateClassificationNamingOnSubmit =
      function validateClassificationNamingOnSubmit() {
        if (!isAddMode || !receitaNomeInput) return true;
        var nomeAtual = (receitaNomeInput.value || '').trim();

        /** **G0.3** — obrigatório no add, independente do rádio */
        if (!nomeAtual) {
          var vazioMsg = msgs.receita_nome_vazio_error || '';
          receitaNomeInput.setCustomValidity(vazioMsg);
          showReceitaNomeError(receitaNomeInput, vazioMsg);
          showTopErrorNote(adminForm, 'Por favor, corrija o erro abaixo.');
          return false;
        }

        var mode = getBaseMode();
        if (mode === 'sem_base' || !mode) {
          receitaNomeInput.setCustomValidity('');
          clearReceitaNomeMessages(receitaNomeInput);
          removeTopErrorNote(adminForm);
          return true;
        }
        ensureNomeMaeFromUi();
        var b = radicalEfetivoGuardrail();
        if (!b) {
          receitaNomeInput.setCustomValidity('');
          clearReceitaNomeMessages(receitaNomeInput);
          removeTopErrorNote(adminForm);
          return true;
        }
        if (b && receitaNomeEhSugestaoIncompleta(nomeAtual, b)) {
          var nomeMsg = msgs.receita_nome_submit_incompleto_error || '';
          receitaNomeInput.setCustomValidity(nomeMsg);
          showReceitaNomeError(receitaNomeInput, nomeMsg);
          showTopErrorNote(adminForm, 'Por favor, corrija o erro abaixo.');
          return false;
        }
        receitaNomeInput.setCustomValidity('');
        clearReceitaNomeMessages(receitaNomeInput);
        removeTopErrorNote(adminForm);
        return true;
      };
  };
})();
