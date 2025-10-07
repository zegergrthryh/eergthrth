# damancom_login.py
# 
# HOW TO RUN: Open Shell and type: python main.py
# (The Run button won't work - this script needs your OTP input!)
# 
# The script will ask you for the 6-digit OTP code from your SMS/Email

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementClickInterceptedException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ===== CONFIG =====
URL = "https://www.damancom.ma/fr/authentification"
HEADLESS = False              # Temporarily disabled - site blocks headless browsers
IMPLICIT_WAIT = 8             # seconds
EXPLICIT_WAIT = 20            # seconds
# ==================

def try_find(driver, by, value, timeout=EXPLICIT_WAIT):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

def click_if_exists(driver, by, value, timeout=5):
    el = try_find(driver, by, value, timeout=timeout)
    if el:
        try:
            el.click()
            return True
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", el)
            return True
    return False

def fill_input_if_exists(driver, selectors, text):
    """
    selectors: list of (By, selector) to try in order
    """
    for by, sel in selectors:
        try:
            el = driver.find_element(by, sel)
            el.clear()
            el.send_keys(text)
            return True
        except Exception:
            continue
    return False

def fill_otp_fields(driver, otp_code):
    """
    Fill 6 separate OTP input fields with the OTP code digits
    """
    try:
        # Find all OTP input fields (type='tel', maxlength='1')
        otp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel' and @maxlength='1']")
        
        if len(otp_inputs) >= 6:
            print(f"📝 Found {len(otp_inputs)} OTP input fields. Filling with code...", flush=True)
            for i, digit in enumerate(otp_code[:6]):
                otp_inputs[i].clear()
                otp_inputs[i].send_keys(digit)
                print(f"  → Entered digit {i+1}: {digit}", flush=True)
            return True
        else:
            print(f"✗ Expected 6 OTP fields but found {len(otp_inputs)}", flush=True)
            return False
    except Exception as e:
        print(f"✗ Error filling OTP fields: {e}", flush=True)
        return False

