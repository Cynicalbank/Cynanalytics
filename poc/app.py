import streamlit as st
import pandas as pd
import json
import time


# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="CYNALYTICS - PoC",
    page_icon="../assets/cyn.ico",
    layout="wide"
)


# ==========================================
# LÓGICA DO EXTRATOR E PIPELINE (CORE 1)
# ==========================================

def executar_extractor(blueprint):
    """
    Simula a validação e extração de dados conforme a fonte definida.
    Gera automaticamente os estados t0 e t1 fictícios baseados no ID do card.
    """
    time.sleep(0.5)  # Simula delay de rede/processamento

    # Validação simples
    if not blueprint["card_id"]:
        return False, "ID do Card inválido."

    # Mock de unidades e valores dinâmicos para novos cards
    novo_card = blueprint.copy()

    if blueprint["tipo"] == "custo":
        novo_card["estados"] = [
            {
                "timestamp": "t0",
                "valor": 0.0,
                "unidade": "brl"
            },
            {
                "timestamp": "t1",
                "valor": 1500.0,
                "unidade": "brl"
            }
        ]
    else:
        novo_card["estados"] = [
            {
                "timestamp": "t0",
                "valor": 10.0,
                "unidade": "horas"
            },
            {
                "timestamp": "t1",
                "valor": 2.0,
                "unidade": "horas"
            }
        ]

    return True, novo_card


def pipeline_core1(storage_cru):
    """
    Processa os dados brutos e normaliza para BRL anualizado
    para fins de cálculo de ROI.

    Esta é uma implementação simplificada baseada no comportamento
    esperado das regras de negócio.
    """

    resultados = {
        "IA_CHATBOT": {
            "ganho_brl": 0.0,
            "custo_brl": 0.0
        },
        "IA_RECOMMENDER": {
            "ganho_brl": 0.0,
            "custo_brl": 0.0
        },
        "PRICING_ENGINE": {
            "ganho_brl": 0.0,
            "custo_brl": 0.0
        }
    }

    # Regras de conversão estáticas/simuladas para a PoC
    for card in storage_cru:
        deck = card["deck_id"]

        if deck not in resultados:
            resultados[deck] = {
                "ganho_brl": 0.0,
                "custo_brl": 0.0
            }

        tipo = card["tipo"]

        # Simulação de cálculo financeiro de valor gerado
        # Exemplo: valor anualizado
        if tipo == "ganho":
            resultados[deck]["ganho_brl"] += 120000.0

        elif tipo == "custo":
            resultados[deck]["custo_brl"] += 35000.0

    # Calcular indicadores derivados para cada deck
    for deck, valores in resultados.items():
        ganho = valores["ganho_brl"]
        custo = valores["custo_brl"]

        roi = (ganho / custo) - 1.0 if custo > 0 else 0.0
        payback = (custo / ganho) * 12.0 if ganho > 0 else 0.0
        valor_liquido = ganho - custo

        valores["indicadores"] = {
            "ROI": roi,
            "Payback_Meses": payback,
            "Valor_Liquido": valor_liquido
        }

    return resultados


# ==========================================
# BANCO DE DADOS EM MEMÓRIA
# 5 MOCKS POR PRODUTO (CORE 0)
# ==========================================

