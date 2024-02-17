"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app
from service import talisman # import talisman from service

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

# Add https protocol
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        # disable https
        talisman.force_https = False
        
    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # TEST CASE FOR GET ACCOUNT
    def test_get_account(self):
        """It should Read a single Account"""
        # make a call to self.client.post() to create the account
        account = self._create_accounts(1)[0]
        # assert that the resp.status_code is status.HTTP_200_OK
        resp = self.client.get(
            f"{BASE_URL}/{account.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the data from resp.get_json()
        data = resp.get_json()
        # assert that data["name"] equals the account.name
        self.assertEqual(data["name"], account.name)

    # TEST CASE FOR ACCOUNT NOT FOUND
    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        # send a self.client.get() request to the BASE_URL with an invalid account number (0: account id)
        resp = self.client.get(f"{BASE_URL}/0")
        # assert that the resp.status_code is status.HTTP_404_NOT_FOUND
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # TEST CASE FOR ACCOUNT LIST
    def test_get_account_list(self):
        """It should get a list of Accounts"""
        self._create_accounts(7)
        # send a self.client.get() request to the BASE_URL
        resp = self.client.get(BASE_URL)
        # assert that the resp.status_code is status.HTTP_200_OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the data from resp.get_json()
        data = resp.get_json()
        # assert that the len() of the data is 5 (number of accounts created)
        self.assertEqual(len(data), 7)

    # TEST CASE FOR UPDATE ACCOUNT
    def test_update_account(self):
        """It should update an existing account"""
        # create an account to update
        test_account = AccountFactory()
        # send a self.client.post() request to the BASE_URL with json payload
        resp = self.client.post(BASE_URL, json=test_account.serialize())
        # assert resp with status.HTTP_201_CREATED
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the account
        new_account = resp.get_json()
        # change the new account name
        new_account["name"] = "Just for Test"
        # send a request to the BASE_URL with json payload
        resp = self.client.put(f"{BASE_URL}/{new_account['id']}", json=new_account)
        # assert the resp is status HTTP_200_OK
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the data as updated_account
        updated_account = resp.get_json()
        # assert the updated_account
        self.assertEqual(updated_account["name"], "Just for Test")

    # TEST CASE FOR DELETE ACCOUNT
    def test_delete_account(self):
        """It should delete an account"""
        account = self._create_accounts(1)[0]
        # send a request tot the BASE_URL with an id of an account
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        # assert that resp is status.HTTP_204_NO_CONTENT
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # TEST CASE FOR ERROR HANDLER
    def test_method_not_allowed(self):
        """It should not allow an illegal methods"""
        resp = self.client.delete(BASE_URL)
        # assert that resp is status.HTTP_405_METHOD_NOT_ALLOWED
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    
    ######################################################################
    #  SECURITY HEADERS
    ######################################################################
    # add security headers
    def test_security_headers(self):
        """It should return security headers"""
        # passing environ_overrides as a parameter
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        # assert with HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # headers content
        headers = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        # Adjusting the expectation for the Content-Security-Policy header
        'Content-Security-Policy': 'default-src \'self\'; object-src \'none\'',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        # headers items
        for key, value in headers.items():
            self.assertEqual(response.headers.get(key), value)

    # add CORS policies
    def test_cors_security(self):
        """It should return a CORS header"""
        # passing environ_overrides as a parameter
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        # assert with HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check for the CORS headers
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
