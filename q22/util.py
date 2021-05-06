# * donor countries to be labled in the parsing.
## list have been manualy adjusted to pycountry/ISO standards for country names.
## source: http://www.oecd.org/dac/dacmembers.htm/members
DONORS = [
    "Australia",
    "Austria",
    "Belgium",
    "Canada",
    "Czechia",
    "Denmark",
    "European Union",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Japan",
    "Korea, Republic of",
    "Luxembourg",
    "Netherlands",
    "New Zealand",
    "Norway",
    "Poland",
    "Portugal",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "United Kingdom",
    "United States",
]
_DAC_DONORS = [x.lower() for x in DONORS]

## aid donor organisations to be labled in the parsing.
# https://en.wikipedia.org/wiki/List_of_development_aid_agencies
_ORG_DONOR_LIST = [
    "aecid",
    "afd",
    "agci",
    "agência brasileira de cooperação",
    "agencia de cooperación internacional de chile",
    "amexcid",
    "aod",
    "ausaid",
    "australian department of foreign affairs and trade",
    "austria wirtschaftsservice gesellschaft",
    "austrian development agency",
    "azerbaijan international development agency",
    "belgian policy plan for development cooperation",
    "belgian technical cooperation",
    "belgium ministry of foreign affairs",
    "btc",
    "camões",
    "canadian international development agency",
    "china international development cooperation agency",
    "cida",
    "cidca",
    "comisión cascos blancos",
    "czda",
    "czech development agency",
    "danida",
    "danish international development agency",
    "dbsa",
    "department of foreign aid of the ministry of commerce",
    "deutsche gesellschaft für internationale zusammenarbeit",
    "development bank of southern africa",
    "dfid",
    "egyptian agency for partnership for development",
    "europeaid development and cooperation",
    "expertise france",
    "fcdo",
    "federal agency for the commonwealth of independent states",
    "finnida",
    "finnish international development agency",
    "foreign, commonwealth and development office",
    "french development agency",
    "giz",
    "global affairs canada",
    "hellenic ministry of foreign affairs",
    "helvetas",
    "icdf",
    "icdf",
    "idrc",
    "instituto da cooperação e da língua",
    "inter-american foundation",
    "international development research centre",
    "irish aid",
    "israel's agency for international development cooperation",
    "italian development cooperation programme",
    "japan bank for international cooperation",
    "japan international cooperation agency",
    "jbic",
    "jica",
    "kfw",
    "koica",
    "korea international cooperation agency",
    "kreditanstalt für wiederaufbau",
    "kuwait fund for arab economic development",
    "liechtensteinische entwicklungsdienst",
    "lux-development",
    "mashav",
    "mcc",
    "millennium challenge corporation",
    "mofcom",
    "netherlands foreign trade and development agency",
    "new zealand agency for international development",
    "nftda",
    "norad",
    "norwegian agency for development cooperation",
    "nzaid",
    "organization for investment, economic, and technical assistance of iran",
    "pakistan technical assistance programme",
    "palestinian international cooperation agenc",
    "pica",
    "rossotrudnichestvo",
    "saudi fund for development",
    "sdc",
    "sfd",
    "sida",
    "slovak aid",
    "spanish agency for international development cooperation",
    "the swedish international development cooperation agency",
    "the swedish international development and cooperation agency",
    "swedish international development and cooperation agency"
    "swedish international development cooperation agency",
    "swiss agency for development and cooperation",
    "thailand international cooperation agency",
    "tica",
    "tika",
    "turkish cooperation and coordination agency",
    "united states agency for international development",
    "usaid",
    "white helmets commission",
    "ebrd",
    "european bank for reconstruction and development",
    "european investment bank",
    "fao",
    "food and agriculture organization of the united nations",
    "iadb",
    "ibrd",
    "ifad",
    "ilo",
    "imf",
    "inter-american development bank",
    "international bank for reconstruction and development",
    "international fund for agricultural development",
    "international labour organization",
    "international monetary fund",
    "international organization for migration",
    "iom",
    "ocha",
    "unctad",
    "undp",
    "unep",
    "unfpa",
    "unhcr",
    "unicef",
    "unido",
    "united nations children's fund",
    "united nations conference on trade and development",
    "united nations development programme",
    "united nations environment programme",
    "united nations high commissioner for refugees",
    "united nations industrial development organization",
    "united nations office for the coordination of humanitarian affairs",
    "united nations population fund",
    "wfp",
    "who",
    "world bank",
    "world bank group",
    "world food programme",
    "world health organization",
    "world trade organization",
    "wto",
    "deutsche fördergemeinschaft",
    "dfg",
    "the swiss national research foundation",
    "european union",
    "un",
]

# * compilation of all donors with small letters.
_ALL_DONORS = _ORG_DONOR_LIST + _DAC_DONORS

_DONOR_DEPENDENCY_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "donors"}, {"LEMMA": "depend"},],
    [{"LEMMA": "donor"}, {"LEMMA": "dependency"},],
    [{"LEMMA": "donor"}, {"LOWER": "-"}, {"LEMMA": "dependency"},],
    [{"LEMMA": "dependent"}, {"LEMMA": "on"}, {"LEMMA": "donor"},],
    [{"LEMMA": "depend"}, {"LEMMA": "on"}, {"LEMMA": "donor"},],
    [{"LEMMA": "dependence"}, {"LEMMA": "on"}, {"LEMMA": "donor"},],
    [{"LEMMA": "dependency"}, {"LEMMA": "on"}, {"LEMMA": "donor"},],
]


_DEPENDENCY_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "depend"},],
    [{"LEMMA": "dependent"},],
    [{"LEMMA": "dependence"},],
    [{"LEMMA": "rely"}, {"LEMMA": "on"}, {"LEMMA": "support"},],
    [{"LEMMA": "rely"}, {"LEMMA": "on"}, {"LEMMA": "continue"},],
]


_DONOR_WORD_LEMMA_PATTERNS = [
    [{"LEMMA": "donor"},],
    [{"LEMMA": "donors"},],
    [{"LEMMA": "financiers"},],
    # [{"LEMMA": "sida"},],
    # [{"LEMMA": "sweden"},],
    # [{"LEMMA": "Swedish"}, {"LEMMA": "support"},],
    # [{"LEMMA": "funding"},],
    # [{"LEMMA": "fund"},],
    # [{"LEMMA": "financial"}, {"LEMMA": "support"},],
]

