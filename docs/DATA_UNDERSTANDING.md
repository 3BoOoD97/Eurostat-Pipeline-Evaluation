# Data Understanding Report

## 1. Eurostat Datasets
Eurostat is the statistical office of the European Union (EU) located in Luxembourg. The data comes from national administrative records in each country. It collects migration and asylum statistics from national administrative records in each Member State. Countries are obligated to send this data to Eurostat under European Regulation 862/2007 on Migration and International Protection Statistics. Eurostat aggregates this data and calculates the European totals using a standardized method. Therefore, the accuracy is very high because it is based on official records, although some countries may apply slight rounding or have minor delays in reporting.

---

## 2. Selected Datasets

### 2.1 Asylum applicants by type, citizenship, age and sex - annual aggregated data (migr_asyappctza)
This table contains annual aggregated data about asylum applicants in European Union countries and other countries (Iceland, Liechtenstein, Norway, Switzerland, Montenegro, Croatia, Montenegro, and United Kingdom until November 2020), broken down by citizenship, age group, sex, and type of application. From 2008 to 2025 (latest available data).

After cleaning and filtering, the table contains 261,085 rows, 13 main columns, and the size is ~13 MB.

#### Variables Description
* **Freq:** Frequency (A = Annual)
* **Unit:** Unit of measure (PER = Person)
* **Citizen:** The nationality of the asylum seeker in (ISO 3166 alpha-2 code)
* **Sex:** The asylum seeker’s sex (T = Total, M = Male, F = Female, UNK = Unknown)
* **Applicant:** Applicant types: First time applicant (FRST), Subsequent applicant (SSEQ), TOTAL (FRST + SSEQ)
* **Age:** The asylum seeker’s age (TOTAL, Y_LT14, Y14-17, Y_LT18, Y18-34, Y35-64, Y_GE65, UNK)
* **Geo/time:** The country where the asylum application was submitted including EU27_2020 (The total number of asylum applications in the 27 European countries (excluding Britain))
* **time columns:** Multiple columns from 2008 to 2025 (Last year)

#### How will it be used in the project?
It allows us to study asylum trends over time (long-term), compare countries, and build forecasting models.

#### Key findings
* It contains some "UNK" (Unknown) values in sex, age, and citizen.
* Minor rounding in totals.

---

### 2.2 Asylum applicants by type, citizenship, age and sex - monthly data (migr_asyappctzm)
This dataset contains the same information as the annual table (migr_asyappctza) but at a monthly frequency. The time period is from January 2008 to the last month currently available (March 2026).

After cleaning and filtering, the total number of rows is 3,233,089, 13 main columns, and the size is ~174 MB.

#### Variables Description
Same as the annual table, with the following changes:
* `~` **Freq:** Frequency (M = Monthly)
* `~` **time columns:** Monthly columns (From January 2008 to the last month currently available - March 2026)

#### How will it be used in the project?
migr_asyappctza gives us an overview, while migr_asyappctzm complements it by allowing us to see monthly changes and short-term fluctuations in asylum applications. This helps in building accurate time-based analyses and future forecasting models.

#### Key findings
* It contains some "UNK" (Unknown) values in sex, age, and citizen.
* Minor rounding in totals.
* The data is detailed and up-to-date.
* The table is significantly larger than the annual table due to monthly breakdowns.

---

### 2.3 First instance decisions on applications by type of decision, citizenship, age and sex - annual aggregated data (migr_asydcfsta)
This table contains information about applications in the first instance (decisions) like: How many were accepted as refugees? How many were rejected? How many received subsidiary protection? etc.

After cleaning and filtering, there are 694,419 rows, 12 main variables, and the table size is ~35 MB.

#### Variables Description
Same as the annual and monthly tables, with some differences as following:
* `~` **Freq:** Frequency (A = Annual)
* `+` **Decision:** * `NEG`: Application rejected
  * `POS`: Application accepted (any type of protection)
  * `POS_RFG`: Refugee status granted
  * `POS_SPROT`: Subsidiary protection granted
  * `POS_HUM`: Humanitarian status granted
  * `TOTAL`: Total of all decisions
* `-` **Applicant**

#### How will it be used in the project?
It allows us to calculate recognition rates and compare the number of applications with the number of positive and negative decisions.

#### Key findings
* It contains some "UNK" (Unknown) values in sex and age.

---

### 2.4 First-time asylum applicants - per thousand persons (migr_asyapp1mp)
This table contains normalized data showing the number of first-time asylum applications per 1,000 inhabitants in each country. It is an aggregated and adjusted indicator.

After cleaning and filtering, it contains 517 rows, 9 main variables, and the size is ~0.02 MB.

#### Variables Description
Same as the annual table, with the following changes:
* `~` **Unit:** Unit of measure (NR = Number)
* `-` **Citizen**
* `-` **Sex**
* `-` **Applicant**
* `-` **Age**

#### How will it be used in the project?
It enables fair comparisons between countries of different population sizes, supports comparative mapping, and helps analyze the relative migration pressure on each country.

#### Key findings
* The data is very small compared to other tables we have.
* No missing values.