from flask import Blueprint, request, jsonify
from models import BillingDetail, db

billing_bp = Blueprint('billing_bp', __name__)

# Create a new billing detail
@billing_bp.route('/billing', methods=['POST'])
def create_billing():
    data = request.get_json()
    new_billing = BillingDetail(
        user_id=data['user_id'],
        full_name=data['full_name'],
        address_line_1=data['address_line_1'],
        address_line_2=data.get('address_line_2'),
        city=data['city'],
        state=data['state'],
        postal_code=data['postal_code'],
        country=data['country'],
        phone_number=data['phone_number'],
        email=data['email']
    )
    db.session.add(new_billing)
    db.session.commit()
    return jsonify(new_billing.serialize()), 201

# Read all billing details
@billing_bp.route('/billing', methods=['GET'])
def get_all_billing():
    billing_details = BillingDetail.query.all()
    return jsonify([billing.serialize() for billing in billing_details]), 200

# Read a single billing detail by ID
@billing_bp.route('/billing/<int:id>', methods=['GET'])
def get_billing_by_id(id):
    billing = BillingDetail.query.get_or_404(id)
    return jsonify(billing.serialize()), 200

# Update a billing detail by ID
@billing_bp.route('/billing/<int:id>', methods=['PATCH'])
def update_billing(id):
    billing = BillingDetail.query.get_or_404(id)
    data = request.get_json()

    if 'full_name' in data:
        billing.full_name = data['full_name']
    if 'address_line_1' in data:
        billing.address_line_1 = data['address_line_1']
    if 'address_line_2' in data:
        billing.address_line_2 = data.get('address_line_2')
    if 'city' in data:
        billing.city = data['city']
    if 'state' in data:
        billing.state = data['state']
    if 'postal_code' in data:
        billing.postal_code = data['postal_code']
    if 'country' in data:
        billing.country = data['country']
    if 'phone_number' in data:
        billing.phone_number = data['phone_number']
    if 'email' in data:
        billing.email = data['email']

    db.session.commit()
    return jsonify(billing.serialize()), 200

# Delete a billing detail by ID
@billing_bp.route('/billing/<int:id>', methods=['DELETE'])
def delete_billing(id):
    billing = BillingDetail.query.get_or_404(id)
    db.session.delete(billing)
    db.session.commit()
    return jsonify({'message': 'Billing detail deleted successfully'}), 200
