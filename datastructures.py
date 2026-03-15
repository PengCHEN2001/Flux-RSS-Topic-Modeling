from dataclasses import dataclass, field

@dataclass
class Article:
    id: str
    source: str
    title: str
    content: str
    date: str
    categories: list[str] = field(default_factory=list)
    
'''
pour utiliser dans autre code :

from datastructures import Article

article = Article(
    id=guid,
    source=source_name,
    title=title,
    content=clean_content,
    date=date_str,
    categories=category_list
)

pour accéder à un element au lieu de faire article["date"], il faut faire article.date
'''