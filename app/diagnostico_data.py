PONTUACAO_MAXIMA = 24
DIAS_BLOQUEIO = 90

AREAS = [
    {
        "key": "habitos_mindset",
        "title": "Arquitetura de Hábitos e Mindset",
        "question": "Como é a sua relação psicológica com o dinheiro?",
        "options": [
            {
                "value": 0,
                "label": "Eu sempre ajo por impulso.",
                "feedback": "Pare! Você precisa dar o primeiro passo que é a consciência que sempre age por impulso.",
            },
            {
                "value": 1,
                "label": "Já iniciei estratégias de controle financeiro mas não dou continuidade.",
                "feedback": "Recomeçar é uma atitude que deve fazer parte dessa estratégia. Crie metas de tempo para ter disciplina. Ex: 90 dias de controle.",
            },
            {
                "value": 2,
                "label": "Atualmente uso sistemas de controle mas não sigo à risca o que foi determinado.",
                "feedback": "Identifique em detalhes o que sai do orçamento e crie um plano de ação para cada item.",
            },
            {
                "value": 3,
                "label": "Uso sistemas de controle financeiro e sou rigoroso no previsto/realizado.",
                "feedback": "Parabéns!! Você já possui o nível máximo nesse quesito!",
            },
        ],
    },
    {
        "key": "fluxo_caixa",
        "title": "Engenharia do Fluxo de Caixa Pessoal",
        "question": "Qual o seu nível de controle sobre as suas entradas e saídas mensais?",
        "options": [
            {
                "value": 0,
                "label": "Não faço ideia de quanto ganho ou gasto. Só vejo o saldo no fim do mês.",
                "feedback": "Atenção! Comece anotando pelo menos seus gastos fixos básicos deste mês.",
            },
            {
                "value": 1,
                "label": "Sei mais ou menos de cabeça, mas não anoto e quase sempre não sobra.",
                "feedback": "A memória engana. Registre as saídas no momento em que elas ocorrem.",
            },
            {
                "value": 2,
                "label": "Anoto tudo, mas não consigo fazer sobrar dinheiro com frequência.",
                "feedback": "Corte 10% dos gastos supérfluos identificados e direcione para o FINANÇAS+.",
            },
            {
                "value": 3,
                "label": "Tenho orçamento definido, sigo à risca e separo minha poupança no início do mês.",
                "feedback": "Excelente! Seu fluxo de caixa está dominado.",
            },
        ],
    },
    {
        "key": "gestao_passivos",
        "title": "Gestão Estratégica de Passivos (Dívidas)",
        "question": "Como você lida com cartões de crédito, empréstimos e parcelamentos?",
        "options": [
            {
                "value": 0,
                "label": "Estou no rotativo do cartão, cheque especial ou tenho dívidas em atraso.",
                "feedback": "Alerta vermelho! Sua prioridade é usar as dicas de renda extra para renegociar e quitar essas dívidas.",
            },
            {
                "value": 1,
                "label": "Pago as contas em dia, mas parcelo tudo que compro e comprometo a renda futura.",
                "feedback": "Tente passar 30 dias sem usar o cartão e foque em juntar o valor à vista.",
            },
            {
                "value": 2,
                "label": "Uso o cartão para benefícios, mas possuo financiamentos longos.",
                "feedback": "Analise se vale a pena usar o dinheiro guardado aqui para antecipar parcelas.",
            },
            {
                "value": 3,
                "label": "Não tenho dívidas de consumo; só uso capital de terceiros para alavancagem.",
                "feedback": "Impecável. Você entende a diferença entre dívida ruim e alavancagem.",
            },
        ],
    },
    {
        "key": "matematica_financeira",
        "title": "Matemática Financeira Prática",
        "question": "Qual o seu nível de compreensão sobre como o dinheiro e os juros se comportam no tempo?",
        "options": [
            {
                "value": 0,
                "label": "Não entendo como os juros funcionam, apenas pago o que me cobram.",
                "feedback": "Estude o conceito básico de Juros Compostos na aba 'Aprender'.",
            },
            {
                "value": 1,
                "label": "Sei a teoria dos juros compostos, mas não aplico a meu favor.",
                "feedback": "Use o simulador do tabuleiro para visualizar seu dinheiro rendendo.",
            },
            {
                "value": 2,
                "label": "Entendo de juros/inflação e avalio bem rendimentos de mercado.",
                "feedback": "Teste aportes decrescentes no simulador para otimizar rendimentos reais.",
            },
            {
                "value": 3,
                "label": "Domino o valor do dinheiro no tempo e calculo o custo de oportunidade.",
                "feedback": "Brilhante! Sua lógica matemática já trabalha a seu favor.",
            },
        ],
    },
    {
        "key": "geracao_caixa",
        "title": "Máquinas de Geração de Caixa (Receita Extra)",
        "question": "Como você se posiciona em relação à criação de novas fontes de renda?",
        "options": [
            {
                "value": 0,
                "label": "Dependo 100% de uma fonte e não sei fazer dinheiro extra.",
                "feedback": "Vá para Dicas de Renda Extra e escolha o roteiro 'Geração de Renda Imediata'.",
            },
            {
                "value": 1,
                "label": "Já tentei fazer 'bicos' esporádicos, sem método estruturado.",
                "feedback": "Transforme esforços em processo. Dedique 2 horas semanais a uma habilidade.",
            },
            {
                "value": 2,
                "label": "Tenho fontes de renda extra consistentes, mas dependem do meu tempo físico.",
                "feedback": "O desafio agora é buscar modelos escaláveis, como produtos digitais.",
            },
            {
                "value": 3,
                "label": "Possuo múltiplas fontes, algumas escaláveis e com receita automática.",
                "feedback": "Sensacional! Sua máquina de geração de caixa é uma realidade sólida.",
            },
        ],
    },
    {
        "key": "alocacao_ativos",
        "title": "Alocação Estratégica de Ativos",
        "question": "Como você guarda, investe e protege o dinheiro que poupa?",
        "options": [
            {
                "value": 0,
                "label": "Deixo na conta corrente normal do bancão ou na poupança.",
                "feedback": "Abra conta num banco digital que pague mais de 100% do CDI.",
            },
            {
                "value": 1,
                "label": "Rende em contas digitais, mas não tenho Reserva de Emergência.",
                "feedback": "Separe um valor de 3 a 6 meses do seu custo de vida apenas para emergências.",
            },
            {
                "value": 2,
                "label": "Tenho reserva e invisto, mas sem estratégia clara de portfólio.",
                "feedback": "Estude sobre correlação de ativos e diversifique entre Renda Fixa e Variável.",
            },
            {
                "value": 3,
                "label": "Portfólio diversificado, balanceado e alinhado aos meus objetivos.",
                "feedback": "Perfeito! Sua alocação reflete a blindagem de um investidor maduro.",
            },
        ],
    },
    {
        "key": "negocios_equity",
        "title": "Análise de Negócios e Equity",
        "question": "Como você enxerga a participação em negócios para multiplicar capital?",
        "options": [
            {
                "value": 0,
                "label": "Focado apenas no meu trabalho atual, nunca pensei em ser sócio.",
                "feedback": "Comece consumindo conteúdos básicos sobre como empresas operam e geram lucro.",
            },
            {
                "value": 1,
                "label": "Tenho vontade de empreender, mas falta conhecimento prático.",
                "feedback": "Estude sobre precificação e margem de lucro. Teste algo pequeno.",
            },
            {
                "value": 2,
                "label": "Entendo de negócios, mas atuo em escala local e restrita ao meu tempo.",
                "feedback": "Crie processos ou marcas que tenham valor de mercado e funcionem sem você operar.",
            },
            {
                "value": 3,
                "label": "Visão de investidor/fundador; sei escalar operações focado em valuation.",
                "feedback": "Visão de mestre! Você domina o topo da cadeia de geração de riqueza.",
            },
        ],
    },
    {
        "key": "eficiencia_tributaria",
        "title": "Eficiência Tributária e Proteção Patrimonial",
        "question": "Qual a sua estratégia para proteger patrimônio e otimizar impostos?",
        "options": [
            {
                "value": 0,
                "label": "Pago os impostos padrão e nunca pensei em blindar patrimônio.",
                "feedback": "O primeiro passo é entender como funciona a sua declaração de Imposto de Renda.",
            },
            {
                "value": 1,
                "label": "Faço a declaração certa, mas sinto que pago muito imposto.",
                "feedback": "Pesquise ferramentas legais como PGBL ou abertura de CNPJ.",
            },
            {
                "value": 2,
                "label": "Uso estruturas simples, mas não tenho planejamento sucessório.",
                "feedback": "Entenda como funcionam seguros de vida e custos de inventário no Brasil.",
            },
            {
                "value": 3,
                "label": "Estrutura fiscal otimizada e planejamento sucessório definido.",
                "feedback": "Nível Elite. Você sabe exatamente as regras para manter o dinheiro seguro.",
            },
        ],
    },
]

AREAS_BY_KEY = {area["key"]: area for area in AREAS}
