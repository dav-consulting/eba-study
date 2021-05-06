import pycountry

# import country_converter as coco


## hard coded translation Swedish to English for converting eba2017 dataset.
_EBA_SWE_TO_ENG = {
    "Ukraina": "Ukraine",
    "Uganda": "Uganda",
    "Colombia": "Colombia",
    "Indonesien": "Indonesia",
    "Tanzania": "Tanzania",
    "Georgien": "Georgia",
    "Bosnia": "Bosnia",
    "Sydafrika": "South Africa",
    "Indien": "India",
    "Bangladesh": "Bangladesh",
    "Thailand": "Thailand",
    "Brasilien": "Brazil",
    "Kambodja": "Cambodia",
    "Kosovo": "Kosovo",
    "Zambia": "Zambia",
    "Egypten": "Egypt",
    "Irak": "Iraq",
    "Jordanien": "Jordan",
    "Libanon": "Lebanon",
    "Libyen": "Libya",
    "Marocko": "Morocco",
    "Palestina": "Palestine",
    "Syrien": "Syria",
    "Tunisien": "Tunisia",
    "Yemen": "Yemen",
    "Kenya": "Kenya",
    "Burundi": "Burundi",
    "Rwanda": "Rwanda",
    "En mängd länder globalt": "A lot of countries globally",
    "Kongo": "Congo",
    "Etiopien": "Ethiopia",
    "Somalia": "Somalia",
    "Sudan": "Sudan",
    "Algeriet": "Algeria",
    "Fillippinerna": "Philippines",
    "Malawi": "Malawi",
    "Liberia": "Liberia",
    "Haiti": "Haiti",
    "Makedonien": "Macedonia",
    "Nepal": "Nepal",
    "DRC": "DRC",
    "Ghana": "Ghana",
    "Gambia": "Gambia",
    "Sverige": "Sweden",
    "Kina": "China",
    "Albanien": "Albania",
    "Zimbabwe": "Zimbabwe",
    "Armenien": "Armenia",
    "Azerbajdzjan": "Azerbaijan",
    "Moldavien": "Moldova",
    "Vitryssland": "Belarus",
    "Guinea": "Guinea",
    "Kongo DRC": "Congo",
    "Kongo DCR": "Congo",
    "Swaziland": "Eswatini",
    "Democratic Republic of Congo": "Congo",
    "DRC": "Congo",
    "Kongo Democratic Republic": "Congo",
    "Sierra Leone": "Sierra Leone",
    "India": "India",
    "Bolivia": "Bolivia",
    "Botswana": "Botswana",
    "Burkina Faso": "Burkina Faso",
    "Kongo (DCR)": "Congo (DCR)",
    "Mali": "Mali",
    "Mozambique": "Mozambique",
    "Myanmar": "Myanmar",
    "Namibia": "Namibia",
    "Vietnam": "Vietnam",
    "Sri Lanka": "Sri Lanka",
    "Pakistan": "Pakistan",
    "Turkiet": "Turkey",
    "Bosnien och Hercegovina": "Bosnia and Herzegovina",
    "Bosnia and Hecergovina": "Bosnia and Herzegovina",
    "Serbien": "Serbia",
    "Estland": "Estonia",
    "Lettland": "Latvia",
    "Litauen": "Lithuania",
    "Ryssland": "Russia",
    "Afghanistan": "Afghanistan",
    "Östtimor": "Timor",
    "Timor Est": "Timor",
    "Libyen Benin": "Libya and Benin",
    "Elfenbenskusten": "Côte d'Ivoire",
    "Guinée-Bissau": "Guinee Bissau",
    "Kap Verde": "Cabo Verde",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "Senegal": "Senegal",
    "Togo": "Togo",
    "Angola": "Angola",
    "Djibouti": "Djibouti",
    "Ethiopia": "Ethiopia",
    "Lesotho": "Lesotho",
    "Mauritius": "Mauritius",
    "South Africa": "South Africa",
    "South Sudan": "South Sudan",
    "Zambia and Zimbabwe": "Zambia and Zimbabwe",
    "Cambodia": "Cambodia",
    "Serbia": "Serbia",
    "18 afrikanska länder": "18 African countries",
    "Egypt": "Egypt",
    "Ett flertal länder globalt": "Several countries globally",
    "Bosnien och Hecergovina": "Bosnia and Herzegovina",
    "Montenegro": "Montenegro",
    "Laos": "Laos",
    "Benin": "Benin",
    "Cameroon": "Cameroon",
    "Ethiopien": "Ethiopia",
    "Kongo (Democratic Republic)": "Congo",
    "Morocko": "Morocco",
    "……mfl": "Others",
    "Bosnien": "Bosnia",
    "och Hercegovina": "and Herzegovina",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Bosnia and Hecergovina": "Bosnia and Herzegovina",
    "Kroatien": "Croatia",
    "Moldovien": "Moldova",
    "Israel": "Israel",
    "Guinea-Bissau": "Guinea-Bissau",
    "Yemen Mozambique": "Yemen and Mozambique",  ## added to handle outlier
    "Mail": "Mali",  ## added to handle outlier
}
_NON_COUNTRIES = [
    "Others",
    "Several countries globally",
    "18 African countries",
    "A lot of countries globally",
    "……",
]

