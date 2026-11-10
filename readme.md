🧬 Genetic Admixture Modelling Pipeline (qpAdm)

An auditable workflow for South Asian genetic ancestry modelling using qpAdm and ADMIXTOOLS.**

 1\. Overview

The **Genetic Admixture Modelling Pipeline** is a Python-based research project designed to organise and automate the preparation, execution, and reporting of genetic admixture analysis.

The pipeline takes consumer DNA raw data, prepares it for analysis, merges it with reference populations from the **Allen Ancient DNA Resource (AADR)**, and runs statistical models using the classic qpAdm method.

The primary objective is to make the analysis process more transparent by recording model configurations, dataset information, statistical results, execution logs, and rejected or failed runs.

Rather than introducing a new ancestry estimation algorithm, this project provides an auditable workflow around existing population genetics tools.

 2\. Key Features

- **DNA Data Preparation:** Converts supported consumer DNA data into formats required for genetic analysis.
- **Reference Dataset Integration:** Uses PLINK and ADMIXTOOLS utilities to prepare and merge reference datasets.
- **SNP Quality Reporting:** Records SNP counts and provides information about dataset preparation.
- **Model Configuration:** Defines target populations, source populations, and outgroups.
- **qpAdm Execution:** Runs classic single-model qpAdm analysis.
- **Result Parsing:** Extracts ancestry coefficients, standard errors, and statistical p-values.
- **Run Tracking:** Maintains a ledger of successful, failed, and rejected model runs.
- **Visual Reporting:** Generates descriptive ancestry coefficient plots.

## 3\. Workflow Architecture

The pipeline follows a sequence of data preparation, statistical modelling, and result reporting stages.

### Step 1 – Raw DNA Input

The workflow accepts supported consumer DNA raw-data files, including files following the 23andMe format.

The input data is prepared for conversion before reference integration.

### Step 2 – PLINK Conversion

PLINK is used to convert the supported raw DNA file into a format suitable for downstream processing.

Example:

``` bash
plink --23file my_raw_data.txt \
      --make-bed \
      --out MySample
```

### Step 3 – EIGENSTRAT Conversion

The prepared dataset is converted into EIGENSTRAT format using ADMIXTOOLS `convertf`.

The resulting files include:

- `.geno` – Genotype data
- `.snp` – SNP information
- `.ind` – Individual information

### Step 4 – Reference Dataset Merging

The prepared sample is merged with the selected AADR reference dataset using `mergeit`.

This stage prepares the combined dataset for qpAdm analysis.

### Step 5 – SNP Quality Reporting

The pipeline records SNP counts after dataset preparation.

This information helps inspect the available genetic markers before statistical modelling.

### Step 6 – qpAdm Model Definition

The user specifies:

- Target population
- Source populations
- Right populations (outgroups)
- SNP handling options
- Analysis phase

### Step 7 – Statistical Analysis

The pipeline executes classic qpAdm using the configured model and records the execution details.

### Step 8 – Result Processing

The parser extracts model coefficients, standard errors, and p-values.

The pipeline records the outcome and generates a descriptive coefficient plot.

---

## 4\. Ancestry Model

The current exploratory model focuses on three broad ancestry-related components used in South Asian population genetics.

| Component | Reference proxy | Interpretation |
| --- | --- | --- |
| AASI-related | Onge / AHG | Imperfect proxy for ancient South Asian hunter-gatherer-related ancestry |
| Indus Periphery-related | Indus Periphery | Related to ancestry with Iranian-related and South Asian-related components |
| Steppe\_MLBA-related | Steppe MLBA | Related to Middle-to-Late Bronze Age Steppe ancestry |

These references are analytical proxies, not exact representations of unchanged ancestral populations.

The model is intended for statistical exploration and should not be interpreted as a definitive reconstruction of an individual's complete ancestry.

---

## 5\. Installation and Requirements

### Prerequisites

The following software and data are required:

| Requirement | Description |
| --- | --- |
| Python | Version 3.9 or later |
| PLINK | Version 1.9 |
| ADMIXTOOLS | `convertf`, `mergeit`, and `qpAdm` |
| AADR | Reference dataset in EIGENSTRAT format |
| Git | For repository cloning |

The AADR reference dataset must include its `.geno`, `.snp`, and `.ind` files.

Record the exact AADR release used for each analysis.

### Clone the Repository

``` bash
git clone https://github.com/AELIUS-22/qpAdm-notebook.git

cd qpAdm-notebook
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

### Verify the Installation

Run the available test suite:

``` bash
python -m pytest
```

External executable paths can be configured using:

- `--plink`
- `--convertf`
- `--mergeit`
- `--qpadm`

---

## 6\. Running the Pipeline

The project provides command-line operations for preparing data, executing models, and generating reports.

### A. Prepare the Dataset

Use the `prepare` command to convert the raw DNA file and prepare the reference dataset.

``` bash
python -m qpadm_pipeline prepare \
    --raw my_raw_data.txt \
    --sample-id MySample \
    --reference-prefix /path/to/aadr/v62.0_1240k_public
