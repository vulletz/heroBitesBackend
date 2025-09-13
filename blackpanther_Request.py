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


def get_black_panther_info():
    """Obtiene información de Black Panther desde Marvel API"""
    print("🐾 Obteniendo información de Black Panther desde Marvel...")

    auth_params = generate_marvel_auth()

    # Buscar el personaje Black Panther
    character_url = f"{BASE_URL_MARVEL}/characters"
    character_params = {
        **auth_params,
        'name': 'Black Panther',
        'limit': 1
    }

    try:
        response = requests.get(character_url, params=character_params)
        response.raise_for_status()
        data = response.json()

        if data['data']['results']:
            black_panther = data['data']['results'][0]
            print(f"\n📖 Descripción de Black Panther:")
            print(f"{black_panther['description'] or 'T\'Challa, Rey de Wakanda y protector de su pueblo'}")

            # Obtener imagen
            if black_panther['thumbnail']:
                image_url = f"{black_panther['thumbnail']['path']}.{black_panther['thumbnail']['extension']}"
                print(f"\n🖼️ Imagen de Black Panther: {image_url}")

            # Obtener algunos cómics
            panther_id = black_panther['id']
            comics_url = f"{BASE_URL_MARVEL}/characters/{panther_id}/comics"
            comics_params = {
                **auth_params,
                'limit': 5,
                'orderBy': '-onsaleDate'
            }

            comics_response = requests.get(comics_url, params=comics_params)
            if comics_response.status_code == 200:
                comics_data = comics_response.json()
                print(f"\n📚 Últimos cómics de Black Panther:")
                for comic in comics_data['data']['results'][:3]:
                    print(f"  • {comic['title']}")

        else:
            print("No se encontró información de Black Panther")

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar Marvel API: {e}")


