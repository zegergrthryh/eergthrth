# Damancom Login Automation

## Overview

This is a Flask web application that automates the login process for damancom.ma (a Moroccan insurance/healthcare portal). The application runs Chrome driver on the server (headless mode) and streams the browser view to users through a web interface.

The automation handles the complete login flow including username/password entry and OTP (One-Time Password) verification. Users interact with the server-side browser through a clean web interface, entering credentials step-by-step while viewing real-time screenshots of the automation process.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Server-Side Browser Streaming**
- Flask web application with single-page interface (viewer.html)
- Real-time screenshot streaming from server-side Selenium browser to web client
- Split-panel design: control sidebar (left) and browser view (right)
- Step-by-step credential input with visual feedback
- JavaScript-based screenshot refresh every 2 seconds during active sessions

**Session Management**
- Flask sessions with randomly generated secret keys
- Active browser sessions stored in `active_sessions` dictionary with session_id keys
- Each session tracks: Selenium driver instance, current step, and status
- No persistent storage of credentials - security by design

### Backend Architecture

**Browser Automation Layer**
- Selenium WebDriver running headless Chrome on server
- Runs at 1280x720 resolution for optimal screenshot clarity
- Implements anti-detection measures (custom user agent, webdriver property masking)
- Explicit WebDriverWait conditions ensure each login step completes before advancing
- Screenshot capture using Pillow (PIL) for image processing and base64 encoding

**Modular Helper Functions**
- `try_find()` - Wrapper for element location with timeout handling
- `click_if_exists()` - Attempts element click with JavaScript fallback
- `fill_input_if_exists()` - Tries multiple selectors to accommodate DOM variations
- `fill_otp_fields()` - Handles multi-field OTP input patterns
- `get_screenshot()` - Captures and optimizes browser screenshots
- `create_driver()` - Initializes configured Chrome WebDriver instance

**Login Flow with Explicit Waits**
1. **Username Step**: Fills username, clicks "Suivant", waits for password field to appear
2. **Password Step**: Fills password, clicks "Suivant/Continuer", waits for all 6 OTP fields to appear
3. **OTP Step**: Fills 6-digit code, clicks "Valider", checks for login success indicators

**Error Handling Strategy**
- Each step validates button clicks and waits for next page to load
- TimeoutException handling for pages that fail to load
- JSON error responses with descriptive messages
- Session cleanup on errors to prevent resource leaks

### External Dependencies

**Browser Automation**
- **Selenium (4.36.0)** - WebDriver for browser control
- **undetected-chromedriver (3.5.5)** - Evades bot detection systems on target website

**Web Framework**
- **Flask** - Lightweight WSGI web application framework for the browser-based interface
- Handles routing, session management, and template rendering

**GUI Framework**  
- **Tkinter** - Python's standard GUI library (built-in, no installation required)
- Provides cross-platform desktop application capabilities

**Image Processing**
- **Pillow (PIL)** - Python Imaging Library for screenshot capture and manipulation
- Used in web interface to provide browser viewport visualization

**Target Website**
- **damancom.ma** - Moroccan healthcare/insurance portal
- Requires username/password authentication followed by OTP verification
- Implements bot detection that blocks standard headless browsers
- URL: https://www.damancom.ma/fr/authentification

**Runtime Requirements**
- Chrome/Chromium browser must be installed on the system
- ChromeDriver is managed automatically by undetected-chromedriver