def main():
    print("\n" + "="*60, flush=True)
    print("🚀 DAMANCOM LOGIN AUTOMATION", flush=True)
    print("="*60, flush=True)
    
    # Ask for credentials
    print("\nPlease enter your Damancom credentials:", flush=True)
    EMAIL = input("Username: ").strip()
    PASSWORD = input("Password: ").strip()
    
    if not EMAIL or not PASSWORD:
        print("\n❌ Username and password are required!", flush=True)
        return
    
    print("\n" + "="*60, flush=True)
    print("STARTING AUTOMATION", flush=True)
    print("="*60, flush=True)
    
    options = webdriver.ChromeOptions()
    
    # Headless mode - currently disabled as site blocks headless browsers
    if HEADLESS:
        options.add_argument("--headless=new")
        print("✓ Headless mode enabled", flush=True)
    else:
        print("✓ Running in visible mode (headless disabled)", flush=True)
    
    # Required options for Replit/containerized environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
    
    print("✓ Chrome options configured", flush=True)
    
    # Use regular Selenium with anti-detection options
    print("✓ Starting Chrome browser...", flush=True)
    driver = webdriver.Chrome(options=options)
    
    # Hide webdriver flag
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(45)
    print("✓ Chrome browser started successfully!", flush=True)

    print(f"\n📂 Opening URL: {URL}", flush=True)
    try:
        driver.get(URL)
        print("✓ Page loaded successfully!", flush=True)
    except TimeoutException:
        print("⚠️  Page load timeout - continuing anyway", flush=True)
    
    # Wait for page to actually load by checking for elements
    print("⏳ Waiting for page content to load...", flush=True)
    time.sleep(3)
    
    # Wait for any button or form to appear (sign the page has loaded)
    try:
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "button")) > 0 or 
                     len(d.find_elements(By.TAG_NAME, "input")) > 0
        )
        print(f"✓ Page loaded successfully at: {driver.current_url}", flush=True)
    except TimeoutException:
        print(f"⚠️  Timeout waiting for content. Current URL: {driver.current_url}", flush=True)
    
    time.sleep(2)

    # Step 1: Click "S'authentifier avec OTP" button
    print("\n=== Step 1: Clicking 'S'authentifier avec OTP' button ===", flush=True)
    print(f"Current URL: {driver.current_url}", flush=True)
    print(f"Page title: {driver.title}", flush=True)
    
    # Try multiple selectors for the OTP button
    otp_button_selectors = [
        "//button[contains(@class, 'btn-primary') and contains(text(), \"S'authentifier avec OTP\")]",
        "//button[contains(normalize-space(.), \"S'authentifier avec OTP\")]",
        "//button[contains(., 'OTP')]"
    ]
    
    otp_button_clicked = False
    for selector in otp_button_selectors:
        if click_if_exists(driver, By.XPATH, selector, timeout=5):
            print("✓ Clicked 'S'authentifier avec OTP' button", flush=True)
            otp_button_clicked = True
            time.sleep(2)
            break
    
    if not otp_button_clicked:
        print("✗ Could not find 'S'authentifier avec OTP' button", flush=True)
        driver.save_screenshot("step1_debug.png")
        print("📸 Saved debug screenshot: step1_debug.png", flush=True)

    # Step 2: Enter username/identifier
    print("\n=== Step 2: Entering username ===", flush=True)
    id_selectors = [
        (By.XPATH, "//input[contains(@placeholder,'IDENTIFIANT') or contains(@placeholder,'Identifiant')]"),
        (By.NAME, "username"), 
        (By.NAME, "identifiant"), 
        (By.NAME, "identite"),
        (By.NAME, "email"), 
        (By.ID, "username"), 
        (By.ID, "identifiant"),
        (By.XPATH, "//input[@type='text']")
    ]
    filled_id = fill_input_if_exists(driver, id_selectors, EMAIL)
    if filled_id:
        print(f"✓ Entered username: {EMAIL}", flush=True)
    else:
        print("✗ Could not find username field", flush=True)

    # Step 3: Click "Suivant" button
    print("\n=== Step 3: Clicking 'Suivant' button ===", flush=True)
    time.sleep(1)
    
    # Try multiple selectors for the Suivant button
    suivant_selectors = [
        "//button[contains(@class, 'btn-primary') and contains(text(), 'Suivant')]",
        "//button[contains(normalize-space(.), 'Suivant')]",
        "//button[contains(., 'Suivant')]"
    ]
    
    suivant_clicked = False
    for selector in suivant_selectors:
        if click_if_exists(driver, By.XPATH, selector, timeout=5):
            print("✓ Clicked 'Suivant' button", flush=True)
            suivant_clicked = True
            time.sleep(2)
            break
    
    if not suivant_clicked:
        print("✗ Could not find 'Suivant' button", flush=True)

    # Step 4: Enter password
    print("\n=== Step 4: Entering password ===", flush=True)
    pwd_selectors = [
        (By.XPATH, "//input[contains(@placeholder,'MOT DE PASSE') or contains(@placeholder,'Mot de passe')]"),
        (By.NAME, "password"), 
        (By.NAME, "motdepasse"), 
        (By.ID, "password"),
        (By.XPATH, "//input[@type='password']")
    ]
    filled_pwd = fill_input_if_exists(driver, pwd_selectors, PASSWORD)
    if filled_pwd:
        print("✓ Entered password", flush=True)
    else:
        print("✗ Could not find password field", flush=True)

    # Step 5: Wait for OTP page and ask user for code
    print("\n=== Step 5: Waiting for OTP page ===", flush=True)
    time.sleep(3)
    
    # Check if we're on the OTP page by looking for the 6 OTP input fields
    otp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel' and @maxlength='1']")
    
    if len(otp_inputs) >= 6:
        print(f"✓ OTP page detected! Found {len(otp_inputs)} input fields", flush=True)
        print("\n" + "="*50, flush=True)
        print("📱 Please check your SMS and Email for the OTP code", flush=True)
        print("="*50, flush=True)
        
        # Ask user for OTP code
        otp_code = input("\nEnter the 6-digit OTP code: ").strip()
        
        # Validate OTP code
        if len(otp_code) == 6 and otp_code.isdigit():
            print(f"\n✓ Received OTP code: {otp_code}", flush=True)
            
            # Fill OTP fields
            if fill_otp_fields(driver, otp_code):
                print("✓ OTP code entered successfully", flush=True)
                time.sleep(1)
                
                # Step 6: Click "Valider" button
                print("\n=== Step 6: Clicking 'Valider' button ===", flush=True)
                valider_clicked = click_if_exists(
                    driver, 
                    By.XPATH, 
                    "//button[contains(normalize-space(.), 'Valider')]",
                    timeout=5
                )
                if valider_clicked:
                    print("✓ Clicked 'Valider' button", flush=True)
                    time.sleep(3)
                else:
                    print("✗ Could not find 'Valider' button", flush=True)
            else:
                print("✗ Failed to enter OTP code", flush=True)
        else:
            print("✗ Invalid OTP code. Must be 6 digits.", flush=True)
    else:
        print(f"✗ OTP page not detected. Found {len(otp_inputs)} OTP fields (expected 6)", flush=True)

    # Final check: successful login indicator
    print("\n=== Final Check: Login Status ===", flush=True)
    success_indicators = [
        "//a[contains(., 'Logout') or contains(., 'Déconnexion') or contains(., 'Se déconnecter')]",
        "//div[contains(@class,'dashboard')]", 
        "//h1[contains(.,'Bienvenue')]", 
        "//a[contains(@href,'/private/')]"
    ]
    logged_in = False
    for sel in success_indicators:
        try:
            if driver.find_elements(By.XPATH, sel):
                logged_in = True
                break
        except Exception:
            pass

    if logged_in:
        print("✅ Login successful!", flush=True)
    else:
        print("⚠️  Login status unclear. Check the browser window.", flush=True)
        print(f"Current URL: {driver.current_url}", flush=True)
        print(f"Page title: {driver.title}", flush=True)
        driver.save_screenshot("damancom_debug.png")
        print("📸 Saved screenshot: damancom_debug.png", flush=True)

    # Keep browser open for inspection
    print("\n" + "="*60, flush=True)
    print("⏳ Browser will remain open for 10 seconds for inspection", flush=True)
    print("="*60, flush=True)
    time.sleep(10)
    driver.quit()
    print("\n✅ Script completed. Browser closed.", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
