from flask import Flask, render_template, request, jsonify, session as flask_session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import time
import os
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = os.urandom(24)

URL = "https://www.damancom.ma/fr/authentification"
IMPLICIT_WAIT = 8
EXPLICIT_WAIT = 20

active_sessions = {}

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
    try:
        otp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel' and @maxlength='1']")
        
        if len(otp_inputs) >= 6:
            for i, digit in enumerate(otp_code[:6]):
                otp_inputs[i].clear()
                otp_inputs[i].send_keys(digit)
            return True
        else:
            return False
    except Exception:
        return False

def create_driver():
    options = webdriver.ChromeOptions()
    
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(45)
    
    return driver

def get_screenshot(driver):
    try:
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        screenshot_base64 = base64.b64encode(buffer.getvalue()).decode()
        return screenshot_base64
    except Exception as e:
        return None

@app.route('/')
def index():
    return render_template('viewer.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    try:
        session_id = os.urandom(16).hex()
        flask_session['session_id'] = session_id
        
        driver = create_driver()
        
        driver.get(URL)
        time.sleep(3)
        
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "button")) > 0 or 
                     len(d.find_elements(By.TAG_NAME, "input")) > 0
        )
        
        time.sleep(2)
        
        otp_button_selectors = [
            "//button[contains(@class, 'btn-primary') and contains(text(), \"S'authentifier avec OTP\")]",
            "//button[contains(normalize-space(.), \"S'authentifier avec OTP\")]",
            "//button[contains(., 'OTP')]"
        ]
        
        for selector in otp_button_selectors:
            if click_if_exists(driver, By.XPATH, selector, timeout=5):
                time.sleep(2)
                break
        
        active_sessions[session_id] = {
            'driver': driver,
            'step': 'username',
            'status': 'ready'
        }
        
        screenshot = get_screenshot(driver)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'screenshot': screenshot,
            'step': 'username'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_screenshot', methods=['POST'])
def get_screenshot_endpoint():
    session_id = flask_session.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    driver = active_sessions[session_id]['driver']
    screenshot = get_screenshot(driver)
    
    return jsonify({
        'success': True,
        'screenshot': screenshot,
        'step': active_sessions[session_id]['step']
    })

@app.route('/submit_username', methods=['POST'])
def submit_username():
    session_id = flask_session.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    username = request.json.get('username')
    if not username:
        return jsonify({'success': False, 'error': 'Username required'})
    
    driver = active_sessions[session_id]['driver']
    
    try:
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
        
        filled = fill_input_if_exists(driver, id_selectors, username)
        
        if not filled:
            return jsonify({'success': False, 'error': 'Could not find username field'})
        
        time.sleep(1)
        
        suivant_selectors = [
            "//button[contains(@class, 'btn-primary') and contains(text(), 'Suivant')]",
            "//button[contains(normalize-space(.), 'Suivant')]",
            "//button[contains(., 'Suivant')]"
        ]
        
        button_clicked = False
        for selector in suivant_selectors:
            if click_if_exists(driver, By.XPATH, selector, timeout=5):
                button_clicked = True
                break
        
        if not button_clicked:
            return jsonify({'success': False, 'error': 'Could not find Next button'})
        
        try:
            def password_field_ready(driver):
                pwd_selectors = [
                    (By.XPATH, "//input[contains(@placeholder,'MOT DE PASSE') or contains(@placeholder,'Mot de passe')]"),
                    (By.NAME, "password"), 
                    (By.ID, "password"),
                    (By.XPATH, "//input[@type='password']")
                ]
                for by, sel in pwd_selectors:
                    try:
                        elem = driver.find_element(by, sel)
                        return elem if elem else False
                    except:
                        continue
                return False
            
            WebDriverWait(driver, EXPLICIT_WAIT).until(password_field_ready)
            
            active_sessions[session_id]['step'] = 'password'
            screenshot = get_screenshot(driver)
            
            return jsonify({
                'success': True,
                'screenshot': screenshot,
                'step': 'password'
            })
        except TimeoutException:
            return jsonify({'success': False, 'error': 'Password page did not load within expected time'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/submit_password', methods=['POST'])
def submit_password():
    session_id = flask_session.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    password = request.json.get('password')
    if not password:
        return jsonify({'success': False, 'error': 'Password required'})
    
    driver = active_sessions[session_id]['driver']
    
    try:
        pwd_selectors = [
            (By.XPATH, "//input[contains(@placeholder,'MOT DE PASSE') or contains(@placeholder,'Mot de passe')]"),
            (By.NAME, "password"), 
            (By.NAME, "motdepasse"), 
            (By.ID, "password"),
            (By.XPATH, "//input[@type='password']")
        ]
        
        filled = fill_input_if_exists(driver, pwd_selectors, password)
        
        if not filled:
            return jsonify({'success': False, 'error': 'Could not find password field'})
        
        time.sleep(1)
        
        suivant_selectors = [
            "//button[contains(@class, 'btn-primary') and contains(text(), 'Suivant')]",
            "//button[contains(normalize-space(.), 'Suivant')]",
            "//button[contains(., 'Suivant')]",
            "//button[contains(normalize-space(.), 'Continuer')]",
            "//button[@type='submit']"
        ]
        
        button_clicked = False
        for selector in suivant_selectors:
            if click_if_exists(driver, By.XPATH, selector, timeout=5):
                button_clicked = True
                break
        
        if not button_clicked:
            return jsonify({'success': False, 'error': 'Could not find continue button'})
        
        try:
            def otp_fields_ready(driver):
                fields = driver.find_elements(By.XPATH, "//input[@type='tel' and @maxlength='1']")
                return fields if len(fields) >= 6 else False
            
            otp_inputs = WebDriverWait(driver, EXPLICIT_WAIT).until(otp_fields_ready)
            
            active_sessions[session_id]['step'] = 'otp'
            screenshot = get_screenshot(driver)
            
            return jsonify({
                'success': True,
                'screenshot': screenshot,
                'step': 'otp'
            })
        except TimeoutException:
            return jsonify({'success': False, 'error': 'OTP page did not load within expected time'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/submit_otp', methods=['POST'])
def submit_otp():
    session_id = flask_session.get('session_id')
    
    if not session_id or session_id not in active_sessions:
        return jsonify({'success': False, 'error': 'No active session'})
    
    otp_code = request.json.get('otp')
    if not otp_code or len(otp_code) != 6:
        return jsonify({'success': False, 'error': 'OTP must be 6 digits'})
    
    driver = active_sessions[session_id]['driver']
    
    try:
        if fill_otp_fields(driver, otp_code):
            time.sleep(1)
            
            click_if_exists(driver, By.XPATH, "//button[contains(normalize-space(.), 'Valider')]", timeout=5)
            time.sleep(3)
            
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
            
            active_sessions[session_id]['step'] = 'complete'
            screenshot = get_screenshot(driver)
            
            return jsonify({
                'success': True,
                'screenshot': screenshot,
                'logged_in': logged_in,
                'url': driver.current_url
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to enter OTP'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cleanup', methods=['POST'])
def cleanup():
    session_id = flask_session.get('session_id')
    
    if session_id and session_id in active_sessions:
        try:
            active_sessions[session_id]['driver'].quit()
            del active_sessions[session_id]
        except:
            pass
    
    flask_session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
