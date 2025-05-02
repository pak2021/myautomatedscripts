from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from webdriver_manager.chrome import ChromeDriverManager

def send_email(subject, body):

    recipient_email = os.getenv("TO_EMAIL_USER")

    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use 465 for SSL or 587 for TLS
        server.starttls()  # Start TLS encryption

        server.login(from_email, password)

        text = msg.as_string()
        server.sendmail(from_email, recipient_email, text)

        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    finally:
        server.quit()

print("Installing ChromeDriver...")
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")

print("Starting scrape.")
driver = webdriver.Chrome(service=service, options=options)

product_url = os.getenv("PRODUCT_URL")
driver.get(product_url)

wait = WebDriverWait(driver, 10)

input_box = wait.until(EC.visibility_of_element_located((By.ID, "search")))
input_box.clear()
input_box.send_keys("500075")

first_result = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#automatic .searchitem-name'))
)
first_result.click()

add_to_cart_button = wait.until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.add-to-cart'))
)

should_send_mail = False
error = ""
try:
    sold_out_element = wait.until(
        lambda driver: driver.find_element(By.CSS_SELECTOR, 'div.alert.alert-danger.mt-3') 
                      and driver.find_element(By.CSS_SELECTOR, 'div.alert.alert-danger.mt-3').text == "Sold Out"
    )
    should_send_mail = False
except TimeoutException:
    should_send_mail = True
except Exception as e:
    should_send_mail = True
    error = str(e)

if should_send_mail:
    print("Sending email.")
    if error != "":
        body = error
        subject = "Amul script error"
    else:
        body = product_url
        subject = "Amul Product Available Alert"
    send_email(subject, body)

driver.quit()