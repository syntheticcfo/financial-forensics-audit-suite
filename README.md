# Financial Forensics Audit Suite (v1.0)

**Architect:** Axolile Lungu (Chartered Accountant & Financial Systems Architect)  
**Project Status:** Platinum Release  
**License:** Proprietary / Evaluation Only

---

## 1. Executive Summary

This repository contains the **Forensic Validation & Integration Logic** for the **Synthetic CFO** enterprise simulation engine. 

The **Synthetic CFO** project creates high-fidelity "Digital Twins" of major ERP environments (SAP ECC 6.0 and Oracle Cloud ERP). Unlike standard synthetic data which produces random noise, this engine simulates a fully relational, mathematically reconciled financial ledger with embedded fraud vectors designed for **AI Training** and **Forensic Audit Calibration**.

**Key Capabilities:**
* **Relational Integrity:** Enforces strict ERP schema logic (e.g., SAP Document Flow: `PO` -> `GR` -> `IR` -> `Payment`).
* **Forensic Injection:** Autonomously plants specific financial crimes (Kiting, SoD Conflicts, Phantom Billing) into the dataset.
* **Automated Auditing:** Python-based "Robotic Auditors" that detect and flag these anomalies.

---

## 2. Repository Architecture

This suite is organized by ERP Platform. Each module contains the **Integrator** (Database Builder) and the **Fraud Hunter** (Automated Auditor).

### 📂 `/sap_ecc_suite/` (SAP ECC 6.0)
* **Target Schema:** `BKPF` (Header), `BSEG` (Segment), `LFA1` (Vendor), `PAYR` (Payment).
* **`sap_erp_integrator.py`:** A Python ETL engine that ingests raw CSV modules (P2P, O2C, R2R, CE) and constructs a normalized SQLite relational database (`synthetic_cfo_sap_ecc.db`). It enforces foreign key constraints between the General Ledger and Sub-ledgers.
* **`sap_fraud_hunter.py`:** An automated forensic script that runs SQL logic to detect 30+ specific SAP fraud patterns, including:
    * **Cookie Jar Reserves:** Analyzing `BSEG-SME_REASONING` for manual month-end adjustments.
    * **Split Purchase Orders:** Detecting structural evasion in `EKKO` tables.
    * **3-Way Match Failures:** Validating `EKPO-MENGE` vs `EKPO-WEMNG`.

### 📂 `/oracle_cloud_suite/` (Oracle Cloud ERP)
* **Target Schema:** `AP_INVOICES_ALL`, `GL_JE_LINES`, `PO_HEADERS_ALL`.
* **`oracle_erp_integrator.py`:** Handles the ingestion of Oracle-specific datasets, managing the relationship between "Headers" and "Lines" standard in Oracle architecture.
* **`oracle_fraud_hunter.py`:** A specialized audit bot tuned for Oracle risk vectors:
    * **Kiting Schemes:** Detecting timing gaps in Cash Management (`CE_STATEMENT_LINES`).
    * **Phantom Vendors:** Cross-referencing Invoice Headers against Master Data.

### 📂 `/documentation/`
Contains the technical specifications and control manifests for the datasets.
* **`SAP_ECC_Digital_Twin_Whitepaper_v3.pdf`**: Detailed breakdown of the SAP table logic, chain of custody, and verified fraud counts (e.g., 284 P2P Mismatches, 13 Kiting Events).
* **`Oracle_Enterprise_Digital_Twin_Whitepaper.pdf`**: Specification for the Oracle Cloud simulation.

### 📂 `/data_samples/`
Contains structural samples (First 500 rows) of the Platinum datasets.
* **Purpose:** To allow Data Engineers to validate the schema, column types, and relational keys without requiring access to the full proprietary dataset.

---

## 3. Intellectual Property Notice

**Note on the Data Generation Engine:**
This repository hosts the **Client-Side Tools** (Integration & Auditing). 

The **Core Generation Engine** (the proprietary Python logic that parametrically generates the transaction topology, creates the fraud patterns, and balances the accounting equation) is hosted in a private, air-gapped repository to protect Intellectual Property.

The tools provided here demonstrate the **complexity** and **integrity** of the data produced by that engine.

---

## 4. Usage & Verification

**Note on Data Samples:**
The CSV files in `/data_samples/` contain the first **500 rows** of the Platinum dataset. This is a **Structural Sample** designed to validate the schema, column types, and relational keys.

Because the specific forensic injections (e.g., Kiting events, SoD conflicts) are distributed throughout the full transaction ledger, running the Audit Bot on the sample data will not reproduce the full fraud findings.

**How to Evaluate:**

1.  **Code Validation (The "How"):**
    Run the `*_integrator.py` and `*_fraud_hunter.py` scripts against the sample data.
    * *Result:* This proves the Python logic successfully ingests the schema, executes the SQL queries, and generates a formatted PDF report (likely showing "CLEAN" status due to sample size).

2.  **Outcome Validation (The "What"):**
    Review the pre-generated reports in `/documentation/`.
    * `SAP_ECC_Forensic_Audit_Report_Platinum.pdf`
    * *Result:* These are the actual outputs generated from the full proprietary dataset, showing the 300+ detected fraud vectors.
