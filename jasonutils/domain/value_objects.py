from dataclasses import dataclass


@dataclass(frozen=True)
class SearchOptions:
    """
    Value Object: параметры поисковой операции.
    Иммутабельный объект, описывающий как выполнять поиск и замену.
    """
    regex: bool = False
    case_sensitive: bool = True
    whole_words: bool = False
    max_matches: int = 1  # 0 = без ограничений (заменить все)
    direction: str = "top_to_bottom"  # "top_to_bottom" | "bottom_to_top"
