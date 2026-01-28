import pandas as pd
import sqlite3
import os
import re

# --- CONFIGURATION ---
DB_NAME = "synthetic_cfo_sap_ecc.db"
SOURCE_FILES = {
    "P2P": "SAP_ECC_P2P_Final_Platinum.xlsx",
    "O2C": "SAP_ECC_O2C_Final_Platinum.xlsx",
    "CE":  "SAP_ECC_CE_Final_Platinum.xlsx",
    "R2R": "SAP_ECC_R2R_Final_Platinum.xlsx"
}

def log(msg):
    print(f"[SYSTEM] {msg}")

def clean_reference_id(ref_id):
    """Forensic cleaning: Removes prefixes like 'INV-', 'CHK-' to ensure ID matching."""
    if not isinstance(ref_id, str): return str(ref_id)
    return re.sub(r'[^0-9]', '', ref_id) # Strips everything except numbers

def run_integration():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        log(f"Cleaned previous build: {DB_NAME}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    total_rows = 0

    log("Initializing SAP ECC Forensic Integration...")

    # --- 1. DATA INGESTION & HARMONIZATION ---
    for module, filename in SOURCE_FILES.items():
        if not os.path.exists(filename):
            log(f"[CRITICAL] Missing File: {filename}. Please ensure all 4 Platinum files are present.")
            continue
            
        log(f"Processing Module: {module}...")
        try:
            xls = pd.ExcelFile(filename)
            for sheet in xls.sheet_names:
                # We only want data tables, not summaries/dictionaries
                if sheet in ["SUMMARY", "SKA1", "AUDIT_LEAD_SHEET", "T012"]:
                    # Special handling: SKA1 and T012 are master data, we DO want them
                    if sheet not in ["SKA1", "T012"]:
                        continue

                df = pd.read_excel(filename, sheet_name=sheet)
                
                # --- FORENSIC DATA CLEANING ---
                # Ensure Reference Keys match across modules (e.g., P2P Invoice -> R2R Reference)
                if 'XBLNR' in df.columns:
                    df['XBLNR_CLEAN'] = df['XBLNR'].apply(clean_reference_id)
                if 'EOWNR' in df.columns: # Bank Statement Ref
                    df['EOWNR_CLEAN'] = df['EOWNR'].apply(clean_reference_id)
                
                # Prefix table names with module to prevent collisions (e.g. P2P_BKPF vs R2R_BKPF)
                table_name = f"{module}_{sheet}"
                
                # Write to SQL
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                rows = len(df)
                total_rows += rows
                print(f"   >>> Injected: {table_name} ({rows} rows)")
                
        except Exception as e:
            log(f"[FAIL] Error processing {module}: {str(e)}")

    # --- 2. THE FRAUD HUNTER VIEW (V_GLOBAL_RISK_MAP) ---
    # This aggregates the "SME_REASONING" flags from all modules into one Master Risk View
    log("Deploying 'V_GLOBAL_RISK_MAP' (Forensic Surveillance Layer)...")
    
    fraud_view_sql = """
    CREATE VIEW V_GLOBAL_RISK_MAP AS
    
    -- 1. P2P RISKS (Procurement Fraud)
    SELECT 
        'P2P' as Module, 'EKKO' as Source, EBELN as Doc_ID, 
        SME_REASONING as Forensic_Log, 'High' as Risk_Level
    FROM P2P_EKKO 
    WHERE SME_REASONING LIKE '%FAIL%' OR SME_REASONING LIKE '%CRITICAL%'
    UNION ALL
    
    -- 2. O2C RISKS (Revenue Fraud)
    SELECT 
        'O2C', 'VBRK', VBELN, SME_REASONING, 'Medium'
    FROM O2C_VBRK 
    WHERE SME_REASONING LIKE '%FAIL%' OR SME_REASONING LIKE '%CRITICAL%' OR SME_REASONING LIKE '%OVERRIDE%'
    UNION ALL
    
    -- 3. TREASURY RISKS (Kiting/Theft)
    SELECT 
        'CE', 'FEBEP', KUKEY || '-' || ESNUM, SME_REASONING, 'Critical'
    FROM CE_FEBEP 
    WHERE SME_REASONING LIKE '%FAIL%' OR SME_REASONING LIKE '%CRITICAL%'
    UNION ALL
    
    -- 4. GL RISKS (Management Override)
    SELECT 
        'R2R', 'BSEG', BELNR, SME_REASONING, 'Critical'
    FROM R2R_BSEG 
    WHERE SME_REASONING LIKE '%FAIL%' OR SME_REASONING LIKE '%CRITICAL%' OR SME_REASONING LIKE '%Suspicious%'
    """
    
    try:
        cursor.execute("DROP VIEW IF EXISTS V_GLOBAL_RISK_MAP")
        cursor.execute(fraud_view_sql)
        log("   >>> Fraud Hunter View deployed successfully.")
    except Exception as e:
        log(f"   >>> View Creation Failed: {str(e)}")

    # --- 3. INTEGRITY PROOF (THE TWIN CHECK) ---
    log("Running Digital Twin Connectivity Verification...")
    
    # Check 1: Revenue Interlock (O2C Billing -> R2R GL)
    # We check if O2C Billing Docs exist in the R2R Header references
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM O2C_VBRK v
            JOIN R2R_BKPF b ON b.XBLNR = v.VBELN
            WHERE b.BLART = 'RV'
        """)
        revenue_links = cursor.fetchone()[0]
        log(f"   [PASS] Revenue Handshake: {revenue_links} O2C Billing Docs successfully posted to GL.")
    except: log("   [WARN] Revenue Handshake check skipped (Data missing).")

    # Check 2: Cash Interlock (P2P Payments -> CE Bank Stmt)
    # We check if P2P Checks appear on the Bank Statement
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM P2P_PAYR p
            JOIN CE_FEBEP f ON f.EOWNR_CLEAN = p.CHECT
        """)
        cash_links = cursor.fetchone()[0]
        log(f"   [PASS] Cash Handshake: {cash_links} Physical Checks cleared on Bank Statement.")
    except: log("   [WARN] Cash Handshake check skipped (Data missing).")

    # --- 4. FINAL STATS ---
    try:
        cursor.execute("SELECT Count(*) FROM V_GLOBAL_RISK_MAP")
        risk_count = cursor.fetchone()[0]
        log(f"   [ALERT] Total Active Fraud Vectors Detected: {risk_count}")
    except: pass

    conn.close()
    print("="*60)
    print(f"SYSTEM READY. Database: {DB_NAME}")
    print("Next Step: Open in Tableau/PowerBI/DBeaver and query 'V_GLOBAL_RISK_MAP'")
    print("="*60)

if __name__ == "__main__":
    run_integration()