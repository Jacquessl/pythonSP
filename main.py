import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import time

COOKIES_FILE_PATH = "sciezka/do/pliku/cookies.txt"


def skinport_script(driver):
    global checkout_btn, discount_value, discountElement
    aborted = False
    discount_value = None
    discountElement = None
    checkout_btn = None
    while not aborted:
        try:
            live_btn = driver.find_element(By.CLASS_NAME, "LiveBtn")
            if "LiveBtn--isActive" not in live_btn.get_attribute("class"):
                live_btn.click()
            time.sleep(10)
            item_containers = driver.find_elements(By.CSS_SELECTOR, "div.CatalogPage-item--grid")

            for container in item_containers:
                priceElement = container.find_element(By.CSS_SELECTOR, "div.ItemPreview-priceValue")
                try:
                    discountElement = container.find_element(By.CSS_SELECTOR, "div.GradientLabel.ItemPreview-discount")
                    discount_value = extract_discount_value(discountElement.text)
                except Exception:
                    discount_value = 0
                    pass
                if priceElement is not None and discountElement is not None:
                    cleaned_price_string = przyciac_stringa(priceElement.text)
                    current_price = float(cleaned_price_string)
                    # print(current_price)
                    if 10 < current_price < 10000 and discount_value >= 20:
                        add_to_cart_button = container.find_element(By.CLASS_NAME, "ItemPreview-mainAction")
                        if add_to_cart_button is not None:
                            ActionChains(driver).move_to_element(container).perform()
                            add_to_cart_button.click()

                            driver.get("https://skinport.com/pl/cart")
                            wait_until_url_change(driver, "https://skinport.com/pl/market?sort=date&order=desc")
                            print("123")
                            time.sleep(0.2)
                            WebDriverWait(driver, 1).until(
                                ec.presence_of_element_located((By.XPATH, "//input[@name='cancellation']")))
                            checkboxes = driver.find_elements(By.XPATH, "//input[@name='cancellation']")
                            checkboxes2 = driver.find_elements(By.XPATH, "//input[@name='tradelock']")
                            print("1234")
                            for checkbox in checkboxes:
                                checkbox.click()
                            for checkbox in checkboxes2:
                                checkbox.click()
                            checkout_btn = driver.find_element(By.CSS_SELECTOR,
                                                               "button.SubmitButton.CartSummary-checkoutBtn")
                            if checkout_btn is not None:
                                checkout_btn.click()
                                WebDriverWait(driver, 10).until(ec.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div/div[1]/div/ul/li[1]/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/span[1]/iframe")))
                                WebDriverWait(driver, 10).until(
                                   ec.element_to_be_clickable((By.XPATH, "/html/body/div/input"))).send_keys("425")
                                driver.switch_to.default_content()
                                WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[4]/div[2]/div[1]/div[2]/div/div[1]/div/ul/li[1]/div[2]/div[2]/button"))).click()
                                break
                            time.sleep(10)
        except Exception as E:
            pass

def extract_discount_value(discount_text):
    digits = ''.join(filter(str.isdigit, discount_text))
    return int(digits) if digits else 0


def przyciac_stringa(s):
    result = ''
    found_digit = False

    for char in s:
        if char.isdigit():
            result += char
            found_digit = True
        elif found_digit:
            break

    return result


def wait_until_url_change(driver, old_url):
    WebDriverWait(driver, 0.1).until(ec.url_changes(old_url))


def load_cookies_from_file(driver, file_path):
    try:
        with open(file_path, "r") as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True
    except FileNotFoundError:
        return False


def save_cookies_to_file(driver, file_path):
    cookies = driver.get_cookies()
    with open(file_path, "w") as f:
        f.write(json.dumps(cookies))


file_path = "cookies.json"


def main():
    chOptions = uc.ChromeOptions()
    profile = "Profile 3"
    chOptions.add_argument(f"--user-data-dir={profile}")
    chOptions.add_argument("--remote-debugging-port=9292")
    driver = uc.Chrome(
        driver_executable_path="C:\\Users\\litwi\\Desktop\\skinport\\chromedriver-win64\\chromedriver.exe",
        options=chOptions)
    driver.get("https://skinport.com/pl/market?sort=date&order=desc")

    try:
        time.sleep(30)
        skinport_script(driver)
        time.sleep(60000)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
