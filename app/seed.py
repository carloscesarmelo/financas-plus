from sqlalchemy.orm import Session

from app.models import Desejo, LearningContent, Tip

INITIAL_DESEJOS = [
    {"emoji": "🏠", "label": "Apartamento", "headline": "Seu apartamento em 500 dias. Veja como.", "subheadline": "Descubra seu Score de Saúde Financeira e siga o Desafio Finanças500+ — poupança diária até a entrada do seu imóvel.", "plan_key": "financas500", "ordem": 1},
    {"emoji": "🚗", "label": "Carro novo", "headline": "Seu carro novo em 365 dias. Veja como.", "subheadline": "Siga o Desafio Finanças365+ até dar a entrada — ou pagar à vista — no seu carro novo.", "plan_key": "financas365", "ordem": 2},
    {"emoji": "✈️", "label": "Viagem dos sonhos", "headline": "Sua viagem dos sonhos em 100 dias. Veja como.", "subheadline": "Monte sua reserva de viagem com o Desafio Finanças100+, sem abrir mão do orçamento mensal.", "plan_key": "financas100", "ordem": 3},
    {"emoji": "🛟", "label": "Reserva de emergência", "headline": "Sua reserva de emergência em 50 dias. Veja como.", "subheadline": "Construa sua segurança financeira com o Desafio Finanças50+ antes de planejar o próximo passo.", "plan_key": "financas50", "ordem": 4},
    {"emoji": "🏥", "label": "Realizar uma Cirurgia", "headline": "Sua cirurgia realizada em 365 dias. Veja como.", "subheadline": "Organize seus recursos com o Desafio Finanças365+ e realize o procedimento que você precisa sem depender de terceiros.", "plan_key": "financas365", "ordem": 5},
    {"emoji": "💳", "label": "Quitar Dívidas", "headline": "Suas dívidas quitadas em 100 dias. Veja como.", "subheadline": "Siga o Desafio Finanças100+ e construa o fundo para zerar suas dívidas e recomeçar do zero.", "plan_key": "financas100", "ordem": 6},
    {"emoji": "🏦", "label": "Pagar Empréstimos", "headline": "Seus empréstimos pagos em 100 dias. Veja como.", "subheadline": "Com o Desafio Finanças100+, acumule o valor para quitar seus empréstimos e recuperar sua liberdade financeira.", "plan_key": "financas100", "ordem": 7},
    {"emoji": "💼", "label": "Capital para Empreender", "headline": "Seu capital de negócio em 365 dias. Veja como.", "subheadline": "Construa o capital inicial do seu negócio com o Desafio Finanças365+ — disciplina diária que vira o fundo que você precisa.", "plan_key": "financas365", "ordem": 8},
    {"emoji": "👶", "label": "Ter um bebê", "headline": "Preparado para seu bebê em 365 dias. Veja como.", "subheadline": "Organize suas finanças com o Desafio Finanças365+ para chegar nessa fase da vida com tranquilidade e segurança.", "plan_key": "financas365", "ordem": 9},
    {"emoji": "🏍️", "label": "Comprar uma Moto", "headline": "Sua moto nova em 365 dias. Veja como.", "subheadline": "Siga o Desafio Finanças365+ e junte o valor para comprar sua moto à vista ou dar uma entrada confortável.", "plan_key": "financas365", "ordem": 10},
    {"emoji": "🛋️", "label": "Mobília para casa", "headline": "Sua casa mobiliada em 100 dias. Veja como.", "subheadline": "Com o Desafio Finanças100+, acumule o valor para mobiliar sua casa sem parcelamento e sem dívidas.", "plan_key": "financas100", "ordem": 11},
    {"emoji": "🏊", "label": "Construir uma Piscina", "headline": "Sua piscina construída em 500 dias. Veja como.", "subheadline": "Realize esse sonho com o Desafio Finanças500+ — poupança consistente que transforma seu quintal.", "plan_key": "financas500", "ordem": 12},
    {"emoji": "💍", "label": "Cerimônia de Casamento", "headline": "Seu casamento dos sonhos em 500 dias. Veja como.", "subheadline": "Planeje a cerimônia perfeita com o Desafio Finanças500+ — sem comprometer o orçamento do novo lar.", "plan_key": "financas500", "ordem": 13},
    {"emoji": "🎉", "label": "Festa de Aniversário", "headline": "Sua festa inesquecível em 100 dias. Veja como.", "subheadline": "Com o Desafio Finanças100+, organize a comemoração que você merece sem apertar o orçamento.", "plan_key": "financas100", "ordem": 14},
    {"emoji": "🌍", "label": "Realizar Intercâmbio", "headline": "Seu intercâmbio em 365 dias. Veja como.", "subheadline": "Construa o fundo do seu intercâmbio com o Desafio Finanças365+ — idiomas e experiências que valem para sempre.", "plan_key": "financas365", "ordem": 15},
    {"emoji": "🎓", "label": "Quitar FIES", "headline": "Seu FIES quitado em 500 dias. Veja como.", "subheadline": "Siga o Desafio Finanças500+ e acumule o valor para quitar seu financiamento estudantil com total liberdade.", "plan_key": "financas500", "ordem": 16},
]

