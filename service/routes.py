"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    This endpoint will list all accounts
    """
    app.logger.info("Request to list all accounts")
    # Account.all() method to retrieve all accounts
    accounts = Account.all()
    # create a list of serialize() accounts
    account_list = [account.serialize() for account in accounts]
    # log the number of accounts in the list
    app.logger.info("Returning [%s] accounts, len(account_list)")
    # return the lists with status.HTTP_200_Ok
    return jsonify(account_list), status.HTTP_200_OK


######################################################################
# READ AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    This endpoint will read an Account with account_id
    """
    app.logger.info("Request to read an Account with id: %s", account_id)
    # Account.find() method to find the account
    account = Account.find(account_id)
    # Abort() with a status.HTTP_404_NOT_FOUND if it cannot be found
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account}] could not be found.")
    # return the serialize() version of the account with a return code of status.HTTP_200_OK
    return account.serialize(), status.HTTP_200_OK



######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    This endpoint will update an Account
    """
    app.logger.info("Request to update an Account with id: %s", account_id)
    # find method to get account by id
    account = Account.find(account_id)
    # return 404 not found if the account not found
    if not account:
        abort(status.HTTP_404_NOT_FOUND,f"Account with id [{account_id}] could not be found")
    account.deserialize(request.get_json())
    # update the account with the new data
    account.update()
    # return python dictionary with a return code of HTTP_200_OK
    return account.serialize(), status.HTTP_200_OK



######################################################################
# DELETE AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """This endpoint will delete an existing account"""
    app.logger.info("Request to delete an account with id: %s", account_id)
    # find() method to get account with id
    account = Account.find(account_id)
    # if found, call the delete() method
    if account:
        account.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