topics = {
    "Demokrati": ["Democracy"],
    "Mänskliga rättigheter": ["Human", "Rights"],
    "Jämställdhet": ["Gender", "Equality"],
    "Nationell, regional eller lokal förvaltning": [
        "National",
        "Regional",
        "local",
        "government",
    ],
    "Kultur": ["Culture"],
    "Marknad, företagande, handel, innovation": [
        "Market",
        "entrepreneurship",
        "trade",
        "innovation",
    ],
    "Jordbruk, skogsbruk, fiske samt landfrågor": [
        "Agriculture",
        "forestry",
        "fishing",
        "land",
    ],
    "Utbildning": ["Education"],
    "Forskning och högre utbildning": ["Research", "education"],
    "Humanitärt bistånd (analyseras i så fall ej i studien)": ["Humanitarian", "aid"],
    "Klimat": ["Climate"],
    "Övrig miljö inkl. vatten": ["environment", "water"],
    "Hälsa (inkl. SRHR)": ["Health"],
    "Konflikt, fred, säkerhet": ["Conflict", "peace", "security"],
    "Hållbar samhällsbyggnad och infrastruktur": [
        "Sustainable",
        "community",
        "infrastructure",
    ],
    "Flera områden i samma": [],
}

topic_similarities = {
    "Demokrati": [
        "democracy",
        "opposition",
        "independence",
        "political",
        "movement",
        "party",
        "dictatorship",
        "regime",
        "establishment",
        "solidarity",
    ],
    "Mänskliga rättigheter": [
        "human",
        "rights",
        "justice",
        "appeal",
        "civil",
        "constitution",
        "legitimate",
        "constitutional",
        "participation",
        "respect",
    ],
    "Jämställdhet": [
        "gender",
        "equality",
        "empowerment",
        "principles",
        "fairness",
        "virtue",
        "pluralism",
        "diversity",
        "norms",
        "advocating",
        "values",
    ],
    "Nationell, regional eller lokal förvaltning": [
        "national",
        "regional",
        "local",
        "government",
        "state",
        "union",
        "provincial",
        "administration",
        "officials",
        "power",
    ],
    "Kultur": [
        "culture",
        "tradition",
        "cultural",
        "modern",
        "religion",
        "traditional",
        "folklore",
        "contemporary",
        "literature",
        "art",
    ],
    "Marknad, företagande, handel, innovation": [
        "market",
        "entrepreneurship",
        "trade",
        "innovation",
        "prices",
        "economy",
        "trade",
        "business",
        "technology",
        "commerce",
    ],
    "Jordbruk, skogsbruk, fiske samt landfrågor": [
        "agriculture",
        "forestry",
        "fishing",
        "land",
        "conservation",
        "farming",
        "husbandry",
        "crops",
        "husbandry",
        "territory",
    ],
    "Utbildning": [
        "education",
        "teaching",
        "schools",
        "learning",
        "student",
        "programs",
        "curriculum",
        "teachers",
        "universities",
        "institution",
    ],
    "Forskning och högre utbildning": [
        "research",
        "academic",
        "scientific",
        "science",
        "laboratory",
        "expert",
        "analysis",
        "specialist",
        "project",
        "clinical",
    ],
    "Humanitärt bistånd (analyseras i så fall ej i studien)": [
        "humanitarian",
        "aid",
        "relief",
        "peacekeeping",
        "refugees",
        "unicef",
        "u.n.",
        "assistance",
        "mission",
        "reconstruction",
    ],
    "Klimat": [
        "climate",
        "warming",
        "policy",
        "global",
        "change",
        "temperature",
        "implications",
        "weather",
        "atmosphere",
        "carbon",
    ],
    "Övrig miljö inkl. vatten": [
        "environment",
        "water",
        "dry",
        "groundwater",
        "reservoir",
        "rain",
        "ecology",
        "natural",
        "conservation",
        "clean",
    ],
    "Hälsa (inkl. SRHR)": [
        "health",
        "care",
        "medical",
        "prevention",
        "healthcare",
        "poor",
        "nutrition",
        "hospitals",
        "medicine",
        "patients",
    ],
    "Konflikt, fred, säkerhet": [
        "conflict",
        "peace",
        "security" "war",
        "fighting",
        "violence",
        "negotiations",
        "military",
        "defense",
        "terrorism",
    ],
    "Hållbar samhällsbyggnad och infrastruktur": [
        "sustainable",
        "community",
        "infrastructure",
        "development",
        "construction",
        "housing",
        "community",
        "facilities",
        "reconstruction",
        "rebuilding",
    ],
}

