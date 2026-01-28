import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION ---
DB_NAME = "synthetic_cfo_erp.db"
REPORT_FILE = "Forensic_Audit_Report.pdf"

class AuditPDF(FPDF):
    def header(self):
        # Branding: lowercase 'synthetic cfo'
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, 'synthetic cfo | AUTOMATED FORENSIC AUDIT BOT', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_heading(self, title, description):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(32, 55, 100) # Oracle Blue
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f'  TEST: {title}', 0, 1, 'L', 1)
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(80, 80, 80) # Dark Grey
        self.multi_cell(0, 6, f"Scope: {description}")
        self.ln(2)

    def log_finding_table(self, df, status_msg):
        # TRAFFIC LIGHT LOGIC
        self.set_font('Arial', 'B', 10)
        
        if "FAIL" in status_msg or "CRITICAL" in status_msg:
            self.set_text_color(200, 0, 0) # RED (Confirmed Fraud)
        elif "WARN" in status_msg:
            self.set_text_color(220, 110, 0) # DARK ORANGE (Suspicious)
        else:
            self.set_text_color(0, 128, 0) # GREEN (Clean)
            
        self.cell(0, 6, f"STATUS: {status_msg}", 0, 1, 'L')
        self.set_text_color(0, 0, 0) # Reset to black
        self.ln(2)

        if not df.empty:
            # Data Dump (Monospace for table-like look)
            self.set_font('Courier', '', 8)
            self.set_fill_color(245, 245, 245) # Very light grey
            
            # Convert DF to string with headers
            txt_data = df.head(15).to_string(index=False)
            if len(df) > 15:
                txt_data += f"\n\n... ({len(df) - 15} more records truncated)"
            
            self.multi_cell(0, 4, txt_data, 0, 'L', True)
        self.ln(8)

