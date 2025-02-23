from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import *
from fake_useragent import UserAgent
import time
import json

# Set a default global wait_time value.
wait_time = 10

# Sets up the driver, prevents detection, and visits a website if provided.
def set_up_driver(website="", wt=10, hide_selenium=True, use_tor=False, headless=False, crash_prevention=True, no_sandbox=False, print_extra=False, add_toolbar=True):
    global user_agent, driver, wait_time
    # Assign the wait time parameter to the global variable.
    wait_time = wt

    options = Options()
    service = Service(ChromeDriverManager().install())

    if no_sandbox:
        options.add_argument('--no-sandbox')

    if hide_selenium:
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--incognito")
        user_agent = UserAgent().random
        options.add_argument(f'user-agent={user_agent}')  # Spoof the user agent
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    
    if crash_prevention:
        options.add_argument('--disable-dev-shm-usage')
    
    if use_tor:
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')

    if headless:
        options.add_argument('--headless')

    driver = webdriver.Chrome(options=options, service=service)

    # Hide webdriver flags and fingerprinting (as before)
    if hide_selenium:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            // 1. Hide WebDriver flag
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // 2. Fake Touch Support
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
            // 3. Fake Network Information
            Object.defineProperty(navigator.connection, 'rtt', {get: () => 100});
            // 4. Spoof Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' || parameters.name === 'midi' || parameters.name === 'camera' 
                    ? Promise.resolve({ state: 'granted' }) 
                    : originalQuery(parameters)
            );
            // 5. Prevent WebRTC Leaks
            Object.defineProperty(window, 'RTCPeerConnection', {
                get: () => function() { return null; }
            });
            // 6. Patch Canvas Fingerprint Detection
            HTMLCanvasElement.prototype.toDataURL = (function(original) {
                return function(...args) {
                    return original.apply(this, args);
                };
            })(HTMLCanvasElement.prototype.toDataURL);
            // 7. Modify WebGL Vendor & Renderer
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return "Intel Open Source Technology Center";
                if (parameter === 37446) return "Mesa DRI Intel(R) HD Graphics 620";
                return getParameter(parameter);
            };
            """
        })

    # Inject the toolbar script on every new document if enabled.
    if add_toolbar:
        toolbar_injection_script = r"""
        window.addEventListener('DOMContentLoaded', function(){
            if (!document.getElementById('selenium-toolbar-icon')) {
                // Create a small toolbar icon at the top-right corner.
                var toolbarIcon = document.createElement('div');
                toolbarIcon.id = 'selenium-toolbar-icon';
                toolbarIcon.style.position = 'fixed';
                toolbarIcon.style.top = '10px';
                toolbarIcon.style.right = '10px';
                toolbarIcon.style.width = '40px';
                toolbarIcon.style.height = '40px';
                toolbarIcon.style.backgroundColor = '#333';
                toolbarIcon.style.color = '#fff';
                toolbarIcon.style.borderRadius = '5px';
                toolbarIcon.style.display = 'flex';
                toolbarIcon.style.alignItems = 'center';
                toolbarIcon.style.justifyContent = 'center';
                toolbarIcon.style.cursor = 'pointer';
                toolbarIcon.style.zIndex = '999999';
                toolbarIcon.innerText = '☰';
                document.body.appendChild(toolbarIcon);

                // Create the full toolbar container (initially hidden).
                var toolbar = document.createElement('div');
                toolbar.id = 'selenium-toolbar';
                toolbar.style.position = 'fixed';
                toolbar.style.top = '60px';
                toolbar.style.right = '10px';
                toolbar.style.backgroundColor = '#333';
                toolbar.style.color = '#fff';
                toolbar.style.padding = '10px';
                toolbar.style.zIndex = '999999';
                toolbar.style.fontFamily = 'Arial, sans-serif';
                toolbar.style.display = 'none';
                toolbar.innerHTML = '<button id="toggle-highlight" style="cursor:pointer;">Enable Element Highlight</button>';
                document.body.appendChild(toolbar);

                // Toggle full toolbar visibility when the icon is clicked.
                toolbarIcon.addEventListener('click', function(e){
                    if (toolbar.style.display === 'none') {
                        toolbar.style.display = 'block';
                    } else {
                        toolbar.style.display = 'none';
                    }
                });

                // Optionally, allow right-click to toggle toolbar.
                document.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    if (toolbar.style.display === 'none') {
                        toolbar.style.display = 'block';
                    } else {
                        toolbar.style.display = 'none';
                    }
                });

                var highlightMode = false;
                // Computes a basic CSS selector for an element.
                function getCssSelector(el) {
                    if (el.id) return '#' + el.id;
                    var path = [];
                    while (el.nodeType === Node.ELEMENT_NODE) {
                        var selector = el.nodeName.toLowerCase();
                        if (el.className) {
                            var classes = el.className.trim().split(/\s+/);
                            if (classes.length) {
                                selector += '.' + classes.join('.');
                            }
                        }
                        var sibling = el;
                        var nth = 1;
                        while (sibling = sibling.previousElementSibling) {
                            if (sibling.nodeName.toLowerCase() == el.nodeName.toLowerCase()) {
                                nth++;
                            }
                        }
                        selector += ":nth-of-type(" + nth + ")";
                        path.unshift(selector);
                        el = el.parentNode;
                    }
                    return path.join(" > ");
                }
                // Highlight element on mouseover.
                function mouseOverHandler(e) {
                    e.target.style.outline = '2px solid red';
                    e.stopPropagation();
                }
                // Remove highlight on mouseout.
                function mouseOutHandler(e) {
                    e.target.style.outline = '';
                    e.stopPropagation();
                }
                // On click, copy the computed selector to clipboard and disable highlight mode.
                function clickHandler(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var selector = getCssSelector(e.target);
                    navigator.clipboard.writeText(selector).then(function() {
                        alert("Copied selector: " + selector);
                    }, function(err) {
                        alert("Failed to copy selector: " + err);
                    });
                    disableHighlightMode();
                }
                function enableHighlightMode() {
                    highlightMode = true;
                    document.body.addEventListener('mouseover', mouseOverHandler, true);
                    document.body.addEventListener('mouseout', mouseOutHandler, true);
                    document.body.addEventListener('click', clickHandler, true);
                    document.getElementById('toggle-highlight').innerText = 'Disable Element Highlight';
                }
                function disableHighlightMode() {
                    highlightMode = false;
                    document.body.removeEventListener('mouseover', mouseOverHandler, true);
                    document.body.removeEventListener('mouseout', mouseOutHandler, true);
                    document.body.removeEventListener('click', clickHandler, true);
                    document.getElementById('toggle-highlight').innerText = 'Enable Element Highlight';
                }
                document.getElementById('toggle-highlight').addEventListener('click', function(e){
                    e.preventDefault();
                    if (!highlightMode) {
                        enableHighlightMode();
                    } else {
                        disableHighlightMode();
                    }
                });
            }
        });
        """
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": toolbar_injection_script})

    if website != "":
        if not website.startswith("http"):
            website = "https://" + website

        try:
            driver.get(website)
            if print_extra:
                print(f"Visiting {website} with UserAgent: {user_agent}")
            return driver
        except WebDriverException as e:
            if use_tor:
                print("TOR isn't configured. Run 'tor &' in terminal.")
            else:
                print(e)
            quit()
    else:
        return driver

def keep_awake():
    time.sleep(9999999)
    driver.quit()

#
# ELEMENT LOCATORS
#

def find(elementidentifier):
    if not isinstance(elementidentifier, str):
        return "The input is not a string."

    # Determine locator type: XPATH vs CSS vs ID.
    if elementidentifier.startswith('/') or elementidentifier.startswith('(') or elementidentifier.startswith('//'):
        loc_type = By.XPATH
    else:
        if '#' in elementidentifier or '.' in elementidentifier or '[' in elementidentifier:
            loc_type = By.CSS_SELECTOR
        else:
            loc_type = By.ID

    element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((loc_type, elementidentifier)))
    # Scroll element into view and adjust (if needed) to avoid overlap.
    driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -60);", element)
    WebDriverWait(driver, wait_time).until(EC.visibility_of(element))
    if not element.is_displayed():
        print(f"Error: Element {elementidentifier} is not visible.")
        quit()
    if not element.is_enabled():
        print(f"Error: Element {elementidentifier} is not enabled.")
        quit()
    return element

def find_by_text(text, tag='*'):
    xpath = f"//{tag}[contains(text(), '{text}')]"
    try:
        element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true); window.scrollBy(0, -60);", element)
        WebDriverWait(driver, wait_time).until(EC.visibility_of(element))
        if not element.is_displayed():
            print(f"Error: Element with text '{text}' is not visible.")
            quit()
        if not element.is_enabled():
            print(f"Error: Element with text '{text}' is not enabled.")
            quit()
        return element
    except TimeoutException:
        print(f"Error: Element with text '{text}' not found.")
        return None

#
# EXTRA FUNCTIONS
#

def get_info(show=True, headless=True, use_tor=False):
    try:
        set_up_driver(website="https://ipinfo.io/json", use_tor=use_tor, headless=headless, add_toolbar=False)
        raw_data = driver.find_element(By.TAG_NAME, "pre").text
        data = json.loads(raw_data)
        user_agent = driver.execute_script("return navigator.userAgent;")
        driver.quit()
        ip_info = {
            "IP": data.get('ip', 'Unknown'),
            "Org": data.get('org', 'Unknown'),
            "Hostname": data.get('hostname', 'Unknown'),
            "Latitude": float(data['loc'].split(',')[0]),
            "Longitude": float(data['loc'].split(',')[1]),
            "City": data.get('city', 'Unknown'),
            "State": data.get('region', 'Unknown'),
            "Country": data.get('country', 'Unknown'),
            "Postal": data.get('postal', 'Unknown'),
            "Timezone": data.get('timezone', 'Unknown'),
            "User-Agent": user_agent
        }
        if show:
            print(f"\nIP Address: {ip_info['IP']},\n{ip_info['Org']}, Hostname: {ip_info['Hostname']},\n"
                  f"Latitude: {ip_info['Latitude']}, Longitude: {ip_info['Longitude']},\n"
                  f"City: {ip_info['City']}, {ip_info['State']}, {ip_info['Country']}\n"
                  f"Postal Code: {ip_info['Postal']}, Time zone: {ip_info['Timezone']}\n"
                  f"User-Agent: {ip_info['User-Agent']}\n")
        return ip_info
    except Exception as e:
        print(f"Error: {e}")
        exit()
        return False

def click_button(identifier):
    """Waits for an element to be clickable and clicks it."""
    try:
        # Explicitly wait until the element is clickable.
        element = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, identifier))
        )
        element.click()
        return True
    except TimeoutException:
        print(f"Error: Timed out waiting for '{identifier}' to be clickable.")
    except Exception as e:
        print(f"Error: Could not click '{identifier}' due to: {e}")
    return False

def fill_text(identifier, text):
    """Finds a text field and enters text."""
    try:
        element = find(identifier)
        if element:
            element.clear()
            element.send_keys(text)
            return True
        else:
            print(f"Error: Text field '{identifier}' not found.")
            return False
    except TimeoutException:
        print(f"Error: Timed out waiting for text field '{identifier}' to be interactable.")
    except Exception as e:
        print(f"Error: Could not enter text in '{identifier}' due to: {e}")
    return False

def select_dropdown(identifier, option_text):
    """Finds a dropdown and selects an option by visible text."""
    try:
        element = find(identifier)
        if element:
            select = Select(element)
            select.select_by_visible_text(option_text)
            return True
        else:
            print(f"Error: Dropdown '{identifier}' not found.")
            return False
    except TimeoutException:
        print(f"Error: Timed out waiting for dropdown '{identifier}' to be selectable.")
    except Exception as e:
        print(f"Error: Could not select '{option_text}' in dropdown '{identifier}' due to: {e}")
    return False