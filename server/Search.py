from fuzzywuzzy import fuzz

def search_products(query, products, threshold=70):
    results = []

    for product in products:
        name_similarity = fuzz.partial_ratio(query.lower(), product['name'].lower())
        description_similarity = fuzz.partial_ratio(query.lower(), product['description'].lower())
        tags_similarity = max([fuzz.partial_ratio(query.lower(), tag['name'].lower()) for tag in product['tags']], default=0)

        # Calculate an overall similarity score
        overall_similarity = max(name_similarity, description_similarity, tags_similarity)

        if overall_similarity >= threshold:
            results.append({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'tags': product['tags'],
                'image_url': product['image_url'],
                'category': product['category'],
                'price': product['price'],
                'similarity_score': overall_similarity
            })

    # Sort results by similarity score in descending order
    results.sort(key=lambda x: x['similarity_score'], reverse=True)

    return results
