import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_connection import test_connection, get_wellbeing_collection
from models.checkin_model import CheckinModel
from models.wellbeing_model import WellbeingModel


def main():
    print("=" * 60)
    print("DEBUG: MongoDB - WellbeingModel")
    print("=" * 60)

    # 1. Probar conexión
    print("\n[1] Probando conexión a MongoDB...")
    ok, msg = test_connection()
    print(f"    {msg}")

    if not ok:
        print("\n   ⚠  No se pudo conectar a MongoDB. Verifica que esté corriendo.")
        print("   Ejecuta: mongod (o inicia el servicio de MongoDB)")
        return

    # 2. Asegurar documento para id_usuario=1
    print("\n[2] Asegurando documento para id_usuario=1...")
    doc = CheckinModel.ensure_user_document(1)
    print(f"    Documento asegurado. ID: {doc.get('_id')}")
    print(f"    Check-ins actuales: {len(doc.get('checkins', []))}")

    # 3. Insertar check-in de prueba
    print("\n[3] Insertando check-in de prueba...")
    result = CheckinModel.save_checkin(
        id_usuario=1,
        tipo_checkin="estres_energia",
        titulo_checkin="Estado general",
        estado_animo_general="Ansioso",
        respuestas=[
            {"clave": "estres", "pregunta": "¿Qué tanto estrés sientes ahora?", "tipo": "escala", "valor": 7, "min": 1, "max": 10},
            {"clave": "energia", "pregunta": "¿Cuánta energía tienes?", "tipo": "escala", "valor": 4, "min": 1, "max": 10},
            {"clave": "enfoque", "pregunta": "¿Qué tan fácil te concentras?", "tipo": "escala", "valor": 5, "min": 1, "max": 10},
            {"clave": "frase_dia", "pregunta": "Escribe una frase", "tipo": "texto", "valor": "Hoy puedo avanzar poco a poco"},
        ],
        recomendacion_automatica={
            "titulo": "Modo Calma",
            "descripcion": "Realiza una pausa guiada de 5 minutos.",
            "tipo": "modo_calma"
        }
    )
    print(f"    Success: {result['success']}")
    print(f"    Message: {result['message']}")
    if result.get("checkin"):
        ck = result["checkin"]
        print(f"    ID Check-in: {ck.get('id_checkin')}")
        print(f"    Estado: {ck.get('estado_animo_general')}")
        print(f"    Métricas: {ck.get('resumen_metricas')}")
        print(f"    Respuestas: {len(ck.get('respuestas', []))} preguntas")

    # 4. Leer últimos check-ins
    print("\n[4] Leyendo últimos check-ins (limit=5)...")
    checkins = CheckinModel.get_user_checkins(1, limit=5)
    print(f"    Total obtenidos: {len(checkins)}")
    for ck in checkins:
        mood = ck.get("estado_animo_general") or ck.get("estado_animo", "-")
        metricas = ck.get("resumen_metricas", {})
        print(f"    - {ck.get('fecha')} | {mood} | "
              f"Métricas:{metricas} | "
              f"Tipo:{ck.get('tipo_checkin')}")

    # 5. Leer resumen
    print("\n[5] Leyendo resumen de bienestar...")
    summary = CheckinModel.get_user_wellbeing_summary(1)
    print(f"    Total check-ins: {summary['total_checkins']}")
    promedios = summary.get("promedios", {})
    for k, v in promedios.items():
        print(f"    {k.capitalize()} prom: {v}/10")
    print(f"    Último estado: {summary['ultimo_estado_animo_general']}")
    print(f"    Última frase: {summary['ultima_frase']}")
    print(f"    Fecha último: {summary['fecha_ultimo_checkin']}")

    # 6. Último check-in
    print("\n[6] Último check-in...")
    latest = CheckinModel.get_latest_checkin(1)
    if latest:
        print(f"    Estado: {latest.get('estado_animo_general')}")
        print(f"    Tipo: {latest.get('tipo_checkin')}")
    else:
        print("    No hay check-ins.")

    # 7. Historial para especialista
    print("\n[7] Historial para especialista (id_usuario=1)...")
    hist = CheckinModel.get_specialist_user_history(1)
    print(f"    Resumen: {hist['resumen']['total_checkins']} check-ins")
    print(f"    Check-ins en lista: {len(hist['checkins'])}")

    # 8. Actualizar música
    print("\n[8] Actualizando música background_track...")
    r = WellbeingModel.update_music_settings(
        id_usuario=1,
        background_track="track_lluvia_001"
    )
    print(f"    {r['message']}")

    # 9. Leer música
    print("\n[9] Leyendo configuración musical...")
    music = WellbeingModel.get_music_settings(1)
    print(f"    Background: {music['background_track']}")
    print(f"    Calm Mode: {music['calm_mode_track']}")
    print(f"    Favoritos: {music['favorites']}")

    # 10. Toggle favorito
    print("\n[10] Toggle favorito...")
    r = WellbeingModel.toggle_favorite_music(1, "track_lluvia_001")
    print(f"    {r['message']} (favorite={r.get('favorite')})")
    music = WellbeingModel.get_music_settings(1)
    print(f"    Favoritos ahora: {music['favorites']}")

    # 11. Ver colección completa
    print("\n[11] Documento final en MongoDB:")
    collection = get_wellbeing_collection()
    final_doc = collection.find_one({"id_usuario": 1})
    if final_doc:
        print(f"    _id: {final_doc['_id']}")
        print(f"    id_usuario: {final_doc['id_usuario']}")
        print(f"    checkins: {len(final_doc.get('checkins', []))} registros")
        print(f"    musica: {final_doc.get('musica', {})}")
        print(f"    created_at: {final_doc.get('created_at')}")
        print(f"    updated_at: {final_doc.get('updated_at')}")

    print("\n" + "=" * 60)
    print("DEBUG COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
