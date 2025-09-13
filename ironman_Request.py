import requests
import hashlib
import time
from config import MARVEL_PUBLIC_KEY, MARVEL_PRIVATE_KEY, SPOONACULAR_API_KEY, BASE_URL_MARVEL, BASE_URL_SPOONACULAR


def generate_marvel_auth():
    ts = str(int(time.time()))
    hash_input = ts + MARVEL_PRIVATE_KEY + MARVEL_PUBLIC_KEY
    hash_md5 = hashlib.md5(hash_input.encode()).hexdigest()

    return {
        'ts': ts,
        'apikey': MARVEL_PUBLIC_KEY,
        'hash': hash_md5
    }


def get_ironman_info():
    """Obtiene información de Iron Man desde Marvel API"""
    print("🤖 Obteniendo información de Iron Man desde Marvel...")

    auth_params = generate_marvel_auth()

    # Buscar el personaje Iron Man
    character_url = f"{BASE_URL_MARVEL}/characters"
    character_params = {
        **auth_params,
        'name': 'Iron Man',
        'limit': 1
    }

    try:
        response = requests.get(character_url, params=character_params)
        response.raise_for_status()
        data = response.json()

        if data['data']['results']:
            ironman = data['data']['results'][0]
            print(f"\n📖 Descripción de Iron Man:")
            print(f"{ironman['description'] or 'Tony Stark, el genio multimillonario y filántropo conocido como Iron Man'}")

            # Obtener imagen
            if ironman['thumbnail']:
                image_url = f"{ironman['thumbnail']['path']}.{ironman['thumbnail']['extension']}"
                print(f"\n🖼️ Imagen de Iron Man: {image_url}")

            # Obtener algunos cómics
            ironman_id = ironman['id']
            comics_url = f"{BASE_URL_MARVEL}/characters/{ironman_id}/comics"
            comics_params = {
                **auth_params,
                'limit': 5,
                'orderBy': '-onsaleDate'
            }

            comics_response = requests.get(comics_url, params=comics_params)
            if comics_response.status_code == 200:
                comics_data = comics_response.json()
                print(f"\n📚 Últimos cómics de Iron Man:")
                for comic in comics_data['data']['results'][:3]:
                    print(f"  • {comic['title']}")

        else:
            print("No se encontró información de Iron Man")

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar Marvel API: {e}")


def get_recipe_details(recipe_id):
    """Obtiene los detalles completos de una receta incluyendo ingredientes e instrucciones"""
    try:
        url = f"{BASE_URL_SPOONACULAR}/recipes/{recipe_id}/information"
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'includeNutrition': False
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        recipe_data = response.json()

        # Obtener ingredientes
        ingredients = []
        if 'extendedIngredients' in recipe_data:
            for ingredient in recipe_data['extendedIngredients']:
                ingredients.append(ingredient.get('original', ''))

        # Obtener instrucciones
        instructions = []
        if 'analyzedInstructions' in recipe_data and recipe_data['analyzedInstructions']:
            for instruction_group in recipe_data['analyzedInstructions']:
                if 'steps' in instruction_group:
                    for step in instruction_group['steps']:
                        instructions.append(f"{step['number']}. {step['step']}")

        return {
            'ingredients': ingredients,
            'instructions': instructions,
            'servings': recipe_data.get('servings', 'N/A'),
            'ready_in_minutes': recipe_data.get('readyInMinutes', 'N/A'),
            'source_url': recipe_data.get('sourceUrl', ''),
            'summary': recipe_data.get('summary', '')
        }

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener detalles de la receta: {e}")
        return None


