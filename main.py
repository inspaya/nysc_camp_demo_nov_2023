from os import environ
from sqlite3 import connect, Cursor
from json import loads, dumps
from uuid import uuid4
from typing import Union
from datetime import datetime

from pytz import timezone
from requests import post
from fastapi import FastAPI, Request

app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/demo", redoc_url=None)

RECHARGE_URL = f"{environ['SERVICE_BASE_URL']}pay"
CONFIRM_URL = f"{environ['SERVICE_BASE_URL']}requery"

# Create DB and tables for the app
conn = connect("nysc_camp_demo.db")
cursor = Cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS beneficiaries(request_id UNIQUE, phone_no NOT NULL, status NOT NULL, response_message)
""")


def _generate_request_id(phone_number: str) -> str:
    africa_lagos = timezone("Africa/Lagos")
    _current_time = datetime.now(africa_lagos)
    current_time = _current_time.strftime("%Y%m%d%H%M")
    random_uuid = str(uuid4())
    request_id = f"{current_time}{random_uuid}{phone_number}".replace("-", "")
    return request_id


def _check_phone_number_first_visit(phone_number: str) -> bool:
    parameter = (phone_number,)
    phone_check = cursor.execute("SELECT * FROM beneficiaries WHERE phone_no == ?", parameter)
    if phone_check.fetchone() is None:
        return False
    else:
        return True
    
def _save_phone_number(**transaction_details) -> bool:
    try:
        parameters = (
            transaction_details["request_id"],
            transaction_details["phone_number"],
            transaction_details["status"],
            transaction_details["response_message"],
        )
        phone_save = cursor.execute("""
            INSERT INTO beneficiaries(request_id, phone_no, status, response_message) 
            VALUES()
        """, parameters)
        phone_save.commit()
    except Exception as saveException:
        print(f"An error occurred. See {saveException}")


def _phone_number_is_valid(phone_number: str) -> bool:
    return True


def _determine_network_from_phone_number(phone_number: str) -> Union[str | None]:
    valid_network_prefixes = {
        "glo": ["0805", "0705", "0811", "0815", "0905", "0807"],
        "mtn": ["0706", "0814", "0816", "0903", "0803", "0806", "0702", "0810", "0801"],
        "airtel": ["0902", "0808", "0802", "0901", "0812", "0708", "0911", "0912"],
        "etisalat": ["0817", "0818", "0909", "0809"]  # a.k.a 9Mobile
    }

    matched_network = None

    for network, prefixes in valid_network_prefixes.items():
        if phone_number[0:4] in prefixes:
            matched_network = network
            break

    return matched_network


@app.get("/", include_in_schema=False)
async def index():
    pass


@app.post("/recharge", include_in_schema=True)
async def recharge(request: Request):
    _request_payload = await request.json()
    phone_number = _request_payload["phone_number"]
    if _phone_number_is_valid(phone_number) and _check_phone_number_first_visit(phone_number):
        _request_id = _generate_request_id(phone_number)
        recharge_body = {
            "request_id": _request_id,
            "serviceID": _determine_network_from_phone_number(phone_number),
            "amount": 5.0,
            "phone": phone_number
        }

        recharge_headers = {
            "api-key": environ["API_KEY"],
            "secret-key": environ["SECRET_KEY"],
            "Content-type": "application/json"
        }

        recharge_response = post(
            url=RECHARGE_URL, headers=recharge_headers, data=dumps(recharge_body)
        )

        print(
            recharge_body,
            recharge_response
        )

        _response = loads(recharge_response.text)
        _response_description = _response["response_description"]
        if _response_description == "TRANSACTION SUCCESSFUL":
            transaction = {
                "request_id": _request_id,
                "phone_number": phone_number,
                "status": _response["content"]["transactions"]["status"],
                "response_message": _response_description
            }
            _save_phone_number(**transaction)
            _amount = _response["amount"]
            _parsed_response = f"Congrats! iSTEMLabs.Africa credited your number {phone_number} with N{_amount}."
            return {"data": _parsed_response}
        else:
            return {"data": f"Sorry, {_response_description}!"}
    else:
        return {"data": "Sorry, invalid phone number provided"}


@app.post("/confirm", include_in_schema=False)
async def confirm(recharge_request_id: str):
    pass
