import re
from typing import Tuple
from jasonutils.domain.value_objects import SearchOptions


class SearchEngine:
    """
    Инфраструктурный сервис для поиска и замены.
    Инкапсулирует всю логику построения паттернов и применения замен
    с учётом опций (regex, регистр, целые слова, лимит, направление).
    """
    def replace(
        self,
        content: str,
        search: str,
        replace: str,
        options: SearchOptions
    ) -> Tuple[str, int]:
        pattern = self._build_pattern(search, options)
        matches = list(pattern.finditer(content))
        if not matches:
            return content, 0
        if options.max_matches == 0:
            limit = len(matches)
        else:
            limit = min(options.max_matches, len(matches))
        if options.direction == "top_to_bottom":
            targets = matches[:limit]
        elif options.direction == "bottom_to_top":
            targets = matches[-limit:] if limit < len(matches) else matches
        else:
            raise ValueError(f"Неизвестное направление: {options.direction}")
        result = content
        for m in reversed(targets):
            if options.regex:
                replacement = m.expand(replace)
            else:
                replacement = replace
            result = result[:m.start()] + replacement + result[m.end():]
        return result, len(targets)

    def _build_pattern(self, search: str, options: SearchOptions) -> re.Pattern:
        if options.regex:
            pattern_str = search
        else:
            escaped = re.escape(search)
            if options.whole_words:
                pattern_str = r'\b' + escaped + r'\b'
            else:
                pattern_str = escaped
        flags = 0 if options.case_sensitive else re.IGNORECASE
        try:
            return re.compile(pattern_str, flags)
        except re.error as e:
            raise ValueError(f"Некорректное регулярное выражение: {e}")
