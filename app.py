from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib.parse
import time
import os

app = Flask(__name__)
# Using API key directly
API_KEY = os.getenv('API_NINJA_KEY')

def generate_food_image(recipe_name):
    try:
        clean_name = recipe_name.strip()
        return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_name)}%20food%20photo%20realistic"
    except Exception as e:
        print(f"Error generating image for {recipe_name}: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        return redirect(url_for('index', query=query))
    
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of recipes per page
    
    if query:
        # Make multiple related searches to get more recipes
        all_recipes = []
        search_terms = [query]
        
        # Add some variations to get more results
        if len(query.split()) == 1:  # If it's a single word query
            search_terms.append(f"{query} recipe")
            search_terms.append(f"{query} easy")
            search_terms.append(f"{query} homemade")
        
        # Fetch recipes for each search term
        for term in search_terms:
            encoded_term = urllib.parse.quote(term.strip())
            recipe_url = f'https://api.api-ninjas.com/v1/recipe?query={encoded_term}'
            
            print(f"Searching for: {term}")
            
            try:
                recipe_response = requests.get(
                    recipe_url, 
                    headers={'X-Api-Key': API_KEY},
                    timeout=15
                )
                
                if recipe_response.status_code == 200:
                    term_recipes = recipe_response.json()
                    print(f"Found {len(term_recipes)} recipes for term '{term}'")
                    
                    # Add recipes while avoiding duplicates
                    titles = [r['title'] for r in all_recipes]
                    for recipe in term_recipes:
                        if recipe['title'] not in titles:
                            all_recipes.append(recipe)
                            titles.append(recipe['title'])
                    
                    # Add a small delay to avoid rate limiting
                    time.sleep(1)
                else:
                    print(f"Failed search for '{term}': {recipe_response.status_code} - {recipe_response.text}")
            except Exception as e:
                print(f"Error searching for '{term}': {str(e)}")
        
        # Generate images for all recipes after collecting them
        for recipe in all_recipes:
            recipe['image_url'] = generate_food_image(recipe['title'])
            time.sleep(0.5)
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Handle edge cases for pagination
        if len(all_recipes) == 0:
            return render_template('index.html', error=f"No recipes found for '{query}'")
        
        if start_idx >= len(all_recipes):
            start_idx = 0
            end_idx = min(per_page, len(all_recipes))
            page = 1
        
        current_recipes = all_recipes[start_idx:end_idx]
        has_more = len(all_recipes) > end_idx
        
        return render_template('index.html', 
                            recipes=current_recipes, 
                            query=query,
                            page=page,
                            has_more=has_more,
                            total_recipes=len(all_recipes))
    
    return render_template('index.html')

@app.route('/test-api')
def test_api():
    try:
        test_url = 'https://api.api-ninjas.com/v1/recipe?query=pasta'
        response = requests.get(
            test_url, 
            headers={'X-Api-Key': API_KEY},
            timeout=10
        )
        return {
            'status_code': response.status_code,
            'response': response.text
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)