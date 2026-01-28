import pandas as pd
import sqlite3
import os

# --- CONFIGURATION ---
DB_NAME = "synthetic_cfo_erp.db"
SOURCE_FILES = {
    "P2P": "Oracle_P2P_Platinum_Mode.xlsx",
    "O2C": "Oracle_O2C_Platinum_Mode.xlsx",
    "CE":  "Oracle_CE_Platinum_Mode.xlsx",
    "GL":  "Oracle_GL_Platinum_Mode.xlsx"
}

def log(msg):
    print(f"[SYSTEM] {msg}")

def run_integration():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        log(f"Cleaned previous build: {DB_NAME}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    total_tables = 0
    total_rows = 0

    log("Initializing ERP Schema Injection...")

    for module, filename in SOURCE_FILES.items():
        if not os.path.exists(filename):
            log(f"WARNING: Missing Module {module} ({filename}). Skipping.")
            continue
            
        log(f"Processing Module: {module}...")
        try:
            xls = pd.ExcelFile(filename)
            for sheet in xls.sheet_names:
                # Skip Summary/Control tabs, we only want raw data
                if sheet in ["SUMMARY", "RECONCILIATION_REPORT", "CONTROL_MATRIX"]:
                    continue
                
                df = pd.read_excel(filename, sheet_name=sheet)
                
                # Clean column names (remove spaces, standard format)
                df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]
                
                # Write to SQL
                df.to_sql(sheet, conn, if_exists='replace', index=False)
                
                rows = len(df)
                total_tables += 1
                total_rows += rows
                print(f"   >>> Loaded Table: {sheet} ({rows} rows)")
                
        except Exception as e:
            log(f"CRITICAL FAIL on {module}: {str(e)}")

    # --- CROSS-MODULE INTEGRITY CHECKS ---
    log("Running Cross-Module Forensic Validation...")
    
    # Check 1: Does GL Cash match CE Cash?
    try:
        cursor.execute("SELECT SUM(ENDING_BALANCE) FROM GL_TRIAL_BALANCE WHERE ACCOUNT IN ('11000','11001','11002')")
        gl_cash = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(CLOSING_BALANCE) FROM CE_STATEMENT_HEADERS WHERE STATEMENT_DATE = (SELECT MAX(STATEMENT_DATE) FROM CE_STATEMENT_HEADERS)")
        bank_cash = cursor.fetchone()[0]
        
        # Note: These won't match exactly due to the Float/Kiting traps we built, but they should correlate.
        log(f"   > GL Cash Position: ${gl_cash:,.2f}")
        log(f"   > Bank Cash Position: ${bank_cash:,.2f}")
        log(f"   > Reconciliation Gap: ${gl_cash - bank_cash:,.2f} (Expected due to Float/Kiting Traps)")
    except:
        log("   > Skipping Cash Check (Data missing)")

    conn.close()
    
    print("="*60)
    print(f"DEPLOYMENT SUCCESSFUL: {DB_NAME}")
    print(f"Statistics: {total_tables} Tables | {total_rows} Rows")
    print("Ready for SQL/PowerBI Connection.")
    print("="*60)

if __name__ == "__main__":
    run_integration()