# search.py
from flask import Blueprint, request, jsonify
from models import Product
from sqlalchemy import or_

search_bp = Blueprint('search_bp', __name__, url_prefix='/api')

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    search_results = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.category.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).all()

    suggestions = get_search_suggestions(query)
    
    return jsonify({
        'results': [product.to_dict() for product in search_results],
        'suggestions': suggestions
    }), 200

def get_search_suggestions(query):
    # This is a placeholder implementation, you can use more advanced NLP techniques
    # such as using a library like spaCy or a search suggestion service.
    suggestions = []
    words = query.split()
    if len(words) > 1:
        for i in range(len(words)):
            suggestion = ' '.join(words[:i] + words[i+1:])
            suggestions.append(suggestion)
    return suggestions