if "storage_cru" not in st.session_state:
    st.session_state.storage_cru = [

        # ------------------------------------------
        # DECK: IA_CHATBOT
        # ------------------------------------------

        {
            "deck_id": "IA_CHATBOT",
            "card_id": "tempo_homologacao",
            "tipo": "ganho",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 5.0,
                    "unidade": "meses"
                },
                {
                    "timestamp": "t1",
                    "valor": 0.25,
                    "unidade": "meses"
                }
            ]
        },

        {
            "deck_id": "IA_CHATBOT",
            "card_id": "custo_infra_nuvem",
            "tipo": "custo",
            "fonte": "AWS Billing",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 0.0,
                    "unidade": "usd"
                },
                {
                    "timestamp": "t1",
                    "valor": 2500.0,
                    "unidade": "usd"
                }
            ]
        },

        {
            "deck_id": "IA_CHATBOT",
            "card_id": "tempo_atendimento_cliente",
            "tipo": "ganho",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 20.0,
                    "unidade": "minutos"
                },
                {
                    "timestamp": "t1",
                    "valor": 4.5,
                    "unidade": "minutos"
                }
            ]
        },

        {
            "deck_id": "IA_CHATBOT",
            "card_id": "licencas_software",
            "tipo": "custo",
            "fonte": "Financeiro Planilha",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 500.0,
                    "unidade": "brl"
                },
                {
                    "timestamp": "t1",
                    "valor": 1200.0,
                    "unidade": "brl"
                }
            ]
        },

        {
            "deck_id": "IA_CHATBOT",
            "card_id": "erros_triagem_manual",
            "tipo": "ganho",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 150.0,
                    "unidade": "erros_mes"
                },
                {
                    "timestamp": "t1",
                    "valor": 12.0,
                    "unidade": "erros_mes"
                }
            ]
        },

        # ------------------------------------------
        # DECK: IA_RECOMMENDER
        # ------------------------------------------

        {
            "deck_id": "IA_RECOMMENDER",
            "card_id": "conversao_vendas",
            "tipo": "ganho",
            "fonte": "Financeiro Planilha",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 2.1,
                    "unidade": "percentual"
                },
                {
                    "timestamp": "t1",
                    "valor": 4.8,
                    "unidade": "percentual"
                }
            ]
        },

        {
            "deck_id": "IA_RECOMMENDER",
            "card_id": "custo_infra_nuvem",
            "tipo": "custo",
            "fonte": "AWS Billing",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 0.0,
                    "unidade": "usd"
                },
                {
                    "timestamp": "t1",
                    "valor": 4200.0,
                    "unidade": "usd"
                }
            ]
        },

        {
            "deck_id": "IA_RECOMMENDER",
            "card_id": "tempo_processamento_rec",
            "tipo": "ganho",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 800.0,
                    "unidade": "ms"
                },
                {
                    "timestamp": "t1",
                    "valor": 120.0,
                    "unidade": "ms"
                }
            ]
        },

        {
            "deck_id": "IA_RECOMMENDER",
            "card_id": "manutencao_modelos_horas",
            "tipo": "custo",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 10.0,
                    "unidade": "horas_semana"
                },
                {
                    "timestamp": "t1",
                    "valor": 35.0,
                    "unidade": "horas_semana"
                }
            ]
        },

        {
            "deck_id": "IA_RECOMMENDER",
            "card_id": "churn_usuarios",
            "tipo": "ganho",
            "fonte": "Financeiro Planilha",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 5.0,
                    "unidade": "percentual"
                },
                {
                    "timestamp": "t1",
                    "valor": 2.2,
                    "unidade": "percentual"
                }
            ]
        },

        # ------------------------------------------
        # DECK: PRICING_ENGINE
        # ------------------------------------------

        {
            "deck_id": "PRICING_ENGINE",
            "card_id": "margem_lucro_media",
            "tipo": "ganho",
            "fonte": "Financeiro Planilha",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 12.5,
                    "unidade": "percentual"
                },
                {
                    "timestamp": "t1",
                    "valor": 15.3,
                    "unidade": "percentual"
                }
            ]
        },

        {
            "deck_id": "PRICING_ENGINE",
            "card_id": "custo_infra_nuvem",
            "tipo": "custo",
            "fonte": "AWS Billing",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 0.0,
                    "unidade": "usd"
                },
                {
                    "timestamp": "t1",
                    "valor": 1800.0,
                    "unidade": "usd"
                }
            ]
        },

        {
            "deck_id": "PRICING_ENGINE",
            "card_id": "tempo_recalculo_precos",
            "tipo": "ganho",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 24.0,
                    "unidade": "horas"
                },
                {
                    "timestamp": "t1",
                    "valor": 0.5,
                    "unidade": "horas"
                }
            ]
        },

        {
            "deck_id": "PRICING_ENGINE",
            "card_id": "suporte_operacional",
            "tipo": "custo",
            "fonte": "Jira Logs",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 40.0,
                    "unidade": "horas_mes"
                },
                {
                    "timestamp": "t1",
                    "valor": 15.0,
                    "unidade": "horas_mes"
                }
            ]
        },

        {
            "deck_id": "PRICING_ENGINE",
            "card_id": "perda_receita_precificacao",
            "tipo": "ganho",
            "fonte": "Financeiro Planilha",
            "estados": [
                {
                    "timestamp": "t0",
                    "valor": 45000.0,
                    "unidade": "brl_mes"
                },
                {
                    "timestamp": "t1",
                    "valor": 5000.0,
                    "unidade": "brl_mes"
                }
            ]
        }
    ]


