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

  function validateVigenciaOnSubmit() {
    // Valida para ambas as estratégias: "Registrar nova vigência" e "Sobrescrever/ajustar".
    // Sempre checa a linha "Nova versão" na tabela de preview.
    var vigenciaInvalida = false;
    var rows = document.querySelectorAll('#preview-body tr');
    rows.forEach(function (tr) {
      var cells = tr.querySelectorAll('td');
      if (cells.length < 3) return;
      var label = (cells[0].textContent || '').trim();
      if (label !== 'Nova versão') return;
      var inicioInput = tr.querySelector('input[name^="edit_vig_inicio_"]');
      var fimInput = tr.querySelector('input[name^="edit_vig_fim_"]');
      if (!inicioInput || !fimInput || !inicioInput.value || !fimInput.value)
        return;
      if (
        !isValidDateDMY(inicioInput.value) ||
        !isValidDateDMY(fimInput.value)
      )
        return;
      var inicioIso = parseDMYtoISO(inicioInput.value);
      var fimIso = parseDMYtoISO(fimInput.value);
      var inicioDate = new Date(inicioIso);
      var fimDate = new Date(fimIso);
      if (fimDate < inicioDate) {
        vigenciaInvalida = true;
      }
    });

    if (vigenciaInvalida) {
      alert(
        'Data de Início de Vigência não pode ser anterior à Data de Fim de Vigência.'
      );
      return false;
    }

    return true;
  }

  window.bitemporalValidateVigenciaOnSubmit = validateVigenciaOnSubmit;
})(window, document);

