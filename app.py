from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
import json
import urllib.parse
import time

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv('API_NINJA_KEY')  # Only need API Ninjas key

def generate_food_image(recipe_name):
    try:
        # Simplified prompt
        clean_name = recipe_name.strip()
        # Direct image URL without checking
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
        recipe_url = f'https://api.api-ninjas.com/v1/recipe?query={query}&limit=10'  # Request 10 recipes
        recipe_response = requests.get(recipe_url, headers={'X-Api-Key': API_KEY})
        
        if recipe_response.status_code == 200:
            all_recipes = recipe_response.json()
            
            # Generate images for all recipes
            for recipe in all_recipes:
                recipe['image_url'] = generate_food_image(recipe['title'])
                time.sleep(0.5)
            
            # Calculate pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            current_recipes = all_recipes[start_idx:end_idx]
            has_more = len(all_recipes) > end_idx
            
            return render_template('index.html', 
                                recipes=current_recipes, 
                                query=query,
                                page=page,
                                has_more=has_more,
                                total_recipes=len(all_recipes))
        else:
            return render_template('index.html', error='Failed to fetch recipes')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True) 