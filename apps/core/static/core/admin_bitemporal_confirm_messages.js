/**
 * Texto explicativo dinâmico na tela de confirmação bitemporal.
 * Atualiza o bloco #bitemporal-explicativo conforme a estratégia e as datas da tabela de vigência.
 */
(function (window, document) {
  'use strict';

  function isValidDateDMY(value) {
    if (!value) return true;
    var regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    var match = value.match(regex);
    if (!match) return false;
    var day = parseInt(match[1], 10);
    var month = parseInt(match[2], 10);
    var year = parseInt(match[3], 10);
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    var date = new Date(year, month - 1, day);
    return (
      date.getFullYear() === year &&
      date.getMonth() === month - 1 &&
      date.getDate() === day
    );
  }

  function parseDMYtoISO(dmyDate) {
    if (!dmyDate) return '';
    var parts = dmyDate.split('/');
    if (parts.length !== 3) return dmyDate;
    return parts[2] + '-' + parts[1] + '-' + parts[0];
  }

  function getCellValue(cell) {
    var input = cell ? cell.querySelector('input') : null;
    return input ? input.value.trim() : (cell ? (cell.textContent || '').trim() : '');
  }

  function updateMessage() {
    var container = document.getElementById('bitemporal-explicativo');
    if (!container) return;
    var selected = document.querySelector('input[name="edit_strategy"]:checked');
    if (!selected) return;

    var versaoAtualInicio = '';
    var versaoAtualFim = '';
    var novaInicio = '';
    var novaFim = '';
    var rows = document.querySelectorAll('#preview-body tr');
    rows.forEach(function (tr) {
      var cells = tr.querySelectorAll('td');
      if (cells.length < 3) return;
      var label = (cells[0].textContent || '').trim();
      if (label === 'Versão atual') {
        versaoAtualInicio = getCellValue(cells[1]);
        versaoAtualFim = getCellValue(cells[2]);
      } else if (label === 'Nova versão') {
        novaInicio = getCellValue(cells[1]);
        novaFim = getCellValue(cells[2]);
      }
    });

    var strategy = selected.value;
    var html = '';
    var alertas = [];

    var invalido = function (v) {
      return v && !isValidDateDMY(v);
    };

    if (strategy === 'nova_vigencia') {
      if (
        invalido(versaoAtualInicio) ||
        invalido(versaoAtualFim) ||
        invalido(novaInicio) ||
        invalido(novaFim)
      ) {
        alertas.push('Data inválida. Use o formato dd/mm/aaaa.');
      } else if (versaoAtualInicio || versaoAtualFim || novaInicio || novaFim) {
        html +=
          '<p>Será registrado que a versão atual teve vigência durante o período de <strong>' +
          (versaoAtualInicio || '—') +
          '</strong> a <strong>' +
          (versaoAtualFim || '—') +
          '</strong>.</p>';
        if (novaFim === '31/12/9999') {
          html +=
            '<p>A nova versão entrará em vigor em <strong>' +
            (novaInicio || '—') +
            '</strong>, sem prazo de fim de vigência estipulado.</p>';
        } else {
          html +=
            '<p>A nova versão entrará em vigor em <strong>' +
            (novaInicio || '—') +
            '</strong> até <strong>' +
            (novaFim || '—') +
            '</strong>.</p>';
        }
        if (
          novaInicio &&
          novaFim &&
          isValidDateDMY(novaInicio) &&
          isValidDateDMY(novaFim)
        ) {
          var di = new Date(parseDMYtoISO(novaInicio));
          var df = new Date(parseDMYtoISO(novaFim));
          if (df < di) {
            alertas.push(
              'Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.'
            );
          }
        }
        if (
          versaoAtualInicio &&
          versaoAtualFim &&
          isValidDateDMY(versaoAtualInicio) &&
          isValidDateDMY(versaoAtualFim)
        ) {
          var dai = new Date(parseDMYtoISO(versaoAtualInicio));
          var daf = new Date(parseDMYtoISO(versaoAtualFim));
          if (daf < dai) {
            alertas.push(
              'Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.'
            );
          }
        }
      }
    } else if (strategy === 'sobrescrever') {
      if (invalido(novaInicio) || invalido(novaFim)) {
        alertas.push('Data inválida. Use o formato dd/mm/aaaa.');
      } else if (novaInicio || novaFim) {
        var mesmaVigencia =
          versaoAtualInicio &&
          versaoAtualFim &&
          novaInicio === versaoAtualInicio &&
          novaFim === versaoAtualFim;

        var onlyVigenciaNode = document.getElementById('bitemporal-explicativo');
        var onlyVigenciaChanges =
          onlyVigenciaNode &&
          onlyVigenciaNode.getAttribute('data-only-vigencia-changes') === 'true';

        if (mesmaVigencia && onlyVigenciaChanges) {
          html +=
            '<p>Não foram detectadas alterações no período de vigência.</p>';
        } else if (mesmaVigencia && !onlyVigenciaChanges) {
          if (novaFim === '31/12/9999') {
            html +=
              '<p>As alterações realizadas na nova versão substituirão a versão atual e serão assumidas para o período com início de vigência em <strong>' +
              (novaInicio || '—') +
              '</strong>, sem prazo de fim de vigência estipulado.</p>';
          } else {
            html +=
              '<p>As alterações realizadas na nova versão substituirão a versão atual e serão assumidas para o período de <strong>' +
              (novaInicio || '—') +
              '</strong> a <strong>' +
              (novaFim || '—') +
              '</strong>.</p>';
          }
        } else if (novaFim === '31/12/9999') {
          html +=
            '<p>O período de vigência anterior será "excluído" (desativado) e substituído pelo novo período, que passa a ter início de vigência em <strong>' +
            (novaInicio || '—') +
            '</strong>, sem prazo de fim de vigência estipulado.</p>';
        } else {
          html +=
            '<p>O período de vigência anterior será "excluído" (desativado) e substituído pelo novo período, que passa a ter início de vigência em <strong>' +
            (novaInicio || '—') +
            '</strong>, indo até <strong>' +
            (novaFim || '—') +
            '</strong>.</p>';
        }
        if (
          novaInicio &&
          novaFim &&
          isValidDateDMY(novaInicio) &&
          isValidDateDMY(novaFim)
        ) {
          var di = new Date(parseDMYtoISO(novaInicio));
          var df = new Date(parseDMYtoISO(novaFim));
          if (df < di) {
            alertas.push(
              'Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.'
            );
          }
        }
      }
    }

    if (alertas.length) {
      html += '<div class="bitemporal-alerta">' + alertas.join(' ') + '</div>';
    }
    container.innerHTML = html || '';
  }

  function init() {
    var previewBody = document.getElementById('preview-body');
    if (previewBody) {
      previewBody.addEventListener('change', function (e) {
        if (
          e.target &&
          (e.target.matches('input.date-input') ||
            e.target.matches('input.date-input-readonly'))
        ) {
          updateMessage();
        }
      });
    }
  }

  window.bitemporalUpdateMessage = updateMessage;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window, document);
