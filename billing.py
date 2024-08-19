from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db,app,jwt
from models import BillingDetail

billing_bp = Blueprint('billing', __name__)
# Initialize JWT
def init_jwt(app):
    jwt.init_app(app)


@billing_bp.route('/billing_details', methods=['POST'])
@jwt_required()
def add_billing_details():
    user_id = get_jwt_identity()
    data = request.get_json()

    full_name = data.get('full_name')
    address_line_1 = data.get('address_line_1')
    address_line_2 = data.get('address_line_2')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    country = data.get('country')
    phone_number = data.get('phone_number')
    email = data.get('email')

    if not all([full_name, address_line_1, city, state, postal_code, country, phone_number, email]):
        return jsonify({'msg': 'Missing required fields'}), 400

    billing_details = BillingDetail(
        user_id=user_id,
        full_name=full_name,
        address_line_1=address_line_1,
        address_line_2=address_line_2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        phone_number=phone_number,
        email=email
    )
    db.session.add(billing_details)
    db.session.commit()

    return jsonify(billing_details.serialize()), 201

@billing_bp.route('/billing_details', methods=['GET'])
@jwt_required()
def get_billing_details():
    user_id = get_jwt_identity()
    billing_details = BillingDetail.query.filter_by(user_id=user_id).first()

    if not billing_details:
        return jsonify({'msg': 'Billing details not found'}), 404

    return jsonify(billing_details.serialize()), 200

@billing_bp.route('/billing_details', methods=['PUT'])
@jwt_required()
def update_billing_details():
    user_id = get_jwt_identity()
    data = request.get_json()

    billing_details = BillingDetail.query.filter_by(user_id=user_id).first()

    if not billing_details:
        return jsonify({'msg': 'Billing details not found'}), 404

    if 'full_name' in data:
        billing_details.full_name = data['full_name']
    if 'address_line_1' in data:
        billing_details.address_line_1 = data['address_line_1']
    if 'address_line_2' in data:
        billing_details.address_line_2 = data['address_line_2']
    if 'city' in data:
        billing_details.city = data['city']
    if 'state' in data:
        billing_details.state = data['state']
    if 'postal_code' in data:
        billing_details.postal_code = data['postal_code']
    if 'country' in data:
        billing_details.country = data['country']
    if 'phone_number' in data:
        billing_details.phone_number = data['phone_number']
    if 'email' in data:
        billing_details.email = data['email']

    db.session.commit()

    return jsonify(billing_details.serialize()), 200

@billing_bp.route('/billing_details', methods=['DELETE'])
@jwt_required()
def delete_billing_details():
    user_id = get_jwt_identity()
    billing_details = BillingDetail.query.filter_by(user_id=user_id).first()

    if not billing_details:
        return jsonify({'msg': 'Billing details not found'}), 404

    db.session.delete(billing_details)
    db.session.commit()

    return '', 204
