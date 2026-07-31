from datetime import datetime

CHECKIN_TEMPLATES = [
    {
        "tipo_checkin": "estres_energia",
        "titulo": "Estado general",
        "preguntas": [
            {
                "clave": "estres",
                "texto": "¿Qué tanto estrés sientes ahora?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "energia",
                "texto": "¿Cuánta energía tienes en este momento?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "estado_animo",
                "texto": "¿Qué estado de ánimo describe mejor tu día?",
                "tipo": "opcion",
                "opciones": ["Tranquilo", "Ansioso", "Cansado", "Motivado", "Saturado"]
            },
            {
                "clave": "frase_dia",
                "texto": "Escribe una frase sobre cómo te sientes hoy.",
                "tipo": "texto"
            }
        ]
    },
    {
        "tipo_checkin": "descanso_cansancio",
        "titulo": "Descanso y cansancio",
        "preguntas": [
            {
                "clave": "calidad_descanso",
                "texto": "¿Qué tan bien descansaste?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "cansancio_mental",
                "texto": "¿Qué tan cansada está tu mente?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "irritabilidad",
                "texto": "¿Qué tan irritable te sientes?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "pensamiento_principal",
                "texto": "¿Qué pensamiento ha estado más presente hoy?",
                "tipo": "texto"
            }
        ]
    },
    {
        "tipo_checkin": "motivacion_enfoque",
        "titulo": "Motivación y enfoque",
        "preguntas": [
            {
                "clave": "motivacion",
                "texto": "¿Qué tanta motivación tienes hoy?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "enfoque",
                "texto": "¿Qué tan fácil te está siendo concentrarte?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "saturacion",
                "texto": "¿Qué tan saturado te sientes?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "necesidad_pausa",
                "texto": "¿Sientes que necesitas una pausa?",
                "tipo": "opcion",
                "opciones": ["No", "Un poco", "Sí", "Urgentemente"]
            }
        ]
    },
    {
        "tipo_checkin": "burnout",
        "titulo": "Señales de burnout",
        "preguntas": [
            {
                "clave": "agotamiento",
                "texto": "¿Qué tan agotado te sientes?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "presion",
                "texto": "¿Qué tanta presión académica o laboral sientes?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "desconexion",
                "texto": "¿Qué tan desconectado te sientes de tus actividades?",
                "tipo": "escala",
                "min": 1,
                "max": 10
            },
            {
                "clave": "comentario",
                "texto": "Describe brevemente qué te está pesando más.",
                "tipo": "texto"
            }
        ]
    }
]

def get_today_checkin_template(id_usuario):
    today = datetime.now().toordinal()
    index = (today + id_usuario) % len(CHECKIN_TEMPLATES)
    return CHECKIN_TEMPLATES[index]