# ==========================================
# TÍTULO PRINCIPAL DO DASHBOARD
# ==========================================

st.title("CYNALYTICS - Centro de Comando")


# ==========================================
# CONFIGURAÇÃO DAS ABAS DE NAVEGAÇÃO
# ==========================================

tab_criar, tab_analytics, tab_core1 = st.tabs(
    [
        "1. Criar Novo Card",
        "2. Core 0: Analytics do Deck",
        "3. Core 1: Dashboard de Valor (ROI)"
    ]
)


# ==========================================
# ABA 1: CRIAÇÃO DO CARD
# ==========================================

with tab_criar:

    st.subheader("Passo 1: Definir Assinatura Lógica da Carta")

    col1, col2 = st.columns(2)

    # ------------------------------------------
    # COLUNA 1: FORMULÁRIO
    # ------------------------------------------

    with col1:

        deck_id = st.selectbox(
            "Selecione o Deck (Produto):",
            [
                "IA_CHATBOT",
                "IA_RECOMMENDER",
                "PRICING_ENGINE"
            ]
        )

        card_id = st.text_input(
            "ID Técnico do Card (Ex: custo_infra_nuvem):",
            placeholder="custo_infra_nuvem"
        )

        tipo = st.radio(
            "Natureza da Métrica:",
            ["custo", "ganho"],
            horizontal=True
        )

        fonte = st.selectbox(
            "Fonte de Dados Indicada:",
            [
                "AWS Billing",
                "Jira Logs",
                "Financeiro Planilha"
            ]
        )

        pergunta = st.text_area(
            "Pergunta de Negócio:",
            placeholder="Qual o custo de infraestrutura mapeado?"
        )

        card_blueprint = {
            "deck_id": deck_id,
            "card_id": card_id,
            "tipo": tipo,
            "fonte": fonte,
            "estados": []
        }

    # ------------------------------------------
    # COLUNA 2: BLUEPRINT
    # ------------------------------------------

    with col2:

        st.markdown("#### Assinatura do Card Gerada (JSON BluePrint)")

        st.json(card_blueprint)

        if st.button(
            "Enviar para a Esteira do Extrator",
            type="primary"
        ):

            if not card_id:

                st.error(
                    "Por favor, informe o ID Técnico do Card."
                )

            else:

                sucesso, resultado = executar_extractor(
                    card_blueprint
                )

                if sucesso:

                    st.success(
                        "✅ Extrator Validou a Fonte! "
                        "Card anexado ao Storage Cru."
                    )

                    st.session_state.storage_cru.append(
                        resultado
                    )

                else:

                    st.error(
                        f"❌ {resultado}"
                    )


# ==========================================
# ABA 2: CORE 0
# ANALYTICS ENGINE
# ==========================================

with tab_analytics:

    st.subheader(
        "Analytics Engine: Estado Temporal dos Decks"
    )

    deck_selecionado = st.selectbox(
        "Filtrar visualização por Deck:",
        [
            "IA_CHATBOT",
            "IA_RECOMMENDER",
            "PRICING_ENGINE"
        ],
        key="filter_deck"
    )

    cartas_do_deck = [
        card
        for card in st.session_state.storage_cru
        if card["deck_id"] == deck_selecionado
    ]

    if not cartas_do_deck:

        st.info(
            "Nenhum card indexado para este deck."
        )

    else:

        linhas_tabela = []

        for card in cartas_do_deck:

            # Estado inicial
            if len(card["estados"]) > 0:

                v0 = card["estados"][0]["valor"]
                u0 = card["estados"][0]["unidade"]

            else:

                v0 = "N/A"
                u0 = ""

            # Estado atual
            if len(card["estados"]) > 0:

                v1 = card["estados"][-1]["valor"]
                u1 = card["estados"][-1]["unidade"]

            else:

                v1 = "N/A"
                u1 = ""

            linhas_tabela.append(
                {
                    "ID do Card": card["card_id"],
                    "Tipo": card["tipo"].upper(),
                    "Fonte Validada": card["fonte"],
                    "Estado Inicial (t0)": f"{v0} {u0}",
                    "Estado Atual (t1)": f"{v1} {u1}"
                }
            )

        df = pd.DataFrame(linhas_tabela)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# ABA 3: CORE 1
