#!/usr/bin/env python3
"""
Damancom Login Automation with GUI
Run this script to open a graphical interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time

class DamancomLoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Damancom Login Automation")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        self.driver = None
        self.running = False
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🔐 Damancom Login Automation", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # User Information Section
        info_frame = ttk.LabelFrame(main_frame, text="User Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Username field
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value="")
        self.username_entry = ttk.Entry(info_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Password field
        ttk.Label(info_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value="")
        self.password_entry = ttk.Entry(info_frame, textvariable=self.password_var, 
                                       width=40, show="*")
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Show/Hide password checkbox
        self.show_password_var = tk.BooleanVar()
        show_pwd_cb = ttk.Checkbutton(info_frame, text="Show password", 
                                      variable=self.show_password_var,
                                      command=self.toggle_password)
        show_pwd_cb.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Settings Section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Headless mode checkbox
        self.headless_var = tk.BooleanVar(value=False)
        headless_cb = ttk.Checkbutton(settings_frame, text="Headless mode (no browser window)", 
                                     variable=self.headless_var)
        headless_cb.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="🚀 Start Login", 
                                     command=self.start_automation, width=20)
        self.run_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", 
                                     command=self.stop_automation, width=20, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Log/Status Section
        log_frame = ttk.LabelFrame(main_frame, text="Automation Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=20, 
                                                  wrap=tk.WORD, font=('Courier', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log("Welcome! Enter your credentials and click 'Start Login'")
    
    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, status):
        self.status_var.set(status)
    
    def start_automation(self):
        if not self.username_var.get() or not self.password_var.get():
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        self.running = True
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        
        # Run automation in separate thread
        thread = threading.Thread(target=self.run_automation, daemon=True)
        thread.start()
    
    def stop_automation(self):
        self.running = False
        self.log("\n⏹ Stopping automation...")
        if self.driver:
            try:
                self.driver.quit()
                self.log("✓ Browser closed")
            except:
                pass
        self.reset_ui()
    
    def reset_ui(self):
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.username_entry.config(state='normal')
        self.password_entry.config(state='normal')
        self.set_status("Ready")
    
    def run_automation(self):
        try:
            self.log("\n" + "="*60)
            self.log("🚀 DAMANCOM LOGIN AUTOMATION STARTING")
            self.log("="*60)
            self.set_status("Starting browser...")
            
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            
            if self.headless_var.get():
                options.add_argument("--headless=new")
                self.log("✓ Headless mode enabled")
            else:
                self.log("✓ Running in visible mode")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
            
            self.log("✓ Chrome options configured")
            
            # Start browser
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            
            self.driver.implicitly_wait(8)
            self.driver.set_page_load_timeout(45)
            self.log("✓ Chrome browser started successfully!")
            
            # Load page
            url = "https://www.damancom.ma/fr/authentification"
            self.log(f"\n📂 Opening URL: {url}")
            self.set_status("Loading page...")
            
            try:
                self.driver.get(url)
                self.log("✓ Page loaded successfully!")
            except TimeoutException:
                self.log("⚠️  Page load timeout - continuing anyway")
            
            # Wait for content
            self.log("⏳ Waiting for page content to load...")
            time.sleep(3)
            
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "button")) > 0
                )
                self.log(f"✓ Page loaded at: {self.driver.current_url}")
            except TimeoutException:
                self.log(f"⚠️  Timeout waiting for content. URL: {self.driver.current_url}")
            
            if not self.running:
                return
            
            time.sleep(2)
            
            # Step 1: Click OTP button
            self.log("\n=== Step 1: Clicking 'S'authentifier avec OTP' button ===")
            self.set_status("Step 1: Clicking OTP button...")
            
            otp_clicked = self.click_element([
                "//button[contains(@class, 'btn-primary') and contains(text(), \"S'authentifier avec OTP\")]",
                "//button[contains(normalize-space(.), \"S'authentifier avec OTP\")]",
                "//button[contains(., 'OTP')]"
            ])
            
            if otp_clicked:
                self.log("✓ Clicked 'S'authentifier avec OTP' button")
                time.sleep(2)
            else:
                self.log("✗ Could not find 'S'authentifier avec OTP' button")
            
            if not self.running:
                return
            
            # Step 2: Enter username
            self.log("\n=== Step 2: Entering username ===")
            self.set_status("Step 2: Entering username...")
            
            username_filled = self.fill_input([
                (By.XPATH, "//input[contains(@placeholder,'IDENTIFIANT') or contains(@placeholder,'Identifiant')]"),
                (By.NAME, "username"),
                (By.NAME, "identifiant"),
                (By.ID, "username"),
                (By.XPATH, "//input[@type='text']")
            ], self.username_var.get())
            
            if username_filled:
                self.log(f"✓ Entered username: {self.username_var.get()}")
            else:
                self.log("✗ Could not find username field")
            
            if not self.running:
                return
            
            # Step 3: Click Suivant
            self.log("\n=== Step 3: Clicking 'Suivant' button ===")
            self.set_status("Step 3: Clicking next button...")
            time.sleep(1)
            
            suivant_clicked = self.click_element([
                "//button[contains(@class, 'btn-primary') and contains(text(), 'Suivant')]",
                "//button[contains(normalize-space(.), 'Suivant')]"
            ])
            
            if suivant_clicked:
                self.log("✓ Clicked 'Suivant' button")
                time.sleep(2)
            else:
                self.log("✗ Could not find 'Suivant' button")
            
            if not self.running:
                return
            
            # Step 4: Enter password
            self.log("\n=== Step 4: Entering password ===")
            self.set_status("Step 4: Entering password...")
            
            password_filled = self.fill_input([
                (By.XPATH, "//input[contains(@placeholder,'MOT DE PASSE') or contains(@placeholder,'Mot de passe')]"),
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.XPATH, "//input[@type='password']")
            ], self.password_var.get())
            
            if password_filled:
                self.log("✓ Entered password")
            else:
                self.log("✗ Could not find password field")
            
            if not self.running:
                return
            
            # Step 5: Wait for OTP
            self.log("\n=== Step 5: Waiting for OTP page ===")
            self.set_status("Step 5: Waiting for OTP page...")
            time.sleep(3)
            
            otp_inputs = self.driver.find_elements(By.XPATH, "//input[@type='tel' and @maxlength='1']")
            
            if len(otp_inputs) >= 6:
                self.log(f"✓ OTP page detected! Found {len(otp_inputs)} input fields")
                self.log("\n" + "="*50)
                self.log("📱 Please check your SMS and Email for the OTP code")
                self.log("="*50)
                self.set_status("Waiting for OTP input...")
                
                # Ask for OTP in GUI
                otp_code = simpledialog.askstring("OTP Required", 
                                                 "Enter the 6-digit OTP code from SMS/Email:",
                                                 parent=self.root)
                
                if otp_code and len(otp_code) == 6 and otp_code.isdigit():
                    self.log(f"\n✓ Received OTP code: {otp_code}")
                    self.set_status("Entering OTP code...")
                    
                    # Fill OTP
                    self.log(f"📝 Found {len(otp_inputs)} OTP input fields. Filling...")
                    for i, digit in enumerate(otp_code[:6]):
                        otp_inputs[i].clear()
                        otp_inputs[i].send_keys(digit)
                        self.log(f"  → Entered digit {i+1}: {digit}")
                    
                    self.log("✓ OTP code entered successfully")
                    time.sleep(1)
                    
                    # Step 6: Click Valider
                    self.log("\n=== Step 6: Clicking 'Valider' button ===")
                    self.set_status("Step 6: Validating OTP...")
                    
                    valider_clicked = self.click_element([
                        "//button[contains(normalize-space(.), 'Valider')]"
                    ])
                    
                    if valider_clicked:
                        self.log("✓ Clicked 'Valider' button")
                        time.sleep(3)
                    else:
                        self.log("✗ Could not find 'Valider' button")
                else:
                    self.log("✗ Invalid or cancelled OTP input")
            else:
                self.log(f"✗ OTP page not detected. Found {len(otp_inputs)} fields (expected 6)")
            
            # Final check
            self.log("\n=== Final Check: Login Status ===")
            self.set_status("Checking login status...")
            
            success_indicators = [
                "//a[contains(., 'Logout') or contains(., 'Déconnexion')]",
                "//div[contains(@class,'dashboard')]",
                "//h1[contains(.,'Bienvenue')]"
            ]
            
            logged_in = False
            for sel in success_indicators:
                try:
                    if self.driver.find_elements(By.XPATH, sel):
                        logged_in = True
                        break
                except:
                    pass
            
            if logged_in:
                self.log("✅ Login successful!")
                self.set_status("Login successful!")
                messagebox.showinfo("Success", "Login completed successfully!")
            else:
                self.log(f"⚠️  Login status unclear")
                self.log(f"Current URL: {self.driver.current_url}")
                self.set_status("Login status unclear")
            
            self.log("\n⏳ Keeping browser open for inspection...")
            time.sleep(60)
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {e}")
            self.set_status(f"Error: {str(e)[:50]}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
                self.log("\n✅ Browser closed")
            self.reset_ui()
    
    def click_element(self, xpaths):
        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                try:
                    element.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                continue
        return False
    
    def fill_input(self, selectors, text):
        for by, sel in selectors:
            try:
                element = self.driver.find_element(by, sel)
                element.clear()
                element.send_keys(text)
                return True
            except:
                continue
        return False

def main():
    root = tk.Tk()
    app = DamancomLoginGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
