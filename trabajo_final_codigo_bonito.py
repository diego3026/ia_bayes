import re

def quitar_url(texto):
    """
    Elimina las URLs del texto.
    """
    url_pattern = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    texto_sin_url = re.sub(url_pattern, '', texto, flags=re.MULTILINE)
    return texto_sin_url

def quitar_acentos(texto):
    """
    Reemplaza los caracteres acentuados por sus equivalentes sin acentos.
    """
    equivalencias = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"
    }
    letras_sin_acentos = [equivalencias.get(letra, letra) for letra in texto]
    return ''.join(letras_sin_acentos)

def limpiar_texto(texto):
    """
    Limpia el texto eliminando URLs, acentos y cadenas desprovistas.
    """
    texto_sin_url = quitar_url(texto)
    texto_sin_acentos = quitar_acentos(texto_sin_url)
    texto_sin_saltos = texto_sin_acentos.replace("\n", "")
    texto_limpio = ''.join(caracter for caracter in texto_sin_saltos if caracter.isalpha() or caracter.isspace())
    return texto_limpio.lower()

def cargar_tweets(ruta_archivo):
    """
    Carga los tweets desde un archivo y los devuelve en un diccionario.
    """
    diccionario_tweets = {}
    with open(ruta_archivo, "r", encoding="utf8") as archivo:
        for linea in archivo:
            campos = linea.strip().split(',')
            if len(campos) >= 4:
                texto_tweet = limpiar_texto(campos[3])
                if texto_tweet:
                    agregar_valor(diccionario_tweets, campos[2], texto_tweet)
    return diccionario_tweets

def agregar_valor(diccionario, clave, valor):
    """
    Agrega un valor a una lista en un diccionario.
    """
    diccionario.setdefault(clave, []).append(valor)

def eliminar_cortos(diccionario, longitud_minima):
    """
    Elimina elementos de un diccionario cuyos valores tienen una longitud menor a longitud_minima.
    """
    return {clave: valor for clave, valor in diccionario.items() if len(valor) >= longitud_minima}

def dividir_entrenamiento_prueba(diccionario, porcentaje_entrenamiento):
    """
    Divide un diccionario de tweets en conjuntos de entrenamiento y prueba según el porcentaje especificado.
    """
    entrenamiento = {}
    prueba = {}
    for usuario, tweets in diccionario.items():
        punto_separacion = int(len(tweets) * porcentaje_entrenamiento)
        entrenamiento[usuario] = tweets[:punto_separacion]
        prueba[usuario] = tweets[punto_separacion:]
    return entrenamiento, prueba

def calcular_probabilidades_a_priori(diccionario):
    """
    Calcula las probabilidades a priori de los usuarios.
    """
    total_tweets = sum(len(tweets) for tweets in diccionario.values())
    return {usuario: len(tweets) / total_tweets for usuario, tweets in diccionario.items()}

def calcular_probabilidades_condicionales(diccionario):
    """
    Calcula las probabilidades condicionales de las palabras para cada usuario.
    """
    probabilidades_condicionales = {}
    for usuario, tweets in diccionario.items():
        contador_palabras = {}
        for tweet in tweets:
            for palabra in tweet.split():
                contador_palabras[palabra] = contador_palabras.get(palabra, 0) + 1
        total_palabras = sum(contador_palabras.values())
        probabilidades_palabras = {palabra: count / total_palabras for palabra, count in contador_palabras.items()}
        probabilidades_condicionales[usuario] = probabilidades_palabras
    return probabilidades_condicionales

def clasificar_tweet(tweet, probabilidades_a_priori, probabilidades_condicionales):
    """
    Clasifica un tweet en función de las probabilidades a priori y condicionales.
    """
    probabilidades_usuario = {usuario: prob_a_priori for usuario, prob_a_priori in probabilidades_a_priori.items()}
    for usuario, palabras in probabilidades_condicionales.items():
        for palabra in tweet.split():
            if palabra in palabras:
                probabilidades_usuario[usuario] *= palabras[palabra]
    return max(probabilidades_usuario, key=probabilidades_usuario.get)

# Cargar los tweets desde el archivo
diccionario_tweets = cargar_tweets("./tuits_bayes.txt")

# Eliminar usuarios con pocos tweets
diccionario_tweets = eliminar_cortos(diccionario_tweets, 5)

# Dividir los datos en conjuntos de entrenamiento y prueba
entrenamiento, prueba = dividir_entrenamiento_prueba(diccionario_tweets, 0.8)

# Calcular las probabilidades a priori y condicionales
probabilidades_a_priori = calcular_probabilidades_a_priori(entrenamiento)
probabilidades_condicionales = calcular_probabilidades_condicionales(entrenamiento)

# Clasificar los tweets de prueba y mostrar los resultados
for usuario, tweets in prueba.items():
    for tweet in tweets:
        print(clasificar_tweet(tweet, probabilidades_a_priori, probabilidades_condicionales))
