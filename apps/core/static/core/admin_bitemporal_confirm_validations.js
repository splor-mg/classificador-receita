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
    if (!cell) return '';
    var input = cell.querySelector('input');
    return input ? input.value.trim() : (cell.textContent || '').trim();
  }

  function validateVigenciaOnSubmit() {
    // Valida todos os pares início/fim de cada linha da tabela de preview
    // (incluindo "Versão atual", cujos inputs são readonly e sem name).
    // Regra: data de fim não pode ser anterior à data de início.
    var vigenciaInvalida = false;
    var rows = document.querySelectorAll('#preview-body tr');
    rows.forEach(function (tr) {
      var cells = tr.querySelectorAll('td');
      if (cells.length < 3) return;
      var inicioVal = getCellValue(cells[1]);
      var fimVal = getCellValue(cells[2]);
      if (!inicioVal || !fimVal) return;
      if (!isValidDateDMY(inicioVal) || !isValidDateDMY(fimVal)) return;
      var inicioDate = new Date(parseDMYtoISO(inicioVal));
      var fimDate = new Date(parseDMYtoISO(fimVal));
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

