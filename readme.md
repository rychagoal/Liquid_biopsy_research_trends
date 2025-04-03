# 🧬 Liquid Biopsy Research Trends — PubMed Analysis Project

This project analyzes global trends in **liquid biopsy research** based on PubMed abstracts, using custom parsing, data analytics, and upcoming interactive visualizations in Tableau.

## 🌐 Context (as of 2025)

As of 2025, **liquid biopsy** has become a rapidly evolving field in precision oncology, enabling non-invasive detection of cancer biomarkers such as ctDNA, CTCs, and exosomes. Research interest continues to grow, especially in relation to early cancer detection, monitoring treatment response, and minimal residual disease.

This project explores:
- Which **keywords** are most used in publications over time
- What **cancer types** are most studied with liquid biopsy methods
- Which **journals** lead in publishing this research
- Whether there is **growth or decline** in research activity

---

## 📊 Project Overview

We use the NCBI PubMed API to extract relevant article metadata, perform data cleaning and EDA, and export cleaned datasets for use in Tableau dashboards (to be added).

## 📁 Project Structure

```
├── data_analytics/
│   └── EDA.py                       # Exploratory data analysis and visuals
│
├── upload_data/
│   ├── output.csv                   # Raw parsed records
│   ├── clean_data.csv               # Filtered and cleaned abstracts
│   ├── journals.csv                 # Top journals by year
│   ├── keywords.csv                 # Keyword frequencies over time
│   ├── cancer_types.csv             # Cancer types extracted from abstracts
│
├── get_summary.py                   # Async parser from PubMed using EFetch API
├── requirements.txt                 # Python libraries used
├── README.md                        # You are here
```

## 🧪 Key Features of the Analysis

- 9,500+ parsed publications (up to December 2024)
- Yearly trends in research activity since 2010
- Identification of top **journals** and **keywords**
- Detection of most frequently studied **cancer types**
- Exported structured data for dashboard building

## 📈 Tableau Dashboard

> 🧩 A Tableau dashboard is currently under development and will be added here.

## ▶️ How to Run the Parser

```bash
python get_summary.py --term "liquid biopsy"
```

> ⚠️ Due to NCBI restrictions, please run the parser on weekends or between 9 PM–5 AM EST.

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 📊 Libraries Used

- `pandas`, `matplotlib`, `seaborn`
- `httpx`, `asyncio`, `xml.etree`, `tqdm`

---

## 👩‍🔬 Author

**Tamara Rychagova**  
📧 rychagovatam@gmail.com  
🌍 Serbia (Novi Sad)  
🔗 [LinkedIn](https://www.linkedin.com/in/tamara-rychagova-51524893)
