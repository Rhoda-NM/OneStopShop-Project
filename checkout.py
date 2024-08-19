from flask import Flask, request, jsonify, Blueprint
from flask_restful import Api, Resource, reqparse
import requests
from requests.auth import HTTPBasicAuth
import base64
import datetime
import json

checkout_bp = Blueprint('checkout_bp', __name__ )
checkout_api = Api(checkout_bp)

# MPESA credentials
consumer_key = "rqfepkWeiP3heS73MkIxFOGHkLCMTq5zlfthTP8dFBap0ahf"
consumer_secret = "2Q90mcq3Gq13AdKK25jCsHpQQbj6G8kD420CHPWKKIl4W9cmAS9gkLZK8aEUrRGq"
business_short_code = "174379"
lipa_na_mpesa_online_passkey = "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwODE4MTIzNDIx"

# Generate MPESA access token
def get_mpesa_token():
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return r.json()['access_token']

# Helper function to generate the Lipa Na MPESA password
def generate_password():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = business_short_code + lipa_na_mpesa_online_passkey + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')
    return encoded_string, timestamp


# STK Push Resource
class MakeSTKPush(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type=str, required=True, help="Phone number is required")
    parser.add_argument('amount', type=str, required=True, help="Amount is required")

    def post(self):
        try:
            # Get the access token
            access_token = get_mpesa_token()

            # Generate the password and timestamp
            password, timestamp = generate_password()

            # Prepare the headers for the STK push request
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Parse the request data
            data = MakeSTKPush.parser.parse_args()

            # Prepare the STK push request data
            request_data = {
                "BusinessShortCode": "174379",
                "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwODE4MTIzNDIx",
                "Timestamp": "20240818123421",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data['amount'],
                "PartyA": data['phone'],
                "PartyB": "174379",
                "PhoneNumber": data['phone'],
                "CallBackURL": "https://yourdomain.com/mpesa/callback",
                "AccountReference": "OneStop",
                "TransactionDesc": "Payment for order"
            }

            # Make the STK push request
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            response = requests.post(api_url, json=request_data, headers=headers)

            # Check if the request was successful
            if response.status_code > 299:
                return {
                    "success": False,
                    "message": "Sorry, something went wrong. Please try again later."
                }, 400

            # Parse the response and return to the user
            response_data = json.loads(response.text)
            return {
                "data": response_data
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": f"Sorry, something went wrong. Error: {str(e)}"
            }, 500


# Callback Resource
class MpesaCallback(Resource):
    def post(self):
        try:
            # Retrieve the JSON data sent by Safaricom
            mpesa_response = request.get_json()

            # Extract useful fields
            result_code = mpesa_response['Body']['stkCallback']['ResultCode']
            result_description = mpesa_response['Body']['stkCallback']['ResultDesc']
            merchant_request_id = mpesa_response['Body']['stkCallback']['MerchantRequestID']
            checkout_request_id = mpesa_response['Body']['stkCallback']['CheckoutRequestID']

            # Check if the transaction was successful
            if result_code == 0:  # Success
                # Extract transaction details
                amount = mpesa_response['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
                phone_number = mpesa_response['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']

                # Update your database with the transaction details
                # Here, you can mark the order as paid, or do any other processing based on the transaction
                # Example:
                # update_order_status(merchant_request_id, checkout_request_id, amount, phone_number)

                return jsonify({
                    "success": True,
                    "message": "Transaction successful",
                    "amount": amount,
                    "phone_number": phone_number
                }), 200
            else:
                # Handle failure case
                return jsonify({
                    "success": False,
                    "message": result_description
                }), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Add the resources to the API
checkout_api.add_resource(MakeSTKPush, "/stkpush")
checkout_api.add_resource(MpesaCallback, "/mpesa/callback")


