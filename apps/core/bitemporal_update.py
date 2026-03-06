"""
Serviço de atualização bitemporal (ADR-004).

Este módulo implementa as OPERAÇÕES de escrita sobre modelos bitemporais,
aplicando as regras de governança definidas na ADR-004. É o "executor"
que modifica o banco de dados segundo a política bitemporal.

DIFERENÇA ENTRE bitemporal_update.py e bitemporal_registry.py:

    bitemporal_registry.py (METADADOS / CONFIGURAÇÃO)
    --------------------------------------------------
    - Define QUAIS recursos são bitemporais e COMO estão estruturados
    - Contém o dicionário RESOURCES com metadados: campos, FKs, colunas de export
    - Funções de lookup: get_resource(), get_model_for_resource(), resolve_fk()
    - NÃO altera dados; apenas descreve a estrutura dos recursos
    - Usado por: comandos CLI, exporter, admin handlers

    bitemporal_update.py (LÓGICA DE NEGÓCIO / EXECUÇÃO)
    ---------------------------------------------------
    - Implementa a AÇÃO de atualização bitemporal (apply_bitemporal_update)
    - Aplica as regras: fechar registro anterior, criar novo registro
    - Gerencia transaction time (data_registro_*) e valid time (data_vigencia_*)
    - USA metadados do registry (get_sentinela_date) para executar operações
    - Usado por: admin handlers (BitemporalChangeHandler)

FLUXO DE UMA EDIÇÃO BITEMPORAL:
    1. Usuário edita no Admin e clica SAVE
    2. BitemporalChangeHandler detecta alterações
    3. Usuário escolhe estratégia (sobrescrever / nova vigência)
    4. Handler chama apply_bitemporal_update() deste módulo
    5. Serviço fecha registro anterior e cria novo registro
    6. AutoExportAdminMixin exporta CSV se houve mudança
"""
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from django.db import transaction
from django.utils import timezone

from apps.core.bitemporal_registry import get_sentinela_datetime


def apply_bitemporal_update(model, prev_obj, new_values: Dict[str, Any], strategy: str = "sobrescrever") -> Any:
    """
    Aplica a atualização segundo política bitemporal:

    SOBRESCREVER:
    - Encerra registro anterior (data_registro_fim = agora)
    - Cria 1 nova linha com os novos valores

    NOVA VIGÊNCIA:
    - Encerra registro anterior (data_registro_fim = agora)
    - Cria 2 novas linhas:
      1. Versão 1: cópia dos atributos anteriores, mas com data_vigencia_fim fechada
      2. Versão 2: novos atributos com nova vigência

    Se não houver data_vigencia_inicio em new_values para nova_vigencia,
    assume 1º de janeiro do ano atual.

    Retorna a nova instância criada (ou a Versão 2 no caso de nova_vigencia).
    """
    sentinela = get_sentinela_datetime()
    now = timezone.now()
    today = date.today()
    # Padrão de nova vigência: 1º de janeiro do ano corrente,
    # quando nenhuma data de início for explicitamente informada.
    first_jan_current_year = date(today.year, 1, 1)

    Model = model

    with transaction.atomic():
        prev = Model.objects.select_for_update().get(pk=prev_obj.pk)

        new_registro_inicio = now

        prev.data_registro_fim = new_registro_inicio
        prev.save(update_fields=["data_registro_fim"])

        base_data: Dict[str, Any] = {}
        for f in Model._meta.concrete_fields:
            name = f.name
            if name == Model._meta.pk.name:
                continue
            base_data[name] = getattr(prev, name)

        if strategy == "nova_vigencia":
            new_vig_inicio = new_values.get("data_vigencia_inicio", first_jan_current_year)
            prev_vig_fim_closed = new_vig_inicio - timedelta(days=1)

            version1_data = dict(base_data)
            version1_data["data_registro_inicio"] = new_registro_inicio
            version1_data["data_registro_fim"] = sentinela
            version1_data["data_vigencia_fim"] = prev_vig_fim_closed
            Model.objects.create(**version1_data)

            version2_data = dict(base_data)
            for k, v in new_values.items():
                version2_data[k] = v
            version2_data["data_registro_inicio"] = new_registro_inicio
            version2_data["data_registro_fim"] = sentinela
            if "data_vigencia_inicio" not in new_values:
                version2_data["data_vigencia_inicio"] = new_vig_inicio
            version2_data["data_vigencia_fim"] = sentinela

            new_obj = Model.objects.create(**version2_data)
        else:
            create_data = dict(base_data)
            for k, v in new_values.items():
                create_data[k] = v
            create_data["data_registro_inicio"] = new_registro_inicio
            create_data["data_registro_fim"] = sentinela

            new_obj = Model.objects.create(**create_data)

    return new_obj

