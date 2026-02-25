"""
Serviço de atualização bitemporal (ADR-004).

Este módulo implementa as OPERAÇÕES de escrita sobre modelos bitemporais,
aplicando as regras de governança definidas na ADR-004. É o "executor"
que modifica o banco de dados segundo a política bitemporal.

DIFERENÇA ENTRE bitemporal_service.py e bitemporal_registry.py:

    bitemporal_registry.py (METADADOS / CONFIGURAÇÃO)
    --------------------------------------------------
    - Define QUAIS recursos são bitemporais e COMO estão estruturados
    - Contém o dicionário RESOURCES com metadados: campos, FKs, colunas de export
    - Funções de lookup: get_resource(), get_model_for_resource(), resolve_fk()
    - NÃO altera dados; apenas descreve a estrutura dos recursos
    - Usado por: comandos CLI, exporter, admin handlers

    bitemporal_service.py (LÓGICA DE NEGÓCIO / EXECUÇÃO)
    ----------------------------------------------------
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
from datetime import date, timedelta
from typing import Any, Dict, Optional

from django.db import transaction

from apps.core.bitemporal_registry import get_sentinela_date


def apply_bitemporal_update(model, prev_obj, new_values: Dict[str, Any], strategy: str = "sobrescrever") -> Any:
    """
    Aplica a atualização segundo política bitemporal:
    - Não altera dados históricos da linha anterior, apenas atualiza data_registro_fim para encerrar o registro anterior.
    - Cria nova linha com os novos valores, data_registro_inicio = hoje, data_registro_fim = sentinela.
    - Se strategy == "nova_vigencia" e 'data_vigencia_inicio' em new_values, registra fechamento da vigência anterior (ajusta data_vigencia_fim).

    Retorna a nova instância criada.
    """
    sentinela = get_sentinela_date()
    today = date.today()

    Model = model

    with transaction.atomic():
        # Reload previous object with FOR UPDATE to avoid races
        prev = Model.objects.select_for_update().get(pk=prev_obj.pk)

        # Determine new registro inicio (transaction time)
        new_registro_inicio = today

        # Close previous transaction-time
        prev.data_registro_fim = new_registro_inicio
        prev.save(update_fields=["data_registro_fim"])

        # Prepare data for new object: start from prev values, update with new_values
        create_data: Dict[str, Any] = {}
        for f in Model._meta.concrete_fields:
            name = f.name
            if name == Model._meta.pk.name:
                continue
            # take current value from prev
            create_data[name] = getattr(prev, name)

        # Override with provided new values from the form (they are already Python objects/instances)
        for k, v in new_values.items():
            create_data[k] = v

        # Set transaction-time for the new row
        create_data["data_registro_inicio"] = new_registro_inicio
        create_data["data_registro_fim"] = sentinela

        # Handle nova vigencia: if requested and data_vigencia_inicio provided, close previous valid_time
        if strategy == "nova_vigencia" and "data_vigencia_inicio" in new_values:
            new_vig_ini = new_values["data_vigencia_inicio"]
            # set previous valid_time end to day before new_vig_ini
            prev.data_vigencia_fim = new_vig_ini - timedelta(days=1)
            prev.save(update_fields=["data_vigencia_fim"])

        # Create the new row
        new_obj = Model.objects.create(**create_data)

    return new_obj

