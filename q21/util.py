_FUND_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "assistance"},],
    [{"LEMMA": "contribution"},],
    [{"LEMMA": "donation"},],
    [{"LEMMA": "finance"},],
    [{"LEMMA": "financier"},],
    [{"LEMMA": "financial"},],
    [{"LEMMA": "financial"}, {"LEMMA": "effort"},],
    [{"LEMMA": "financial"}, {"LEMMA": "support"},],
    [{"LEMMA": "financial"}, {"LEMMA": "contribution"},],
    [{"LEMMA": "fund"},],
    [{"LEMMA": "funding"},],
    [{"LEMMA": "grant"},],
    [{"LEMMA": "longterm"}, {"LEMMA": "support"},],
    [{"LEMMA": "long"}, {"LOWER": "-"}, {"LEMMA": "term"}, {"LEMMA": "support"},],
]

_SUSTAINABILITY_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "financial"}, {"LEMMA": "sustainability"},],
    [{"LEMMA": "sustainability"},],
    [{"LEMMA": "sustainable"},],
    [{"LEMMA": "sustain"},],
    [{"LEMMA": "self"}, {"LOWER": "-"}, {"LEMMA": "sustain"},],
    [{"LEMMA": "self"}, {"LOWER": "-"}, {"LEMMA": "sustainability"},],
    [{"LEMMA": "donor"}, {"LEMMA": "-"}, {"LEMMA": "dependency"},],
    [{"LEMMA": "selffinancing"},],
    [{"LEMMA": "self"}, {"LOWER": "-"}, {"LEMMA": "financing."},],
]

_IMPORTANCE_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "critical"},],
    [{"LEMMA": "crucial"},],
    [{"LEMMA": "essential"},],
    [{"LEMMA": "important"},],
    [{"LEMMA": "importance"},],
    [{"LEMMA": "particular"},],
    [{"LEMMA": "significant"},],
    [{"LEMMA": "vital"},],
    [{"LEMMA": "need"}, {"LEMMA": "for"},],
    [{"LEMMA": "continued"},],
]