def get_wakanda_jollof_menu():
    """Busca recetas de Jollof Rice y platillos africanos temáticos inspirados en Wakanda"""
    print("\n🌍 Creando menú real de Wakanda con Jollof Rice...")

    # Términos de búsqueda relacionados con cocina africana y Jollof Rice
    african_dishes = {
        'jollof_principal': 'jollof rice chicken',
        'jollof_vegetariano': 'vegetarian jollof rice',
        'jollof_mariscos': 'jollof rice seafood shrimp',
        'jollof_tradicional': 'nigerian jollof rice beef'
    }

    menu = {}

    for tipo_plato, search_term in african_dishes.items():
        try:
            url = f"{BASE_URL_SPOONACULAR}/recipes/complexSearch"
            params = {
                'apiKey': SPOONACULAR_API_KEY,
                'query': search_term,
                'number': 3,
                'addRecipeInformation': True,
                'type': 'main course'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['results']:
                # Buscar la mejor receta que contenga "jollof" en el título
                best_recipe = None
                for recipe in data['results']:
                    if 'jollof' in recipe['title'].lower():
                        best_recipe = recipe
                        break

                if not best_recipe:
                    best_recipe = data['results'][0]  # Tomar la primera si no hay jollof específico

                # Obtener información detallada de la receta
                recipe_id = best_recipe['id']
                details_url = f"{BASE_URL_SPOONACULAR}/recipes/{recipe_id}/information"
                details_params = {
                    'apiKey': SPOONACULAR_API_KEY,
                    'includeNutrition': True
                }

                details_response = requests.get(details_url, params=details_params)
                recipe_details = {}

                if details_response.status_code == 200:
                    details_data = details_response.json()
                    recipe_details = {
                        'ingredientes': [ing['original'] for ing in details_data.get('extendedIngredients', [])[:6]],
                        'instrucciones_resumen': details_data.get('summary', 'Ver receta completa'),
                        'nivel_especias': 'Medio-Alto' if any(spice in details_data.get('summary', '').lower()
                                                              for spice in
                                                              ['spicy', 'pepper', 'chili', 'hot']) else 'Suave',
                        'valor_nutricional': details_data.get('nutrition', {}).get('nutrients', [])[
                                             :3] if details_data.get('nutrition') else []
                    }

                menu[tipo_plato] = {
                    'nombre': best_recipe['title'],
                    'tiempo': f"{best_recipe.get('readyInMinutes', 'N/A')} minutos",
                    'porciones': f"{best_recipe.get('servings', 'N/A')} personas",
                    'imagen': best_recipe.get('image', 'No disponible'),
                    'url': best_recipe.get('sourceUrl', 'No disponible'),
                    'precio_salud': best_recipe.get('healthScore', 'N/A'),
                    **recipe_details
                }
            else:
                menu[tipo_plato] = {'nombre': f'No se encontraron recetas para {tipo_plato}'}

        except requests.exceptions.RequestException as e:
            print(f"Error al buscar {tipo_plato}: {e}")
            menu[tipo_plato] = {'nombre': f'Error al buscar {tipo_plato}'}

    # Mostrar el menú
    print("\n🍛 MENÚ REAL DE WAKANDA - JOLLOF RICE:")
    print("=" * 55)

    wakanda_nombres = {
        'jollof_principal': '🍗 JOLLOF RICE REAL CON POLLO',
        'jollof_vegetariano': '🥬 JOLLOF RICE DE LOS JARDINES DE WAKANDA',
        'jollof_mariscos': '🦐 JOLLOF RICE DEL RÍO SAGRADO',
        'jollof_tradicional': '🥩 JOLLOF RICE ANCESTRAL CON CARNE'
    }

    for tipo, info in menu.items():
        print(f"\n{wakanda_nombres[tipo]}")
        print(f"  🍽️  Nombre: {info['nombre']}")

        if 'tiempo' in info:
            print(f"  ⏱️  Tiempo de preparación: {info['tiempo']}")
        if 'porciones' in info:
            print(f"  👥 Porciones: {info['porciones']}")
        if 'nivel_especias' in info:
            print(f"  🌶️  Nivel de especias: {info['nivel_especias']}")
        if 'precio_salud' in info and info['precio_salud'] != 'N/A':
            print(f"  💪 Puntuación de salud: {info['precio_salud']}/100")

        if 'ingredientes' in info and info['ingredientes']:
            print(f"  🧄 Ingredientes principales:")
            for ingrediente in info['ingredientes']:
                print(f"     • {ingrediente}")

        if 'valor_nutricional' in info and info['valor_nutricional']:
            print(f"  📊 Información nutricional:")
            for nutrient in info['valor_nutricional']:
                print(
                    f"     • {nutrient.get('name', 'N/A')}: {nutrient.get('amount', 'N/A')}{nutrient.get('unit', '')}")

        if 'imagen' in info and info['imagen'] != 'No disponible':
            print(f"  📸 Imagen: {info['imagen']}")

        if 'url' in info and info['url'] != 'No disponible':
            print(f"  🔗 Receta completa: {info['url']}")


def get_wakanda_cooking_wisdom():
    """Sabiduría culinaria de Wakanda al estilo Black Panther"""
    print("\n🐾 SABIDURÍA CULINARIA DE WAKANDA:")
    print("=" * 45)

    wisdom = [
        "🌍 'En Wakanda, cada grano de arroz cuenta la historia de nuestros ancestros'",
        "🔥 'El fuego del vibranium no es nada comparado con el sabor del jollof bien hecho'",
        "👑 'Un rey que no sabe cocinar para su pueblo, no merece gobernar'",
        "🌶️ 'Las especias son como los guerreros: deben trabajar en armonía'",
        "🤝 'Compartir jollof rice es compartir el corazón de África'",
        "⚡ 'Wakanda Forever... y el Jollof Rice también!'"
    ]

    for quote in wisdom:
        print(f"  {quote}")


def get_vibranium_cooking_tips():
    """Consejos de cocina con tecnología de Wakanda"""
    print("\n💎 CONSEJOS DE COCINA CON TECNOLOGÍA WAKANDIANA:")
    print("=" * 50)

    tips = {
        'Preparación': 'Usa tecnología de precisión para medir el arroz perfectamente',
        'Cocción': 'El calor controlado es clave, como el poder de la Pantera Negra',
        'Especias': 'Las especias africanas son tu vibranium culinario',
        'Tiempo': 'La paciencia es una virtud real, no apresures el proceso',
        'Presentación': 'Sirve con el orgullo de un guerriero de Wakanda'
    }

    for categoria, tip in tips.items():
        print(f"  🔸 {categoria}: {tip}")


def main():
    """Función principal"""
    print("🐾🍛 INFORMACIÓN DE BLACK PANTHER Y MENÚ JOLLOF RICE 🍛🐾")
    print("=" * 70)

    # Obtener información de Black Panther desde Marvel
    get_black_panther_info()

    # Obtener menú de Jollof Rice temático desde Spoonacular
    get_wakanda_jollof_menu()

    # Sabiduría culinaria de Wakanda
    get_wakanda_cooking_wisdom()

    # Consejos de cocina con tecnología Wakandiana
    get_vibranium_cooking_tips()

    print("\n✨ ¡Wakanda Forever y que disfrutes estos sabores ancestrales! ✨")
    print("🌍 ¡El legado culinario de África vive en cada bocado! 🌍")
    print("🐾 ¡Por la gloria de Wakanda y el mejor Jollof Rice! 🐾")


if __name__ == "__main__":
    main()