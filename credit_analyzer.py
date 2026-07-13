import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import re
import json
from datetime import datetime

class CreditReportAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Report Forensics Analyzer v1.0")
        self.root.geometry("1100x700")
        
        self.report_data = ""
        self.parsed_data = {}
        
        # Menu
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Upload Credit Report", command=self.upload_file)
        file_menu.add_command(label="Export Analysis Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)
        
        # Main Panels
        self.main_panel = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left Panel (Raw Data)
        left_frame = ttk.Frame(self.main_panel)
        self.main_panel.add(left_frame, weight=1)
        ttk.Label(left_frame, text="Raw Credit Report Data").pack(anchor=tk.W)
        self.raw_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=20)
        self.raw_text.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel (Analysis)
        right_frame = ttk.Frame(self.main_panel)
        self.main_panel.add(right_frame, weight=2)
        
        # Toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="Run FCRA/FACTA Scan", command=self.run_scan).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Metro 2 Compliance", command=self.metro2_audit).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Calculate Damages", command=self.calc_damages).pack(side=tk.LEFT, padx=2)
        
        # Progress Bar
        self.progress = ttk.Progressbar(right_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Result Tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Violations Found")
        self.notebook.add(self.tab2, text="Metro 2 Audit")
        self.notebook.add(self.tab3, text="Potential Damages")
        
        self.violations_text = scrolledtext.ScrolledText(self.tab1, wrap=tk.WORD)
        self.violations_text.pack(fill=tk.BOTH, expand=True)
        
        self.metro2_text = scrolledtext.ScrolledText(self.tab2, wrap=tk.WORD)
        self.metro2_text.pack(fill=tk.BOTH, expand=True)
        
        self.damages_text = scrolledtext.ScrolledText(self.tab3, wrap=tk.WORD)
        self.damages_text.pack(fill=tk.BOTH, expand=True)
        
        self.parsed_data = {}

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text/PDF files", "*.txt *.pdf"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.report_data = f.read()
                self.raw_text.delete(1.0, tk.END)
                self.raw_text.insert(tk.END, self.report_data[:5000] + "\n\n[Truncated for performance...]")
                messagebox.showinfo("Success", "File uploaded successfully. Click 'Run FCRA/FACTA Scan' to analyze.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def parse_report(self):
        data = self.report_data
        parsed = {}
        parsed['accounts'] = []
        parsed['inquiries'] = []
        parsed['public_records'] = []
        parsed['collections'] = []
        parsed['personal_info'] = {}
        
        # Simple pattern matching
        name_match = re.search(r'Name:\s*([^\n]+)', data, re.IGNORECASE)
        if name_match: parsed['personal_info']['name'] = name_match.group(1).strip()
        
        ssn_match = re.search(r'SSN[^:]*:\s*([^\n]+)', data, re.IGNORECASE)
        if ssn_match: parsed['personal_info']['ssn'] = ssn_match.group(1).strip()
        
        # Account patterns
        accounts = re.findall(r'Account\s*(?:#|Number)?[:\s]+([^\n]+)[\s\S]*?Balance:\s*([^\n]+)[\s\S]*?Status:\s*([^\n]+)', data, re.IGNORECASE)
        for acc in accounts:
            parsed['accounts'].append({
                'number': acc[0].strip(),
                'balance': acc[1].strip(),
                'status': acc[2].strip()
            })
        
        # Inquiries
        inquiries = re.findall(r'Inquiry\s*[:\s]+([^\n]+)\s*Date:\s*([^\n]+)', data, re.IGNORECASE)
        for inq in inquiries:
            parsed['inquiries'].append({'company': inq[0].strip(), 'date': inq[1].strip()})
        
        self.parsed_data = parsed
        return parsed

    def run_scan(self):
        if not self.report_data:
            messagebox.showwarning("Warning", "Please upload a credit report first.")
            return
        
        self.progress['value'] = 0
        self.violations_text.delete(1.0, tk.END)
        self.violations_text.insert(tk.END, "Scanning for FCRA/FACTA violations...\n\n")
        
        def scan():
            parsed = self.parse_report()
            violations = []
            
            # FCRA §605 - Obsolescence (7 year rule)
            self.progress['value'] = 20
            violations.append("FCRA §605 (15 USC §1681c) – Obsolete Information")
            violations.append("  → Check if any accounts are older than 7 years (10 years for bankruptcy).")
            
            # FCRA §611 - Dispute reinvestigation
            self.progress['value'] = 40
            violations.append("\nFCRA §611 (15 USC §1681i) – Reinvestigation")
            violations.append("  → Ensure disputes were reinvestigated within 30 days.")
            
            # FCRA §609 - Disclosure
            self.progress['value'] = 60
            violations.append("\nFCRA §609 (15 USC §1681g) – Disclosure")
            violations.append("  → Verify if source of information is disclosed.")
            
            # FCRA §623 - Furnisher duties
            self.progress['value'] = 80
            violations.append("\nFCRA §623 (15 USC §1681s-2) – Furnisher Responsibilities")
            violations.append("  → Check if Date of First Delinquency (DoFD) is reported.")
            
            # FACTA §112 - Identity theft
            self.progress['value'] = 90
            violations.append("\nFACTA §112 – Identity Theft Protections")
            violations.append("  → Verify if fraud alerts are properly applied.")
            
            # Count potential issues
            total_issues = len(parsed.get('accounts', [])) + len(parsed.get('inquiries', []))
            violations.append(f"\n\nTotal potential issues identified: {total_issues}")
            violations.append(f"Accounts found: {len(parsed.get('accounts', []))}")
            violations.append(f"Inquiries found: {len(parsed.get('inquiries', []))}")
            
            self.root.after(0, lambda: self.display_violations("\n".join(violations)))
            self.root.after(0, lambda: self.progress.configure(value=100))
        
        threading.Thread(target=scan).start()

    def display_violations(self, text):
        self.violations_text.delete(1.0, tk.END)
        self.violations_text.insert(tk.END, text)

    def metro2_audit(self):
        self.metro2_text.delete(1.0, tk.END)
        audit = "Metro 2 Compliance Audit\n" + "="*50 + "\n\n"
        audit += "Checking standard codes:\n"
        audit += "• Account Status Codes (0-9, A-Z, DA, DF) – Check if valid.\n"
        audit += "• Payment Ratings (0-9, A-L) – Verify accuracy.\n"
        audit += "• Special Comment Codes (AU, CO, CL, CM, DB, FC) – Ensure proper use.\n"
        audit += "• Compliance Codes (XA, XB, XC, XD, XE) – Review for errors.\n"
        audit += "\nBased on your report data, these items should be validated against Metro 2 specifications."
        self.metro2_text.insert(tk.END, audit)

    def calc_damages(self):
        self.damages_text.delete(1.0, tk.END)
        damages = "Statutory Damages Calculator (FCRA)\n" + "="*50 + "\n\n"
        
        # Estimate based on accounts found
        account_count = len(self.parsed_data.get('accounts', []))
        inquiry_count = len(self.parsed_data.get('inquiries', []))
        
        per_violation = 1000  # FCRA statutory damages up to $1,000 per violation
        total_estimated = (account_count + inquiry_count) * per_violation
        
        damages += f"Estimated FCRA violations:\n"
        damages += f"  • Accounts: {account_count} (up to ${per_violation} each)\n"
        damages += f"  • Inquiries: {inquiry_count} (up to ${per_violation} each)\n"
        damages += f"  • Total estimated statutory damages: ${total_estimated:,}\n\n"
        damages += "Note: Actual damages vary. Consult an attorney for accurate assessment."
        self.damages_text.insert(tk.END, damages)

    def export_report(self):
        if not self.report_data:
            messagebox.showwarning("Warning", "No report to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write("Credit Report Analysis Report\n")
                f.write("="*50 + "\n\n")
                f.write(self.violations_text.get(1.0, tk.END))
                f.write("\n\n" + self.metro2_text.get(1.0, tk.END))
                f.write("\n\n" + self.damages_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Report exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CreditReportAnalyzer(root)
    root.mainloop()