"""
Filtros de listagem do Django Admin específicos do app ``core``.

As fábricas genéricas ficam em ``admin_mixins``; aqui ficam apenas as classes
instanciadas para este domínio (IDs de negócio e FKs com rótulo semântico).
"""

from apps.core.admin_mixins import make_filter_fk_id, make_filter_local_id
from apps.core.models import Classificacao, NivelHierarquico


#---------------------------------------------------------------------------------------------------
# make_filter_local_id: campo de id na própria tabela da changelist

SerieIdFilter = make_filter_local_id("serie_id", title="Identificador da Série")
ClassificacaoIdFilter = make_filter_local_id("classificacao_id", title="Identificador da Classificação")
NivelIdFilter = make_filter_local_id("nivel_id", title="Identificador do Nível")
ItemIdFilter = make_filter_local_id("item_id", title="Identificador do Item")
VersaoIdFilter = make_filter_local_id("versao_id", title="Identificador da Versão")
VarianteIdFilter = make_filter_local_id("variante_id", title="Identificador da Variante")
BaseLegalTecnicaIdFilter = make_filter_local_id("base_legal_tecnica_id", title="Identificador da Base Legal/Técnica")

#---------------------------------------------------------------------------------------------------
# make_filter_fk_id: FK com rótulo semântico na sidebar (valor na URL = PK relacionada)

SerieIdFKFilter = make_filter_fk_id(Classificacao, "serie_id")
NivelIdFKFilter = make_filter_fk_id(NivelHierarquico, "classificacao_id"
)