```

Replace the input file and reference path with your actual locations.

### B. Execute a qpAdm Model

Run the configured model:

``` bash
python -m qpadm_pipeline run \
    --config examples/example_config.json
```

### C. Generate a Report

Generate the descriptive ancestry coefficient plot:

``` bash
python -m qpadm_pipeline report \
    --out ancestry_plot.png
```

### D. Run Tests

``` bash
python -m pytest
```

---

## 7\. Model Configuration

The pipeline uses a JSON configuration file to define the statistical model.

Example configuration:

``` json
{
  "target": "MySample",
  "sources": [
    "Onge.DG",
    "Indus_Periphery_West",
    "Russia_Sintashta_MLBA"
  ],
  "right": [
    "Mbuti.DG",
    "Russia_Ust_Ishim.DG",
    "Russia_Kostenki14",
    "Han.DG"
  ],
  "allsnps": true,
  "phase": "exploratory"
}
```

### Configuration Parameters

| Parameter | Description |
| --- | --- |
| `target` | Sample being analysed |
| `sources` | Reference populations used in the model |
| `right` | Outgroup populations used for statistical testing |
| `allsnps` | SNP handling option passed to qpAdm |
| `phase` | Identifies the purpose of the model run |

The population names in this example are illustrative. Verify exact labels in the AADR `.ind` file before running an analysis.

The selection of right populations is an important part of the statistical hypothesis and requires scientific justification.

Use appropriate run labels such as `benchmark`, `sensitivity`, or `exploratory`.

---

## 8\. Project Structure

The repository is organised into separate modules for data preparation, model execution, parsing, and reporting.

``` text
qpAdm-notebook/
│
├── qpadm_pipeline/
│   ├── runner.py
│   ├── prepare.py
│   ├── model.py
│   ├── parse.py
│   ├── plot.py
│   └── cli.py
│
├── tests/
│
├── examples/
│   └── example_config.json
│
├── docs/
│   └── Auditable_qpAdm_Workflow_Indian_Cline.pdf
│
├── requirements.txt
└── README.md
```

### Main Modules

**`prepare.py`**

Handles the preparation and conversion of input genetic data.

**`runner.py`**

Coordinates execution of the configured qpAdm workflow.

**`model.py`**

Handles model configuration and associated model information.

**`parse.py`**

Extracts and processes statistical results from qpAdm output.

**`plot.py`**

Creates descriptive visualisations of model coefficients.

**`cli.py`**

Provides command-line access to pipeline operations.

---

## 9\. Output and Run Tracking

The pipeline stores intermediate datasets, model information, logs, and reports in its working directory.

Typical output structure:

``` text
work/
│
├── qc_report.json
├── run_ledger.jsonl
│
├── logs/
│
├── models/
│   └── <run_id>/
│       ├── left.txt
│       ├── right.txt
│       ├── qpadm.par
│       └── manifest.json
│
└── merged/
```

### Output Description

| Output | Purpose |
| --- | --- |
| `qc_report.json` | Records dataset quality information |
| `run_ledger.jsonl` | Maintains model execution history |
| `logs/` | Stores execution logs |
| `left.txt` | Records the model's left populations |
| `right.txt` | Records the model's right populations |
| `qpadm.par` | Stores qpAdm parameters |
| `manifest.json` | Stores model and dataset provenance |
| `merged/` | Contains prepared merged datasets |

Run identifiers are generated using SHA-256 hashes of model and dataset information.

This helps distinguish different configurations and dataset versions.

---

## 10\. Understanding Statistical Results

The pipeline extracts three important types of statistical information.

### Ancestry Coefficients

Coefficients represent estimated contributions from the selected source populations under the specified model.

### Standard Errors

Standard errors provide information about uncertainty in the estimated coefficients.

### P-values

The p-value helps evaluate whether the model is statistically rejected under the selected right-population configuration.

### Interpretation Guidelines

- A p-value greater than 0.05 means the model is not rejected at the 5% significance level. It does not prove that the model is historically correct.
- Multiple models can be statistically compatible with the same dataset.
- Rejected models may still produce coefficients, but those coefficients should not be presented as accepted ancestry estimates.
- Coefficients outside the 0–1 range are flagged as `infeasible_coefficients`.
- A high p-value does not establish that a model is the true historical explanation.
- Generated coefficient plots are descriptive visualisations, not independent statistical fit tests.

Model selection should be based on scientific justification and sensitivity analysis rather than choosing the most attractive ancestry proportions.

---

## 11\. Research Benchmark Data

The original project documentation includes literature-derived reference values for comparison.

These values were not newly generated by this repository. They are not state-wide population averages.

| Population | AASI-related | Indus Periphery-related | Steppe-related | P-value |
| --- | ---: | ---: | ---: | ---: |
| Ulladan Kerala | 61.9% | 35.7% | 2.4% | 0.2386 |
| Palliyar TN | 64.7% | 33.0% | 2.3% | 0.0337 |
| Irula TN | 57.3% | 40.1% | 2.5% | 0.2489 |
| Lohana Gujarat | 10.4% | 64.3% | 25.2% | 0.0517 |
| GujaratiA diaspora panel | 11.6% | 63.9% | 24.5% | 0.3449 |
| Yadav Rajasthan | 15.8% | 61.6% | 22.6% | 0.0765 |
| Brahmin Haryana | 18.2% | 57.2% | 24.6% | 0.4269 |
| Rajput Haryana | 20.3% | 58.4% | 21.2% | 0.0177 |
| Bhumihar Bihar | 20.7% | 52.7% | 26.6% | 0.0514 |
| Yadav UP | 17.3% | 61.4% | 21.3% | 0.2081 |
| Bhumihar UP | 23.4% | 53.2% | 23.4% | 0.0174 |
| Brahmin UP | 24.1% | 50.2% | 25.7% | 0.2591 |

Standard errors are not available in this benchmark table. Comparisons must account for the original study's samples, reference populations, and modelling choices.

---

## 12\. Development Status

The project currently contains an implemented research workflow alongside features that still require further development and validation.

### Implemented

- PLINK raw-data conversion.
- EIGENSTRAT conversion using `convertf`.
- Reference dataset merging using `mergeit`.
- SNP count reporting.
- Frozen model manifests.
- Deterministic run identifiers.
- Single-model classic qpAdm execution.
- Result parsing with tests.
- Failed and rejected run tracking.
- Descriptive coefficient plots with fit status.

### Planned or Not Yet Fully Validated

- Complete allele and strand harmonisation with per-reason SNP loss reporting.
- Batch and rotation scheduling.
- PCA integration.
- Matched benchmarking against direct ADMIXTOOLS execution.
- Repeat-run reproducibility tests.
- Parser validation across ADMIXTOOLS versions.
- Full audit of the deployed Streamlit application.

These features should not be considered complete or validated until the relevant implementation and testing are performed.

---

## 13\. Scientific Limitations

The results of genetic admixture modelling depend on the selected samples, reference populations, and statistical assumptions.

Important limitations include:

1. AASI-related ancestry is represented using imperfect proxies because a directly sequenced ancient AASI reference genome is not available for this model.
2. qpAdm non-rejection does not establish a unique population history.
3. Results depend on source and right-population selection.
4. Endogamy, founder effects, migration, and sex-biased demographic history can influence population patterns.
5. State-based or community-based population labels do not represent genetically homogeneous groups.
6. Autosomal ancestry summaries cannot determine Y-chromosome haplogroups.
7. Consumer DNA arrays may have limited SNP overlap with the AADR 1240K dataset.
8. Genetic, archaeological, linguistic, and oral-history evidence answer different research questions.

Genetic results should not be used to establish social hierarchy, cultural superiority, or the value of any population.

---

## 14\. Data Privacy

Genetic data is sensitive personal information. Proper data handling is essential.

- Never commit raw DNA files to a public repository.
- Do not upload private `.geno`, `.snp`, or `.ind` files.
- Keep the `work/` directory out of version control.
- Review `.gitignore` before pushing changes.
- Only use genetic datasets that you have permission to analyse and share.

---

## 15\. Research Documentation and References

For further information about the workflow and its research methodology, refer to the project documentation.

**Research Paper:** [Auditable qpAdm Workflow for the Indian Cline](<docs/Auditable_qpAdm_Workflow_Indian_Cline.pdf>)

### External Tools and Resources

- [ADMIXTOOLS](<https://github.com/DReichLab/AdmixTools>)
- [PLINK](<https://www.cog-genomics.org/plink/>)
- [Allen Ancient DNA Resource (AADR)](<https://reich.hms.harvard.edu/allen-ancient-dna-resource-aadr-downloadable-genotypes-present-day-and-ancient-dna-data>)

---

## 16\. Contributing

Contributions, technical feedback, and research suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a separate branch for your changes.
3. Implement your changes.
4. Run the available tests.
5. Submit a pull request describing your modifications.

Please maintain clear documentation, scientific transparency, and reproducible model configurations.

---

## 17\. License

This project is distributed under the **MIT License**.

Refer to the `LICENSE` file for the complete license terms.

---

**Project:** Genetic Admixture Modelling Pipeline (qpAdm)  
**Repository:** [AELIUS-22/qpAdm-notebook](<https://github.com/AELIUS-22/qpAdm-notebook>)

*Built to make genetic admixture modelling more transparent, organised, and auditabl*
