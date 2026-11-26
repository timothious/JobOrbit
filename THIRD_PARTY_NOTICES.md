# Third-party notices

Reference data bundled in `backend/catalog/data/` (risk R-10, task T1.6).

| File | Content | Source | Licence |
|---|---|---|---|
| `countries.json` | ISO 3166-1 codes, names, official names | [pycountry](https://github.com/pycountry/pycountry), which packages the Debian [iso-codes](https://salsa.debian.org/iso-codes-team/iso-codes) data | LGPL-2.1-or-later |
| `countries.json` | Primary currency and official languages per country | [Unicode CLDR](https://cldr.unicode.org/), read through [Babel](https://babel.pocoo.org/) | Unicode License v3 |
| `countries.json`, `regions.json` | Region and subregion per country | [UN M49 standard](https://unstats.un.org/unsd/methodology/m49/) (UN Statistics Division), cross-checked against the [country_converter](https://github.com/IndEcol/country_converter) dataset | Classification facts; see source terms |
| `regions.json` | EU, EEA and GCC membership; derived groups (APAC, EMEA, LATAM, MENA, NA) | Curated in this repository | Project-owned |
| `skills.json` | Skills dictionary | Curated in this repository | Project-owned |

No immigration rules or country eligibility facts are bundled. Countries' `english_status` is
seeded as `unknown` and is curated by the user with evidence.