topic_similarity_words = {
    "Demokrati": ["democracy",],
    "Mänskliga rättigheter": ["human rights",],
    "Jämställdhet": ["gender equality",],
    "Nationell, regional eller lokal förvaltning": [
        "national, regional and local government",
    ],
    "Kultur": ["culture",],
    "Marknad, företagande, handel, innovation": [
        "market, entrepreneurship, trade and innovation",
    ],
    "Jordbruk, skogsbruk, fiske samt landfrågor": [
        "agriculture, forestry, fishing and land",
    ],
    "Utbildning": ["education, teaching and schools"],
    "Forskning och högre utbildning": ["research and higher education",],
    # "Humanitärt bistånd (analyseras i så fall ej i studien)": ["humanitarian aid",],
    "Klimat": ["climate change",],
    "Övrig miljö inkl. vatten": ["environment and water",],
    "Hälsa (inkl. SRHR)": ["sexual reproductive health and rights",],
    "Konflikt, fred, säkerhet": ["conflict, peace and security",],
    "Hållbar samhällsbyggnad och infrastruktur": [
        "sustainable societal development and infrastructure",
    ],
}

## functions for Q3-5
def translate_eba_countries(data):
    """translating eba countries/categories to english with lookup dict"""
    return [v for k, v in _EBA_SWE_TO_ENG.items() if k == data]


def convert_eba_country_names(data_series):
    """extracts country data from eba study and translates it to English and normalize it to pycountry/ISO3166 nomenclature
    Note that the method is evaluating the string in two steps:
    1: Assesses if the translated country is in py_country names
    2: if not in 1; lookup the translated woth with fuzzy lookup
    3: if not in 2; append att "Others" - basically all arbitraty categories in the eba data
    4: if not in 3, append as errors. 

    # input and output
    :param data_series: pandas serie.
    :param output: list of string/s relating to context-based categories and meta data:
        '1' according to evaluation step 1 above;
        '2' according to evaluation step 2 above;
        'Other' according to evaluation step 3 above;
        'non_matches'  according to evaluation step 4 above.
    
    :returns: string/s with country name/s
    """
    results = []
    countries = (
        data_series.replace(" and ", ", ")
        .replace(".", ", ")
        .replace("\n", ", ")
        .split(",")
    )

    for c in countries:
        c = c.strip()
        all_pycount_names = [country.name for country in pycountry.countries]
        country = c.strip()

        eng_country = translate_eba_countries(country)
        eng_country = eng_country[0] if len(eng_country) > 0 else country
        if eng_country in all_pycount_names:
            results.append(("1: ", eng_country))
        else:
            try:
                results.append(
                    (
                        "2: ",
                        [
                            country.name
                            for country in pycountry.countries.search_fuzzy(eng_country)
                        ][0],
                    )
                )
            except:
                results.append(("Other: ", eng_country))
        # except:
        #     results.append(("Non_match: ", country))

    final = []
    for i in results:
        if "Other" in i[0]:
            print(i)
        country = i[1] if i[1] not in _NON_COUNTRIES else "None"
        final.append(country.strip())

    return "; ".join(final)
