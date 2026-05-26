/**
 * Override de ``django/contrib/admin/static/admin/js/filters.js`` (Django 6+).
 *
 * Motivo: o script nativo persiste o estado abrir/recolher de cada
 * ``<details data-filter-title="...">`` em
 * ``sessionStorage["django.admin.filtersState"]`` e, no carregamento da
 * página, sobrescreve o atributo ``open`` que o servidor renderiza.
 *
 * Isso conflita com o protocolo declarativo deste projeto
 * (``ChangelistSidebarFilterCollapseMixin`` em ``apps/core/admin_mixins.py``),
 * que recomputa o estado a cada GET e exige que ele NÃO seja sobrescrito
 * pelo navegador (ver ``_dev/spec_django.md`` — «Estado inicial dos filtros
 * do sidebar»).
 *
 * Comportamento deste override:
 * - Não lê nem aplica ``sessionStorage`` no carregamento.
 * - Não persiste cliques de abrir/recolher (o estado vive apenas no DOM
 *   enquanto a página está aberta — comportamento padrão do ``<details>``).
 * - Limpa eventual estado residual previamente gravado por versões
 *   anteriores ou por outros admins.
 *
 * Resolução estática: ``apps.core`` está listado antes de
 * ``django.contrib.admin`` em ``INSTALLED_APPS`` (ver
 * ``classificador/settings.py``), portanto o
 * ``AppDirectoriesFinder`` devolve este ficheiro em vez do nativo.
 */
'use strict';
{
    try {
        sessionStorage.removeItem('django.admin.filtersState');
    } catch (e) {
        /* sessionStorage indisponível (cookies bloqueados, modo restrito, etc.) — ignorar. */
    }
}