INITIAL_TIPS = [
    {
        "title": "Venda itens parados em casa",
        "description": (
            "Faça um raio-x dos seus armários, garagem e gavetas. Roupas, eletrônicos, móveis e "
            "livros que você não usa há mais de 6 meses podem se tornar dinheiro rápido em "
            "marketplaces como OLX, Enjoei e grupos de bairro no Facebook. Tire fotos boas, escreva "
            "um título claro e precifique de forma justa para vender rápido."
        ),
        "category": "Renda imediata",
    },
    {
        "title": "Ofereça um freelance com o que você já sabe fazer",
        "description": (
            "Liste 3 habilidades que você já domina (escrita, design, planilhas, edição de vídeo, "
            "aulas particulares, organização). Cadastre-se em plataformas como Workana, 99Freelas ou "
            "Fiverr e ofereça um serviço simples e rápido de entregar para conseguir os primeiros "
            "clientes e referências."
        ),
        "category": "Habilidades atuais",
    },
    {
        "title": "Comece a construir uma renda recorrente",
        "description": (
            "Escolha um formato de baixo custo para criar conteúdo ou produto digital recorrente: um "
            "perfil em uma rede social sobre um tema que você domina, um e-book curto, ou uma "
            "assinatura de um serviço simples. O objetivo é criar algo que continue gerando valor "
            "(e receita) com pouco esforço de manutenção."
        ),
        "category": "Ativos e renda recorrente",
    },
    {
        "title": "Use Inteligência Artificial para vender serviços",
        "description": (
            "Ferramentas de IA podem te ajudar a oferecer serviços como criação de textos, roteiros, "
            "artes para redes sociais, currículos e apresentações. Aprenda a usar bem uma ferramenta de "
            "IA generativa e ofereça esse serviço para pequenos negócios locais que não têm tempo ou "
            "conhecimento para fazer isso sozinhos."
        ),
        "category": "Inteligência Artificial",
    },
    {
        "title": "Compre para revender (arbitragem)",
        "description": (
            "Encontre produtos com bom desconto em liquidações, promoções ou compras em grupo, e "
            "revenda por um preço justo, ainda abaixo do mercado, para obter lucro rápido. Comece com "
            "pouco capital, valide a demanda antes de comprar em maior quantidade, e reinvista o lucro "
            "para crescer o capital de giro."
        ),
        "category": "Compra e venda",
    },
]

INITIAL_LEARNING_CONTENTS = [
    {
        "title": "Como organizar suas finanças pessoais do zero",
        "url": "https://www.youtube.com/results?search_query=organizar+financas+pessoais+do+zero",
        "content_type": "video",
        "level": "basico",
    },
    {
        "title": "O que é Selic, CDI e como isso afeta seu dinheiro",
        "url": "https://www.youtube.com/results?search_query=o+que+e+selic+cdi",
        "content_type": "artigo",
        "level": "basico",
    },
    {
        "title": "Renda fixa: Tesouro Direto, CDB e LCI/LCA",
        "url": "https://www.youtube.com/results?search_query=renda+fixa+tesouro+direto+cdb+lci+lca",
        "content_type": "video",
        "level": "intermediario",
    },
    {
        "title": "Como montar uma reserva de emergência",
        "url": "https://www.youtube.com/results?search_query=como+montar+reserva+de+emergencia",
        "content_type": "podcast",
        "level": "intermediario",
    },
    {
        "title": "Introdução à Bolsa de Valores e fundos de investimento",
        "url": "https://www.youtube.com/results?search_query=introducao+bolsa+de+valores+fundos+de+investimento",
        "content_type": "video",
        "level": "avancado",
    },
]


def run_seed(db: Session):
    if db.query(Tip).count() == 0:
        for tip in INITIAL_TIPS:
            db.add(Tip(**tip))

    if db.query(LearningContent).count() == 0:
        for content in INITIAL_LEARNING_CONTENTS:
            db.add(LearningContent(**content))

    if db.query(Desejo).count() == 0:
        for desejo in INITIAL_DESEJOS:
            db.add(Desejo(**desejo))

    db.commit()
