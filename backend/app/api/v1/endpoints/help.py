"""
Help/Documentation API Endpoints
"""

from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from pydantic import BaseModel

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Help article categories
HELP_CATEGORIES = {
    "getting_started": {"label": "Pierwsze kroki", "icon": "rocket"},
    "reports": {"label": "Raporty", "icon": "document"},
    "projects": {"label": "Projekty", "icon": "folder"},
    "search": {"label": "Wyszukiwanie", "icon": "search"},
    "alerts": {"label": "Alerty", "icon": "bell"},
    "settings": {"label": "Ustawienia", "icon": "cog"},
    "account": {"label": "Konto", "icon": "user"},
    "faq": {"label": "FAQ", "icon": "question"},
}


# Mock help articles
HELP_ARTICLES = [
    {
        "id": "help_001",
        "category": "getting_started",
        "title": "Wprowadzenie do MI-Navigator",
        "summary": "Dowiedz sie, jak rozpoczac prace z platforma MI-Navigator.",
        "content": """# Wprowadzenie do MI-Navigator

MI-Navigator to zaawansowana platforma do analizy rynkowej i wywiadu biznesowego.

## Glowne funkcje

- **Raporty firmowe** - Generuj kompleksowe analizy firm
- **Monitoring rynku** - Sledz zmiany na rynku w czasie rzeczywistym
- **Alerty** - Otrzymuj powiadomienia o waznych wydarzeniach
- **Projekty** - Organizuj swoje badania w projekty

## Pierwsze kroki

1. Przejdz do panelu glownego (Dashboard)
2. Uzyj paska wyszukiwania, aby znalezc firme
3. Wygeneruj raport lub dodaj firme do monitorowania

## Potrzebujesz pomocy?

Skontaktuj sie z nami: support@mi-navigator.pl""",
        "tags": ["wprowadzenie", "podstawy", "start"],
    },
    {
        "id": "help_002",
        "category": "reports",
        "title": "Tworzenie raportow firmowych",
        "summary": "Jak generowac i eksportowac raporty o firmach.",
        "content": """# Tworzenie raportow firmowych

## Typy raportow

- **Profil firmy** - Podstawowe informacje o firmie
- **Analiza rynku** - Analiza sektora i konkurencji
- **Due Diligence** - Kompleksowa analiza przed transakcja
- **Analiza konkurencji** - Porownanie z konkurentami

## Jak stworzyc raport

1. Wyszukaj firme w pasku wyszukiwania
2. Kliknij "Generuj raport"
3. Wybierz typ raportu
4. Poczekaj na wygenerowanie

## Eksport raportow

Raporty mozna eksportowac do formatow:
- PDF
- Word (DOCX)
- PowerPoint (PPTX)
- Excel (XLSX)""",
        "tags": ["raporty", "eksport", "generowanie", "pdf"],
    },
    {
        "id": "help_003",
        "category": "projects",
        "title": "Zarzadzanie projektami",
        "summary": "Organizacja badan w projekty i foldery.",
        "content": """# Zarzadzanie projektami

## Czym sa projekty?

Projekty pozwalaja grupowac raporty i badania tematycznie.

## Tworzenie projektu

1. Przejdz do zakladki "Projekty"
2. Kliknij "+ Nowy projekt"
3. Wprowadz nazwe i opis
4. Dodaj raporty do projektu

## Funkcje projektow

- Grupowanie raportow
- Wspoldzielenie z zespolem
- Notatki i komentarze
- Historia zmian""",
        "tags": ["projekty", "organizacja", "foldery", "zespol"],
    },
    {
        "id": "help_004",
        "category": "search",
        "title": "Wyszukiwanie firm i danych",
        "summary": "Jak efektywnie wyszukiwac informacje w systemie.",
        "content": """# Wyszukiwanie firm i danych

## Pasek wyszukiwania

Glowny pasek wyszukiwania umozliwia:
- Wyszukiwanie po nazwie firmy
- Wyszukiwanie po NIP/REGON/KRS
- Wyszukiwanie po kodzie PKD

## Zaawansowane wyszukiwanie

Uzyj filtrów, aby zawezic wyniki:
- Branza
- Region
- Wielkosc firmy
- Przychody

## Podpowiedzi

System podpowiada wyniki w trakcie pisania.""",
        "tags": ["wyszukiwanie", "filtrowanie", "NIP", "PKD"],
    },
    {
        "id": "help_005",
        "category": "alerts",
        "title": "Konfiguracja alertow",
        "summary": "Jak ustawic powiadomienia o zmianach.",
        "content": """# Konfiguracja alertow

## Typy alertow

- **Zmiany w firmie** - Zmiany w KRS, zarzadzie
- **Alerty cenowe** - Zmiany cen produktow
- **Aktywnosc konkurencji** - Nowe produkty, inwestycje
- **Zmiany rynkowe** - Trendy, regulacje

## Ustawienia alertow

1. Przejdz do ustawien
2. Wybierz "Alerty i powiadomienia"
3. Skonfiguruj preferowane kanaly
4. Zapisz zmiany""",
        "tags": ["alerty", "powiadomienia", "monitoring", "zmiany"],
    },
    {
        "id": "help_006",
        "category": "settings",
        "title": "Ustawienia konta",
        "summary": "Jak dostosowac ustawienia aplikacji.",
        "content": """# Ustawienia konta

## Profil uzytkownika

- Nazwa wyswietlana
- Branza
- Rola w firmie

## Preferencje

- Jezyk (Polski/English)
- Glebokosc analizy
- Format eksportu

## Powiadomienia

- Email
- W aplikacji""",
        "tags": ["ustawienia", "profil", "preferencje", "jezyk"],
    },
    {
        "id": "help_007",
        "category": "faq",
        "title": "Czesto zadawane pytania",
        "summary": "Odpowiedzi na najczesciej zadawane pytania.",
        "content": """# Czesto zadawane pytania (FAQ)

## Jak dlugo generuje sie raport?

Typowy raport generuje sie w 2-5 minut, w zaleznosci od zlozonosci.

## Czy moge eksportowac wiele raportow naraz?

Tak, uzyj funkcji "Eksport zbiorczy" w widoku raportow.

## Jak anulowac subskrypcje?

Przejdz do Ustawienia > Konto > Subskrypcja.

## Jak skontaktowac sie z supportem?

Email: support@mi-navigator.pl
Telefon: +48 22 123 45 67""",
        "tags": ["faq", "pytania", "pomoc", "kontakt"],
    },
    {
        "id": "help_008",
        "category": "reports",
        "title": "Adnotacje w raportach",
        "summary": "Jak dodawac komentarze i notatki do raportow.",
        "content": """# Adnotacje w raportach

## Dodawanie adnotacji

1. Otwórz raport
2. Zaznacz fragment tekstu
3. Kliknij "Dodaj komentarz"
4. Wpisz swoja notatke

## Widocznosc adnotacji

- Prywatne - tylko Ty widzisz
- Zespolowe - wspolpracownicy widza

## Zarzadzanie adnotacjami

Wszystkie adnotacje znajdziesz w panelu bocznym raportu.""",
        "tags": ["adnotacje", "komentarze", "notatki", "raporty"],
    },
]


