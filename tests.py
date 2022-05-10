import pytest, pytest_html, time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.request
import json
from datetime import datetime

base_domain = "http://192.168.64.5:8000"
email_base = 'info+selenium_%s@timparkin.co.uk'

#Fixture for Chrome
@pytest.fixture(scope="class")
def chrome_driver_init(request):
    chrome_driver = webdriver.Chrome()
    request.cls.driver = chrome_driver
    yield
    chrome_driver.close()

@pytest.mark.usefixtures("chrome_driver_init")
class BasicTest:
    pass

def signup(d, email):
    d.get(base_domain + "/accounts/signup/?next=/")
    d.set_window_size(1728, 1079)
    d.find_element(By.ID, "id_email").send_keys(email)
    d.find_element(By.ID, "id_password1").send_keys("password")
    d.find_element(By.ID, "id_first_name").send_keys("Tim")
    d.find_element(By.ID, "id_last_name").send_keys("Parkin")
    d.find_element(By.ID, "id_date_of_birth").send_keys("18121966")
    d.find_element(By.ID, "id_website").send_keys("http://timparkin.net")
    d.find_element(By.ID, "id_facebook").send_keys("facebook")
    d.find_element(By.ID, "id_instagram").send_keys("instgram")
    d.find_element(By.ID, "id_twitter").send_keys("twitter")
    d.find_element(By.ID, "signupbutton").click()


def pay_with_stripe(d):
    # Pay using Stripe
    wait = WebDriverWait(d, 30)
    wait.until(lambda driver: 'stripe' in driver.current_url)
    # Stripe payment
    d.find_element(By.ID, "email").click()
    d.find_element(By.ID, "email").send_keys("info@timparkin.co.uk")
    d.find_element(By.ID, "cardNumber").send_keys("4242424242424242")
    d.find_element(By.ID, "cardExpiry").send_keys("0134")
    d.find_element(By.ID, "cardCvc").send_keys("123")
    d.find_element(By.ID, "billingName").send_keys("Tim Parkin")
    d.find_element(By.ID, "billingPostalCode").send_keys("PH494JG")
    d.find_element(By.CSS_SELECTOR, ".SubmitButton-CheckmarkIcon path").click()
    # Focus on new page (confirmig payment) and then redirect to image uploads
    d.find_element(By.CSS_SELECTOR, "html").click()

def get_verification_link():
    # check for the verification email
    request = urllib.request.Request('https://mailtrap.io/api/v1/inboxes/1726664/messages?search=&page=&last_id=&api_token=2e49788b3bc4c88461d761471e713342')
    response = urllib.request.urlopen(request)
    emails = json.loads(response.read().decode('utf-8'))
    to_email = emails[0]['to_email']
    txt_path = emails[0]['txt_path']
    request = urllib.request.Request('https://mailtrap.io/%s?api_token=2e49788b3bc4c88461d761471e713342'%txt_path)
    response = urllib.request.urlopen(request)
    body_text = response.read().decode('utf-8')
    verification_link = 'http%s'%body_text.split('http')[1]
    return verification_link

class Test_URL(BasicTest):
    def test_register(self):
        uninow = datetime.strftime(datetime.utcnow(), "%Y-%m-%d-%H-%M")
        email = email_base%uninow

        signup(self.driver, email)

        verification_link = get_verification_link()
        # click on verification link
        self.driver.get(verification_link)
        time.sleep(3)

        # Purchase 12 images
        self.driver.find_element(By.CSS_SELECTOR, ".btn-lg").click()
        # Confirm Purchase
        self.driver.find_element(By.ID, "submitBtn").click()

        pay_with_stripe(self.driver)

        wait = WebDriverWait(self.driver, 30)
        wait.until(lambda driver: 'stripe' not in driver.current_url)
        # CONFIRM PAYMENT SUCCESSFUL
        assert self.driver.find_element(By.CSS_SELECTOR, "h3").text == "Payment Successful"

        # PAUSE SO I CAN SITE AND WAIT ON THE PURCHASE CHOICES PAGE
        time.sleep(1000000)

        self.driver.find_element(By.NAME, "entry_set-0-photo").click()
        self.driver.find_element(By.NAME, "entry_set-0-photo").send_keys("C:\\fakepath\\IMG_1430.jpeg")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-outline-primary").click()
        self.driver.find_element(By.NAME, "entry_set-1-photo").click()
        self.driver.find_element(By.NAME, "entry_set-1-photo").send_keys("C:\\fakepath\\202211761_10159410105097436_500345951676843929_n.jpeg")
        self.driver.find_element(By.ID, "id_entry_set-1-category").click()
        dropdown = self.driver.find_element(By.ID, "id_entry_set-1-category")
        dropdown.find_element(By.XPATH, "//option[. = 'Intimate Landscapes']").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-outline-primary").click()
