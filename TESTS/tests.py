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
from mailtrap_apikey import mailtrap_api_token

#base_domain = "http://192.168.64.5:8000"
base_domain = "http://testing.naturallandscapeawards.com"
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
    mailtrap_url = 'https://mailtrap.io/api/v1/inboxes/1726664/messages?search=&page=&last_id=&api_token={}'.format(mailtrap_api_token)
    request = urllib.request.Request(mailtrap_url)
    response = urllib.request.urlopen(request)
    emails = json.loads(response.read().decode('utf-8'))
    to_email = emails[0]['to_email']
    txt_path = emails[0]['txt_path']
    payload_url = 'https://mailtrap.io/{}?api_token={}'.format(txt_path, mailtrap_api_token)
    request = urllib.request.Request(payload_url)
    response = urllib.request.urlopen(request)
    body_text = response.read().decode('utf-8')
    verification_link = 'http%s'%body_text.split('http')[1]
    return verification_link

entry_button_selector = {
1: '#choice-one .btn',
6: '#choice-six .btn',
12: '#choice-twelve .btn',
18: '#choice-eighteen .btn',
}

@pytest.mark.parametrize("num_entries", [1,6,12,18])
class Test_URL(BasicTest):
    def test_register(self, num_entries):
        uninow = datetime.strftime(datetime.utcnow(), "%Y-%m-%d-%H-%M")
        email = email_base%uninow

        signup(self.driver, email)

        verification_link = get_verification_link()
        # click on verification link
        self.driver.get(verification_link)
        wait = WebDriverWait(self.driver, 30)
        wait.until(lambda driver: 'paymentplan' in driver.current_url)

        # Click on Button for N images
        if num_entries != 12:
            self.driver.find_element(By.CSS_SELECTOR, entry_button_selector[num_entries]).click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-lg").click()
        # Confirm Purchase
        self.driver.find_element(By.ID, "submitBtn").click()

        pay_with_stripe(self.driver)

        wait = WebDriverWait(self.driver, 30)
        wait.until(lambda driver: 'stripe' not in driver.current_url)
        # CONFIRM PAYMENT SUCCESSFUL
        assert self.driver.find_element(By.CSS_SELECTOR, "h3").text == "Payment Successful"
        wait = WebDriverWait(self.driver, 30)
        wait.until(lambda driver: 'entries' in driver.current_url)

        # Assert we have the right number of images
        number_of_image_boxes = self.driver.find_elements(By.CSS_SELECTOR, ".p-card h5")
        assert len(number_of_image_boxes) == num_entries
        self.driver.get(base_domain + "/accounts/logout/")
        time.sleep(10)
        self.driver.find_element(By.CSS_SELECTOR, 'form button').click()
        time.sleep(10)

