import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION ---
DB_NAME = "synthetic_cfo_sap_ecc.db"
REPORT_FILE = "SAP_ECC_Forensic_Audit_Report_Platinum.pdf"

class AuditPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, 'synthetic cfo | AUTOMATED FORENSIC AUDIT BOT', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_heading(self, title, description):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(32, 55, 100) # Professional Blue
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  TEST: {title}", 0, 1, 'L', 1)
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 6, f"Scope: {description}")
        self.ln(2)

    def log_finding_table(self, df, status_msg):
        # TRAFFIC LIGHT LOGIC
        self.set_font('Arial', 'B', 10)
        
        if "FAIL" in status_msg or "CRITICAL" in status_msg:
            self.set_text_color(200, 0, 0) # RED
        elif "WARN" in status_msg:
            self.set_text_color(220, 110, 0) # ORANGE
        else:
            self.set_text_color(0, 128, 0) # GREEN
            
        self.cell(0, 6, f"STATUS: {status_msg}", 0, 1, 'L')
        self.set_text_color(0, 0, 0) # Reset
        self.ln(2)

        if not df.empty:
            self.set_font('Courier', '', 8)
            self.set_fill_color(245, 245, 245)
            
            # Format currency columns for readability if present
            for col in ['NETWR', 'WRBTR', 'DMBTR', 'UMSATZ']:
                if col in df.columns:
                    try:
                        df[col] = df[col].apply(lambda x: f"{float(x):,.2f}")
                    except: pass

            txt_data = df.head(15).to_string(index=False)
            if len(df) > 15:
                txt_data += f"\n\n... ({len(df) - 15} more records truncated)"
            
            self.multi_cell(0, 4, txt_data, 0, 'L', True)
        self.ln(8)