def get_ironman_themed_menu():
    """Busca recetas específicas para el menú temático de Iron Man"""
    print("\n🔴🟡 Creando menú temático de Iron Man (Tony Stark)...")

    # Búsquedas específicas según los lineamientos
    search_terms = {
        'entrada': 'beef carpaccio arugula parmesan',
        'platillo_fuerte': 'filet mignon truffle sauce',
        'bebida': 'single malt scotch whisky',
        'postre': 'gourmet donuts chocolate glaze berries'
    }

    menu = {}

    for categoria, term in search_terms.items():
        try:
            print(f"🔍 Buscando: {term}")
            url = f"{BASE_URL_SPOONACULAR}/recipes/complexSearch"
            params = {
                'apiKey': SPOONACULAR_API_KEY,
                'query': term,
                'number': 3,
                'addRecipeInformation': True,
                'sort': 'popularity'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['results']:
                recipe = data['results'][0]  # Tomamos la primera receta
                recipe_details = get_recipe_details(recipe['id'])
                
                menu[categoria] = {
                    'nombre': recipe['title'],
                    'imagen': recipe.get('image', 'No disponible'),
                    'detalles': recipe_details
                }
            else:
                menu[categoria] = {'nombre': f'No se encontraron recetas para {categoria}'}

            # Pequeña pausa para evitar límites de rate
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Error al buscar {categoria}: {e}")
            menu[categoria] = {'nombre': f'Error al buscar {categoria}'}

    return menu


def display_menu(menu):
    """Muestra el menú completo con recetas detalladas"""
    print("\n🍽️ MENÚ GOURMET DE TONY STARK (IRON MAN)")
    print("=" * 60)

    categorias_info = {
        'entrada': {
            'emoji': '🥩',
            'titulo': 'ENTRADA - APERITIVO DE RES',
            'descripcion': 'Elegante y sofisticado (estilo carpaccio)'
        },
        'platillo_fuerte': {
            'emoji': '🥩',
            'titulo': 'PLATO FUERTE - FILETE PREMIUM',
            'descripcion': 'Lujoso y clásico (estilo filet mignon)'
        },
        'bebida': {
            'emoji': '🥃',
            'titulo': 'BEBIDA - CÓCTEL DE WHISKY',
            'descripcion': 'Sofisticado y premium'
        },
        'postre': {
            'emoji': '🍩',
            'titulo': 'POSTRE - DONAS DE CHOCOLATE',
            'descripcion': 'Gourmet con toque elegante'
        }
    }

    for categoria, info in menu.items():
        if categoria in categorias_info:
            cat_info = categorias_info[categoria]
            print(f"\n{cat_info['emoji']} {cat_info['titulo']}")
            print(f"   {cat_info['descripcion']}")
            print("-" * 50)
            
            print(f"📋 Receta: {info['nombre']}")
            
            if 'detalles' in info and info['detalles']:
                detalles = info['detalles']
                
                if detalles['servings'] != 'N/A':
                    print(f"👥 Porciones: {detalles['servings']}")
                if detalles['ready_in_minutes'] != 'N/A':
                    print(f"⏱️ Tiempo: {detalles['ready_in_minutes']} minutos")
                
                if info['imagen'] != 'No disponible':
                    print(f"🖼️ Imagen: {info['imagen']}")
                
                # Ingredientes
                if detalles['ingredients']:
                    print(f"\n🛒 INGREDIENTES:")
                    for i, ingredient in enumerate(detalles['ingredients'], 1):
                        print(f"  {i}. {ingredient}")
                
                # Instrucciones
                if detalles['instructions']:
                    print(f"\n👨‍🍳 INSTRUCCIONES:")
                    for instruction in detalles['instructions']:
                        print(f"  {instruction}")
                
                # URL de la fuente
                if detalles['source_url']:
                    print(f"\n🔗 Receta completa: {detalles['source_url']}")
                
                print("\n" + "="*60)


def main():
    """Función principal"""
    print("🤖⚡ INFORMACIÓN DE IRON MAN Y MENÚ GOURMET ⚡🤖")
    print("=" * 60)

    # Obtener información de Iron Man desde Marvel
    get_ironman_info()

    # Obtener menú temático desde Spoonacular
    menu = get_ironman_themed_menu()
    
    # Mostrar el menú detallado
    display_menu(menu)

    print("\n✨ ¡Disfruta tu experiencia culinaria digna de Tony Stark! ✨")
    print("🔴🟡 'I am Iron Man' - Tony Stark 🟡🔴")


if __name__ == "__main__":
    main()