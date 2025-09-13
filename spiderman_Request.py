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


def get_spiderman_info():
    """Obtiene información de Spider-Man desde Marvel API"""
    print("🕷️ Obteniendo información de Spider-Man desde Marvel...")

    auth_params = generate_marvel_auth()

    # Buscar el personaje Spider-Man
    character_url = f"{BASE_URL_MARVEL}/characters"
    character_params = {
        **auth_params,
        'name': 'Spider-Man (Peter Parker)',
        'limit': 1
    }

    try:
        response = requests.get(character_url, params=character_params)
        response.raise_for_status()
        data = response.json()

        if data['data']['results']:
            spiderman = data['data']['results'][0]
            print(f"\n📖 Descripción de Spider-Man:")
            print(f"{spiderman['description'] or 'Peter Parker, el amigable Spider-Man vecino de Nueva York'}")

            # Obtener imagen
            if spiderman['thumbnail']:
                image_url = f"{spiderman['thumbnail']['path']}.{spiderman['thumbnail']['extension']}"
                print(f"\n🖼️ Imagen de Spider-Man: {image_url}")

            # Obtener algunos cómics
            spiderman_id = spiderman['id']
            comics_url = f"{BASE_URL_MARVEL}/characters/{spiderman_id}/comics"
            comics_params = {
                **auth_params,
                'limit': 5,
                'orderBy': '-onsaleDate'
            }

            comics_response = requests.get(comics_url, params=comics_params)
            if comics_response.status_code == 200:
                comics_data = comics_response.json()
                print(f"\n📚 Últimos cómics de Spider-Man:")
                for comic in comics_data['data']['results'][:3]:
                    print(f"  • {comic['title']}")

        else:
            print("No se encontró información de Spider-Man")

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar Marvel API: {e}")


def get_spiderman_pizza_menu():
    """Busca recetas de pizzas temáticas inspiradas en Spider-Man/Nueva York"""
    print("\n🕸️ Creando menú de pizzas temáticas de Spider-Man...")

    # Términos de búsqueda relacionados con pizzas y Nueva York
    pizza_searches = {
        'pizza_clasica': 'classic new york pizza',
        'pizza_suprema': 'supreme pizza pepperoni',
        'pizza_vegetariana': 'vegetarian pizza spinach',
        'pizza_especial': 'margherita pizza basil'
    }

    menu = {}

    for tipo_pizza, search_term in pizza_searches.items():
        try:
            url = f"{BASE_URL_SPOONACULAR}/recipes/complexSearch"
            params = {
                'apiKey': SPOONACULAR_API_KEY,
                'query': search_term,
                'number': 2,
                'addRecipeInformation': True,
                'type': 'main course'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['results']:
                recipe = data['results'][0]  # Tomamos la primera receta

                # Obtener ingredientes de la receta
                recipe_id = recipe['id']
                ingredients_url = f"{BASE_URL_SPOONACULAR}/recipes/{recipe_id}/information"
                ingredients_params = {
                    'apiKey': SPOONACULAR_API_KEY,
                    'includeNutrition': False
                }

                ingredients_response = requests.get(ingredients_url, params=ingredients_params)
                ingredients_info = {}

                if ingredients_response.status_code == 200:
                    ingredients_data = ingredients_response.json()
                    ingredients_info = {
                        'ingredientes': [ing['original'] for ing in
                                         ingredients_data.get('extendedIngredients', [])[:5]],
                        'instrucciones': ingredients_data.get('instructions', 'Ver receta completa en el enlace')
                    }

                menu[tipo_pizza] = {
                    'nombre': recipe['title'],
                    'tiempo': f"{recipe.get('readyInMinutes', 'N/A')} minutos",
                    'porciones': f"{recipe.get('servings', 'N/A')} personas",
                    'imagen': recipe.get('image', 'No disponible'),
                    'url': recipe.get('sourceUrl', 'No disponible'),
                    **ingredients_info
                }
            else:
                menu[tipo_pizza] = {'nombre': f'No se encontraron recetas para {tipo_pizza}'}

        except requests.exceptions.RequestException as e:
            print(f"Error al buscar {tipo_pizza}: {e}")
            menu[tipo_pizza] = {'nombre': f'Error al buscar {tipo_pizza}'}

    # Mostrar el menú
    print("\n🍕 MENÚ DE PIZZAS SPIDER-MAN:")
    print("=" * 50)

    pizza_nombres = {
        'pizza_clasica': '🍕 PIZZA CLÁSICA NEW YORK',
        'pizza_suprema': '🍕 PIZZA SUPREMA DEL TREPAMUROS',
        'pizza_vegetariana': '🍕 PIZZA VERDE COMO EL DUENDE',
        'pizza_especial': '🍕 PIZZA MARGHERITA DEL VECINDARIO'
    }

    for tipo, info in menu.items():
        print(f"\n{pizza_nombres[tipo]}")
        print(f"  🍕 Nombre: {info['nombre']}")

        if 'tiempo' in info:
            print(f"  ⏱️  Tiempo: {info['tiempo']}")
        if 'porciones' in info:
            print(f"  👥 Porciones: {info['porciones']}")

        if 'ingredientes' in info and info['ingredientes']:
            print(f"  🧄 Ingredientes principales:")
            for ingrediente in info['ingredientes']:
                print(f"     • {ingrediente}")

        if 'imagen' in info and info['imagen'] != 'No disponible':
            print(f"  📸 Imagen: {info['imagen']}")

        if 'url' in info and info['url'] != 'No disponible':
            print(f"  🔗 Receta completa: {info['url']}")


def get_pizza_delivery_tips():
    """Consejos de entrega de pizza al estilo Spider-Man"""
    print("\n🕷️ CONSEJOS DE ENTREGA SPIDER-MAN:")
    print("=" * 40)

    tips = [
        "🕸️ 'Con un gran poder viene una gran responsabilidad'... ¡y pizzas calientes!",
        "🏢 Usa tu sentido arácnido para encontrar la dirección correcta",
        "⏰ Entregar en 30 minutos o menos, más rápido que balancearse entre edificios",
        "🍕 Mantén la pizza horizontal mientras te balanceas por la ciudad",
        "❤️ Recuerda: ¡Una pizza bien entregada hace feliz al vecindario!"
    ]

    for tip in tips:
        print(f"  {tip}")


def main():
    """Función principal"""
    print("🕷️🍕 INFORMACIÓN DE SPIDER-MAN Y MENÚ DE PIZZAS 🍕🕷️")
    print("=" * 60)

    # Obtener información de Spider-Man desde Marvel
    get_spiderman_info()

    # Obtener menú de pizzas temáticas desde Spoonacular
    get_spiderman_pizza_menu()

    # Consejos adicionales temáticos
    get_pizza_delivery_tips()

    print("\n✨ ¡Tu amigable Spider-Man del vecindario te desea buen provecho! ✨")
    print("🕸️ ¡Que disfrutes estas pizzas dignas de un superhéroe! 🕸️")


if __name__ == "__main__":
    main()