def run_audit_bot_pdf():
    print("INITIALIZING FORENSIC AUDIT BOT (PDF ENGINE)...")
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

    # --- STRATEGIC CONTEXT (The "So What?") ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '  HOW TO READ THIS REPORT (STRATEGIC CONTEXT)', 0, 1, 'L', 1)
    
    pdf.set_font('Arial', '', 10)
    context_text = (
        "This document validates the 'Synthetic CFO' ERP Simulation. Unlike a standard financial audit where findings are negative, "
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
    
    # 1. Manual Invoices (C-01)
    query_manual = "SELECT INVOICE_NUM, VENDOR_ID, INVOICE_AMOUNT, CREATED_BY FROM AP_INVOICES_ALL WHERE SOURCE = 'MANUAL' AND INVOICE_AMOUNT > 50000"
    df_manual = pd.read_sql(query_manual, conn)
    pdf.chapter_heading("HIGH VALUE MANUAL INVOICES (C-01)", "Flagging manual entries > $50k bypassing PO.")
    # Logic: Finding manual invoices is a WARNING (High Risk), not necessarily a FAIL unless unapproved
    status = "CLEAN" if df_manual.empty else f"WARN ({len(df_manual)} Manual Entries)"
    pdf.log_finding_table(df_manual, status)

    # 2. SOD Conflicts (C-08)
    query_sod = "SELECT INVOICE_NUM, INVOICE_AMOUNT, CREATED_BY, LAST_UPDATED_BY as APPROVED_BY FROM AP_INVOICES_ALL WHERE CREATED_BY = LAST_UPDATED_BY AND APPROVAL_STATUS = 'APPROVED'"
    df_sod = pd.read_sql(query_sod, conn)
    pdf.chapter_heading("SEGREGATION OF DUTIES (C-08)", "Invoices where Creator == Approver.")
    status = "CLEAN" if df_sod.empty else f"FAIL ({len(df_sod)} Conflicts)"
    pdf.log_finding_table(df_sod, status)

    # 3. Whitespace Duplicates (Data Hygiene)
    query_white = "SELECT INVOICE_NUM, VENDOR_ID, INVOICE_AMOUNT FROM AP_INVOICES_ALL WHERE INVOICE_NUM LIKE '% '"
    df_white = pd.read_sql(query_white, conn)
    pdf.chapter_heading("DATA SANITIZATION / HIDDEN DUPLICATES", "Invoices with trailing whitespace used to bypass unique constraints.")
    status = "CLEAN" if df_white.empty else f"FAIL ({len(df_white)} Anomalies)"
    pdf.log_finding_table(df_white, status)

    # 4. Voided Checks (C-06)
    query_void = "SELECT CHECK_NUMBER, AMOUNT, CHECK_DATE, VENDOR_ID FROM AP_CHECKS_ALL WHERE STATUS_LOOKUP_CODE = 'VOIDED'"
    df_void = pd.read_sql(query_void, conn)
    pdf.chapter_heading("VOIDED PAYMENTS (C-06)", "Listing voided checks for review.")
    status = "CLEAN" if df_void.empty else f"WARN ({len(df_void)} Voids)"
    pdf.log_finding_table(df_void, status)

    pdf.add_page() # Page Break

    # ==============================================================================
    # MODULE: CE (CASH MANAGEMENT)
    # ==============================================================================

    # 5. Kiting (CASH-01)
    query_kiting = "SELECT LINE_ID, TRX_CODE, AMOUNT, DESC FROM CE_STATEMENT_LINES WHERE GL_MATCH = 'NO_MATCH' AND DESC LIKE '%KITE%'"
    df_kiting = pd.read_sql(query_kiting, conn)
    pdf.chapter_heading("CHECK KITING / UNRECORDED FUNDS (CASH-01)", "Large wire transfers in Bank missing from GL.")
    status = "CLEAN" if df_kiting.empty else f"CRITICAL FAIL ({len(df_kiting)} Kiting Events)"
    pdf.log_finding_table(df_kiting, status)

    # ==============================================================================
    # MODULE: GL (GENERAL LEDGER)
    # ==============================================================================

    # 6. Management Override (GL-04)
    query_override = "SELECT JE_HEADER_ID, JE_LINE_NUM, ENTERED_DR, CREATED_BY FROM GL_JE_LINES WHERE CREATED_BY = 'CFO_OVERRIDE'"
    df_override = pd.read_sql(query_override, conn)
    pdf.chapter_heading("MANAGEMENT OVERRIDE (GL-04)", "Entries by restricted user 'CFO_OVERRIDE'.")
    status = "CLEAN" if df_override.empty else f"CRITICAL FAIL ({len(df_override)} Overrides)"
    pdf.log_finding_table(df_override, status)

    # 7. Benford's Law (GL-03)
    query_round = "SELECT JE_HEADER_ID, ENTERED_DR, SOURCE, PERIOD_NAME FROM GL_JE_LINES WHERE ENTERED_DR > 1000000 AND CAST(ENTERED_DR AS INTEGER) % 10000 = 0 AND SOURCE = 'Manual'"
    df_round = pd.read_sql(query_round, conn)
    pdf.chapter_heading("BENFORD'S LAW VIOLATIONS (GL-03)", "Large, perfectly round manual adjustments (> $1M).")
    status = "CLEAN" if df_round.empty else f"FAIL ({len(df_round)} Suspicious Entries)"
    pdf.log_finding_table(df_round, status)

    # 8. Weekend Posting (GL-02)
    query_dates = "SELECT JE_HEADER_ID, POSTED_DATE, ENTERED_DR FROM GL_JE_LINES WHERE SOURCE = 'Manual'"
    df_dates = pd.read_sql(query_dates, conn)
    df_dates['POSTED_DATE'] = pd.to_datetime(df_dates['POSTED_DATE'])
    df_weekend = df_dates[(df_dates['POSTED_DATE'].dt.weekday >= 5) & (df_dates['ENTERED_DR'] > 500000)]
    df_weekend['POSTED_DATE'] = df_weekend['POSTED_DATE'].dt.strftime('%Y-%m-%d')
    
    pdf.chapter_heading("SUSPICIOUS WEEKEND POSTINGS (GL-02)", "Manual JEs > $500k posted on Sat/Sun.")
    status = "CLEAN" if df_weekend.empty else f"WARN ({len(df_weekend)} Weekend Postings)"
    pdf.log_finding_table(df_weekend, status)

    # --- SAVE ---
    pdf.output(REPORT_FILE, 'F')
    conn.close()
    print(f"SUCCESS: Platinum Audit PDF Generated: '{REPORT_FILE}'")

if __name__ == "__main__":
    run_audit_bot_pdf()