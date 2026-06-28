from sqlalchemy.orm import Session

from app.models import LearningContent, Tip

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

    db.commit()