# DASHBOARD TOTAL INTEGRADO
# ==========================================

with tab_core1:

    dados_processados = pipeline_core1(
        st.session_state.storage_cru
    )

    # ------------------------------------------
    # SEÇÃO SUPERIOR:
    # PORTFÓLIO CONSOLIDADO GERAL
    # ------------------------------------------

    st.markdown(
        "### 1. Performance Consolidada Corporativa"
    )

    total_ganho = sum(
        valores["ganho_brl"]
        for valores in dados_processados.values()
    )

    total_custo = sum(
        valores["custo_brl"]
        for valores in dados_processados.values()
    )

    roi_geral = (
        (total_ganho / total_custo) - 1.0
        if total_custo > 0
        else 0.0
    )

    payback_geral = (
        (total_custo / total_ganho) * 12.0
        if total_ganho > 0
        else 0.0
    )

    vl_geral = total_ganho - total_custo

    # ------------------------------------------
    # GRID DE INDICADORES MACROS
    # ------------------------------------------

    g1, g2, g3 = st.columns(3)

    with g1:

        st.metric(
            label="ROI Global do Portfólio IA",
            value=f"{roi_geral * 100:.1f}%"
        )

    with g2:

        st.metric(
            label="Payback Médio do Portfólio",
            value=f"{payback_geral:.1f} Meses"
        )

    with g3:

        st.metric(
            label="Retorno Financeiro Líquido (Geral)",
            value=f"R$ {vl_geral:,.2f}"
        )

    st.markdown("---")

    # ------------------------------------------
    # SEÇÃO INFERIOR:
    # SUB-DASHBOARDS INDIVIDUAIS POR DECK
    # ------------------------------------------

    st.markdown(
        "###  2. Detalhamento Tático por Projeto (Decks)"
    )

    # Renderiza dinamicamente cada produto
    # em blocos organizados verticalmente

    for deck_name in [
        "IA_CHATBOT",
        "IA_RECOMMENDER",
        "PRICING_ENGINE"
    ]:

        if deck_name not in dados_processados:
            continue

        res = dados_processados[deck_name]
        indicadores = res["indicadores"]

        # Caixa estilizada para limpar o visual
        # e focar na auditoria

        with st.expander(
            f" Módulos de Valor: {deck_name}",
            expanded=True
        ):

            m1, m2, m3 = st.columns(3)

            # ------------------------------------------
            # ROI
            # ------------------------------------------

            with m1:

                st.metric(
                    label=f"ROI - {deck_name}",
                    value=f"{indicadores['ROI'] * 100:.1f}%"
                )

            # ------------------------------------------
            # PAYBACK
            # ------------------------------------------

            with m2:

                payback = indicadores["Payback_Meses"]

                st.metric(
                    label=f"Payback - {deck_name}",
                    value=(
                        f"{payback:.1f} Meses"
                        if payback > 0
                        else "Imediato"
                    )
                )

            # ------------------------------------------
            # VALOR LÍQUIDO
            # ------------------------------------------

            with m3:

                st.metric(
                    label=f"Valor Líquido - {deck_name}",
                    value=(
                        f"R$ "
                        f"{indicadores['Valor_Liquido']:,.2f}"
                    )
                )

            # ------------------------------------------
            # BALANÇO INTERNO DO CORE 1
            # ------------------------------------------

            col_g, col_c = st.columns(2)

            with col_g:

                st.text(
                    f"Ganho Anual (G): "
                    f"R$ {res['ganho_brl']:,.2f}"
                )

            with col_c:

                st.text(
                    f"Custo Anual (C): "
                    f"R$ {res['custo_brl']:,.2f}"
                )
