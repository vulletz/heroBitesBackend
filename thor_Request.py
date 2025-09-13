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


def get_thor_info():
    """Obtiene información de Thor desde Marvel API"""
    print("🔨 Obteniendo información de Thor desde Marvel...")

    auth_params = generate_marvel_auth()

    # Buscar el personaje Thor
    character_url = f"{BASE_URL_MARVEL}/characters"
    character_params = {
        **auth_params,
        'name': 'Thor',
        'limit': 1
    }

    try:
        response = requests.get(character_url, params=character_params)
        response.raise_for_status()
        data = response.json()

        if data['data']['results']:
            thor = data['data']['results'][0]
            print(f"\n📖 Descripción de Thor:")
            print(f"{thor['description'] or 'Thor, el Dios del Trueno de Asgard'}")

            # Obtener imagen
            if thor['thumbnail']:
                image_url = f"{thor['thumbnail']['path']}.{thor['thumbnail']['extension']}"
                print(f"\n🖼️ Imagen de Thor: {image_url}")

            # Obtener algunos cómics
            thor_id = thor['id']
            comics_url = f"{BASE_URL_MARVEL}/characters/{thor_id}/comics"
            comics_params = {
                **auth_params,
                'limit': 5,
                'orderBy': '-onsaleDate'
            }

            comics_response = requests.get(comics_url, params=comics_params)
            if comics_response.status_code == 200:
                comics_data = comics_response.json()
                print(f"\n📚 Últimos cómics de Thor:")
                for comic in comics_data['data']['results'][:3]:
                    print(f"  • {comic['title']}")

        else:
            print("No se encontró información de Thor")

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar Marvel API: {e}")


def get_thor_themed_menu():
    """Busca recetas temáticas relacionadas con Thor/nórdico"""
    print("\n⚡ Creando menú temático de Thor...")

    # Términos de búsqueda relacionados con la temática nórdica/vikinga
    search_terms = {
        'entrada': 'norse appetizer',
        'platillo_fuerte': 'viking feast meat',
        'bebida': 'mead honey drink',
        'postre': 'scandinavian dessert'
    }

    menu = {}

    for categoria, term in search_terms.items():
        try:
            url = f"{BASE_URL_SPOONACULAR}/recipes/complexSearch"
            params = {
                'apiKey': SPOONACULAR_API_KEY,
                'query': term,
                'number': 2,
                'addRecipeInformation': True
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['results']:
                recipe = data['results'][0]  # Tomamos la primera receta
                menu[categoria] = {
                    'nombre': recipe['title'],
                    'tiempo': f"{recipe.get('readyInMinutes', 'N/A')} minutos",
                    'imagen': recipe.get('image', 'No disponible'),
                    'url': recipe.get('sourceUrl', 'No disponible')
                }
            else:
                menu[categoria] = {'nombre': f'No se encontraron recetas para {categoria}'}

        except requests.exceptions.RequestException as e:
            print(f"Error al buscar {categoria}: {e}")
            menu[categoria] = {'nombre': f'Error al buscar {categoria}'}

    # Mostrar el menú
    print("\n🍽️ MENÚ TEMÁTICO DE THOR:")
    print("=" * 40)

    categorias_nombres = {
        'entrada': '🥗 ENTRADA',
        'platillo_fuerte': '🥩 PLATILLO FUERTE',
        'bebida': '🍯 BEBIDA',
        'postre': '🍰 POSTRE'
    }

    for categoria, info in menu.items():
        print(f"\n{categorias_nombres[categoria]}")
        print(f"  Plato: {info['nombre']}")
        if 'tiempo' in info:
            print(f"  Tiempo: {info['tiempo']}")
        if 'imagen' in info and info['imagen'] != 'No disponible':
            print(f"  Imagen: {info['imagen']}")


def main():
    """Función principal"""
    print("⚡🔨 INFORMACIÓN DE THOR Y MENÚ TEMÁTICO 🔨⚡")
    print("=" * 50)

    # Obtener información de Thor desde Marvel
    get_thor_info()

    # Obtener menú temático desde Spoonacular
    get_thor_themed_menu()

    print("\n✨ ¡Que disfrutes tu aventura culinaria asgardiana! ✨")


if __name__ == "__main__":
    main()