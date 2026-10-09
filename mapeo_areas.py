MAPEO_AREAS_OLAS = {
    "RIO DE LA PLATA INTERIOR": "AREA RIO DE LA PLATA",
    "RIO DE LA PLATA EXTERIOR": "AREA RIO DE LA PLATA",
    "RIO DE LA PLATA INTERMEDIO": "AREA RIO DE LA PLATA",
    "OFFSHORE RIO DE LA PLATA": "AREA RIO DE LA PLATA",

    "OFFSHORE MAR DEL PLATA": "AREA A",
    "OFFSHORE BAHIA BLANCA": "AREA B",
    "OFFSHORE VALDES": "AREA C",
    "OFFSHORE SAN JORGE": "AREA D",
    "OFFSHORE PATAGONIA SUR": "AREA E",
    "OFFSHORE FIN DEL MUNDO": "AREA F",
    "ZONA MALVINAS": "AREA G",

    "AREA NORTE (N 40S E30W)": "AREA NORTE",
    "AREA NORTE (N 40S E40 W30)": "AREA NORTE",
    "AREA NORTE (N 40S W 40W)": "AREA NORTE",

    "AREA CENTRO ESTE (N 45S E 030W)": "AREA CENTRO ESTE",
    "AREA CENTRO ESTE (N 45S W 030W)": "AREA CENTRO ESTE",
    "AREA CENTRO ESTE (S 45S E 030W)": "AREA CENTRO ESTE",
    "AREA CENTRO ESTE (S 45S W 030W)": "AREA CENTRO ESTE",

    "AREA CENTRO OESTE (N 45S W 40W)": "AREA CENTRO OESTE",
    "AREA CENTRO OESTE (N 45S W 50W)": "AREA CENTRO OESTE",
    "AREA CENTRO OESTE (S 45S W 040W)": "AREA CENTRO OESTE",
    "AREA CENTRO OESTE (S 45S W 050W)": "AREA CENTRO OESTE",

    "AREA SUDESTE (N 55S W 030W)": "AREA SUR ESTE",
    "AREA SUDESTE (S 55S E 030W)": "AREA SUR ESTE",
    "AREA SUDESTE (S 55S W 030W)": "AREA SUR ESTE",
    "AREA SUDESTE( N 55S E 030W)": "AREA SUR ESTE",

    "AREA SUDOESTE (N 55S E 050W)": "AREA SUR OESTE",
    "AREA SUDOESTE (N 55S W 050W)": "AREA SUR OESTE",
    "AREA SUDOESTE (S 55S E 050W)": "AREA SUR OESTE",
    "AREA SUDOESTE (S 55S W 050W)": "AREA SUR OESTE",

    "AREA DRAKE": "AREA DRAKE",
}


def unir_meteorologia_y_olas(
    boletin_meteorologico,
    datos_olas,
):
    resultado = {}

    for area_meteo, info_meteo in boletin_meteorologico.items():

        area_olas = MAPEO_AREAS_OLAS.get(area_meteo)
        texto_olas = None

        if area_olas:
            texto_olas = datos_olas.get(area_olas)

        resultado[area_meteo] = {
            **info_meteo,
            "olas": texto_olas,
            "area_olas": area_olas,
        }

    return resultado
