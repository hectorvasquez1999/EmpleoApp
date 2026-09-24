"""
Conector de Remote OK.

A diferencia de Adzuna, aqui no se manda una consulta por termino: la API
publica trae de una sola vez todas las ofertas vigentes del portal, y el
filtro por rol lo hace la clasificacion local (normalizar.clasificar),
igual que con las alertas de correo.

No requiere credenciales.
"""

import re

import requests

URL = "https://remoteok.com/api"
CODIGO_FUENTE = "remoteok"

CABECERAS = {"User-Agent": "AppEmpleo/0.1 (proyecto personal, uso no comercial)"}


def recolectar() -> tuple[list[dict], list[str]]:
    try:
        r = requests.get(URL, headers=CABECERAS, timeout=40)
        r.raise_for_status()
        datos = r.json()
    except requests.RequestException as e:
        return [], [f"Fallo al consultar Remote OK: {e}"]

    # El primer elemento del array es un aviso legal, no una oferta.
    anuncios = [a for a in datos if isinstance(a, dict) and a.get("id")]
    return anuncios, []


def _quitar_html(texto: str | None) -> str | None:
    if not texto:
        return None
    return re.sub(r"<[^>]+>", " ", texto)


def a_formato_comun(anuncio: dict) -> dict:
    """Traduce un anuncio de Remote OK a nuestro vocabulario interno."""
    return {
        "id_origen": str(anuncio.get("id")),
        "titulo": anuncio.get("position") or "",
        "empresa": anuncio.get("company"),
        "ubicacion_texto": anuncio.get("location") or "",
        "descripcion": _quitar_html(anuncio.get("description")),
        "url": anuncio.get("url") or f"https://remoteok.com/remote-jobs/{anuncio.get('id')}",
        "salario_min": anuncio.get("salary_min"),
        "salario_max": anuncio.get("salary_max"),
        "publicada_en": anuncio.get("date"),
    }