class HelpArticleSummary(BaseModel):
    id: str
    category: str
    title: str
    summary: str
    tags: List[str]


class HelpArticleDetail(BaseModel):
    id: str
    category: str
    category_label: str
    title: str
    summary: str
    content: str
    tags: List[str]


class HelpSearchResponse(BaseModel):
    items: List[HelpArticleSummary]
    total: int
    query: str


class HelpCategoryInfo(BaseModel):
    id: str
    label: str
    icon: str
    article_count: int


@router.get("/articles")
async def list_help_articles(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List help articles with optional filtering."""
    filtered = HELP_ARTICLES.copy()

    # Filter by category
    if category:
        filtered = [a for a in filtered if a["category"] == category]

    # Filter by search query
    if search:
        search_lower = search.lower()
        filtered = [
            a for a in filtered
            if search_lower in a["title"].lower()
            or search_lower in a["summary"].lower()
            or any(search_lower in tag.lower() for tag in a["tags"])
        ]

    return HelpSearchResponse(
        items=[HelpArticleSummary(
            id=a["id"],
            category=a["category"],
            title=a["title"],
            summary=a["summary"],
            tags=a["tags"]
        ) for a in filtered],
        total=len(filtered),
        query=search or ""
    )


@router.get("/categories")
async def get_help_categories(current_user: User = Depends(get_current_user)):
    """Get help article categories with counts."""
    category_counts = {}
    for article in HELP_ARTICLES:
        cat = article["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    categories = []
    for cat_id, cat_info in HELP_CATEGORIES.items():
        categories.append(HelpCategoryInfo(
            id=cat_id,
            label=cat_info["label"],
            icon=cat_info["icon"],
            article_count=category_counts.get(cat_id, 0)
        ))

    return {"categories": categories}


@router.get("/articles/{article_id}")
async def get_help_article(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific help article."""
    for article in HELP_ARTICLES:
        if article["id"] == article_id:
            cat_info = HELP_CATEGORIES.get(article["category"], {})
            return HelpArticleDetail(
                id=article["id"],
                category=article["category"],
                category_label=cat_info.get("label", article["category"]),
                title=article["title"],
                summary=article["summary"],
                content=article["content"],
                tags=article["tags"]
            )

    return {"error": "Article not found"}