def run_audit_bot_pdf():
    print("INITIALIZING SAP ECC FORENSIC AUDIT BOT (PDF ENGINE)...")
    conn = sqlite3.connect(DB_NAME)
    pdf = AuditPDF()
    pdf.add_page()

    # --- REPORT HEADER ---
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 15, 'FORENSIC AUDIT FINDINGS REPORT', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Target Database: {DB_NAME}", 0, 1, 'C')
    pdf.cell(0, 6, f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)

    # --- STRATEGIC CONTEXT (THE "HOW TO READ THIS" SECTION) ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '  HOW TO READ THIS REPORT (STRATEGIC CONTEXT)', 0, 1, 'L', 1)
    
    pdf.set_font('Arial', '', 10)
    context_text = (
        "This document validates the 'Synthetic CFO' SAP ECC Simulation. Unlike a standard financial audit where findings are negative, "
        "in this context, findings represent SUCCESSFUL DATA GENERATION.\n\n"
        "1. STATUS: CLEAN (Green)\n"
        "   Meaning: The control logic is functioning normally. No anomalies were generated in this batch.\n\n"
        "2. STATUS: WARN (Orange)\n"
        "   Meaning: Suspicious activity detected (e.g., Weekend Postings, SOD Conflicts). These are 'Red Flags' designed "
        "to trigger alerts in AI/ML training models.\n\n"
        "3. STATUS: FAIL / CRITICAL (Red)\n"
        "   Meaning: Confirmed Fraud Pattern (e.g., Kiting, Lapping). The simulation successfully planted a 'Digital Virus' "
        "for auditors to find."
    )
    pdf.multi_cell(0, 6, context_text)
    pdf.ln(10)

    # ==============================================================================
    # MODULE: P2P (PROCURE-TO-PAY)
    # ==============================================================================
    
    # 1. SOD Conflicts
    query_sod = "SELECT BELNR, USNAM, TCODE, SME_REASONING FROM P2P_BKPF WHERE SME_REASONING LIKE '%SOD%' OR SME_REASONING LIKE '%Self-Approval%'"
    df_sod = pd.read_sql(query_sod, conn)
    status = "CLEAN" if df_sod.empty else f"FAIL ({len(df_sod)} Conflicts)"
    pdf.chapter_heading("SEGREGATION OF DUTIES (P2P-02)", "Transactions where Creator == Approver.")
    pdf.log_finding_table(df_sod, status)

    # 2. Split POs
    query_split = "SELECT EBELN, ERNAM, NETWR, SME_REASONING FROM P2P_EKKO WHERE SME_REASONING LIKE '%Split%' OR SME_REASONING LIKE '%Limit Evasion%'"
    df_split = pd.read_sql(query_split, conn)
    status = "CLEAN" if df_split.empty else f"FAIL ({len(df_split)} Split POs)"
    pdf.chapter_heading("SPLIT PURCHASE ORDERS (P2P-03)", "Structuring orders to bypass approval limits.")
    pdf.log_finding_table(df_split, status)

    # 3. Duplicate Invoices
    query_dup = "SELECT BELNR, XBLNR, BKTXT FROM P2P_BKPF WHERE XBLNR LIKE '% ' OR BKTXT LIKE '%Duplicate%'"
    df_dup = pd.read_sql(query_dup, conn)
    status = "CLEAN" if df_dup.empty else f"FAIL ({len(df_dup)} Duplicates)"
    pdf.chapter_heading("DUPLICATE INVOICES (P2P-01)", "Invoices with trailing whitespace used to bypass uniqueness checks.")
    pdf.log_finding_table(df_dup, status)

    pdf.add_page() 

    # ==============================================================================
    # MODULE: O2C (ORDER-TO-CASH)
    # ==============================================================================

    # 4. Channel Stuffing
    query_stuffing = "SELECT VBELN, NETWR, FKDAT, SME_REASONING FROM O2C_VBRK WHERE SME_REASONING LIKE '%Stuffing%' OR SME_REASONING LIKE '%Force%' OR SME_REASONING LIKE '%Premature%'"
    df_stuffing = pd.read_sql(query_stuffing, conn)
    status = "CLEAN" if df_stuffing.empty else f"FAIL ({len(df_stuffing)} Stuffing Events)"
    pdf.chapter_heading("REVENUE CUT-OFF / CHANNEL STUFFING (O2C-02)", "High-value sales forced through at month-end.")
    pdf.log_finding_table(df_stuffing, status)

    # 5. Phantom Billing
    query_phantom = "SELECT VBELN, NETWR, KUNRG, SME_REASONING FROM O2C_VBRK WHERE SME_REASONING LIKE '%Phantom%' OR SME_REASONING LIKE '%No Goods Issue%'"
    df_phantom = pd.read_sql(query_phantom, conn)
    status = "CLEAN" if df_phantom.empty else f"CRITICAL FAIL ({len(df_phantom)} Phantom Bills)"
    pdf.chapter_heading("PHANTOM BILLING (O2C-03)", "Revenue recognition without proof of delivery (Goods Issue).")
    pdf.log_finding_table(df_phantom, status)

    # ==============================================================================
    # MODULE: CE (CASH MANAGEMENT)
    # ==============================================================================

    # 6. Kiting
    query_kiting = "SELECT KUKEY, ESNUM, UMSATZ, VALUT, SME_REASONING FROM CE_FEBEP WHERE SME_REASONING LIKE '%Kiting%'"
    df_kiting = pd.read_sql(query_kiting, conn)
    status = "CLEAN" if df_kiting.empty else f"CRITICAL FAIL ({len(df_kiting)} Kiting Events)"
    pdf.chapter_heading("CHECK KITING (CE-01)", "Large transfers with value date mismatches (Float Fraud).")
    pdf.log_finding_table(df_kiting, status)

    # 7. Lapping
    query_lapping = "SELECT KUKEY, ESNUM, UMSATZ, PARTN, SME_REASONING FROM CE_FEBEP WHERE SME_REASONING LIKE '%Lapping%' OR SME_REASONING LIKE '%Mismatch%'"
    df_lapping = pd.read_sql(query_lapping, conn)
    status = "CLEAN" if df_lapping.empty else f"FAIL ({len(df_lapping)} Lapping Events)"
    pdf.chapter_heading("LAPPING / TEEMING (CE-03)", "Receivables applied to the wrong customer account.")
    pdf.log_finding_table(df_lapping, status)

    pdf.add_page()

    # ==============================================================================
    # MODULE: R2R (GENERAL LEDGER)
    # ==============================================================================

    # 8. Cookie Jar Reserves
    # FIX: Using explicit aliases to avoid 'Ambiguous column' error
    query_cookie = """
    SELECT 
        R2R_BSEG.BELNR, 
        R2R_BSEG.WRBTR, 
        R2R_BSEG.SME_REASONING 
    FROM R2R_BSEG 
    LEFT JOIN R2R_BKPF ON R2R_BSEG.BELNR = R2R_BKPF.BELNR 
    WHERE R2R_BSEG.SME_REASONING LIKE '%Cookie Jar%' 
       OR R2R_BSEG.SME_REASONING LIKE '%Reserve Release%'
    """
    df_cookie = pd.read_sql(query_cookie, conn)
    status = "CLEAN" if df_cookie.empty else f"CRITICAL FAIL ({len(df_cookie)} Reserve Releases)"
    pdf.chapter_heading("COOKIE JAR RESERVES (R2R-02)", "Earnings management via manual reserve releases.")
    pdf.log_finding_table(df_cookie, status)

    # 9. Top-Side Adjustments
    query_topside = "SELECT BELNR, HKONT, SME_REASONING FROM R2R_BSEG WHERE SME_REASONING LIKE '%Top-Side%' OR SME_REASONING LIKE '%Reconciliation Account%'"
    df_topside = pd.read_sql(query_topside, conn)
    status = "CLEAN" if df_topside.empty else f"FAIL ({len(df_topside)} Top-Side Adjs)"
    pdf.chapter_heading("TOP-SIDE ADJUSTMENTS (R2R-04)", "Direct posting to Control Accounts bypassing sub-ledgers.")
    pdf.log_finding_table(df_topside, status)

    # --- SAVE ---
    pdf.output(REPORT_FILE, 'F')
    conn.close()
    print(f"SUCCESS: Platinum Audit PDF Generated: '{REPORT_FILE}'")

if __name__ == "__main__":
    run_audit_bot_pdf()