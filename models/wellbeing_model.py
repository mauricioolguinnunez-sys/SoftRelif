from datetime import datetime
import uuid

from database.mongo_connection import get_wellbeing_collection


class WellbeingModel:

    COLLECTION = None

    @classmethod
    def _collection(cls):
        if cls.COLLECTION is None:
            cls.COLLECTION = get_wellbeing_collection()
        return cls.COLLECTION

    @staticmethod
    def _now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =====================================================
    # DOCUMENT MANAGEMENT
    # =====================================================

    @staticmethod
    def ensure_user_document(id_usuario):
        collection = WellbeingModel._collection()
        existing = collection.find_one({"id_usuario": id_usuario})
        if existing:
            return existing
        doc = {
            "id_usuario": id_usuario,
            "checkins": [],
            "musica": {
                "background_track": None,
                "calm_mode_track": None,
                "favoritos": []
            },
            "microdescansos": [],
            "created_at": WellbeingModel._now(),
            "updated_at": WellbeingModel._now()
        }
        collection.insert_one(doc)
        return doc

    # =====================================================
    # CHECK-INS
    # =====================================================

    @staticmethod
    def save_checkin(id_usuario, tipo_checkin, titulo_checkin, estado_animo_general, respuestas, recomendacion_automatica=None):
        if not id_usuario:
            return {"success": False, "message": "id_usuario es requerido."}
        if not tipo_checkin:
            return {"success": False, "message": "tipo_checkin es requerido."}
        if not isinstance(respuestas, list):
            return {"success": False, "message": "respuestas debe ser una lista."}

        for r in respuestas:
            if not all(k in r for k in ("clave", "pregunta", "tipo", "valor")):
                return {"success": False, "message": "Cada respuesta debe tener clave, pregunta, tipo y valor."}
            if r["tipo"] == "escala":
                if not isinstance(r.get("valor"), (int, float)):
                    return {"success": False, "message": f"La respuesta '{r['clave']} requiere un valor numérico."}
                if not (1 <= r["valor"] <= 10):
                    return {"success": False, "message": f"La respuesta '{r['clave']} debe estar entre 1 y 10."}

        WellbeingModel.ensure_user_document(id_usuario)

        id_checkin = str(uuid.uuid4())
        fecha = WellbeingModel._now()
        fecha_corta = fecha[:10]
        hora = fecha[11:16]

        resumen_metricas = {}
        for r in respuestas:
            if r["tipo"] == "escala":
                resumen_metricas[r["clave"]] = r["valor"]

        checkin = {
            "id_checkin": id_checkin,
            "fecha": fecha,
            "fecha_corta": fecha_corta,
            "hora": hora,
            "tipo_checkin": tipo_checkin,
            "titulo_checkin": titulo_checkin,
            "estado_animo_general": estado_animo_general,
            "respuestas": respuestas,
            "resumen_metricas": resumen_metricas,
            "recomendacion_automatica": recomendacion_automatica or {}
        }

        collection = WellbeingModel._collection()
        collection.update_one(
            {"id_usuario": id_usuario},
            {
                "$push": {"checkins": checkin},
                "$set": {"updated_at": fecha}
            }
        )

        return {
            "success": True,
            "message": "Check-in guardado correctamente.",
            "checkin": checkin
        }

    @staticmethod
    def get_user_checkins(id_usuario, limit=30):
        doc = WellbeingModel.ensure_user_document(id_usuario)
        checkins = doc.get("checkins", [])
        checkins.sort(key=lambda c: c.get("fecha", ""), reverse=True)
        return checkins[:limit]

    @staticmethod
    def get_latest_checkin(id_usuario):
        doc = WellbeingModel.ensure_user_document(id_usuario)
        checkins = doc.get("checkins", [])
        if not checkins:
            return None
        checkins.sort(key=lambda c: c.get("fecha", ""), reverse=True)
        return checkins[0]

    @staticmethod
    def get_user_wellbeing_summary(id_usuario):
        doc = WellbeingModel.ensure_user_document(id_usuario)
        checkins = doc.get("checkins", [])

        if not checkins:
            return {
                "total_checkins": 0,
                "promedios": {},
                "ultimo_estado_animo_general": None,
                "ultima_frase": None,
                "fecha_ultimo_checkin": None,
                "ultimo_tipo_checkin": None
            }

        checkins_sorted = sorted(checkins, key=lambda c: c.get("fecha", ""), reverse=True)
        latest = checkins_sorted[0]
        total = len(checkins)

        metric_keys = set()
        for c in checkins:
            rm = c.get("resumen_metricas", {})
            metric_keys.update(rm.keys())

        promedios = {}
        for key in metric_keys:
            values = []
            for c in checkins:
                rm = c.get("resumen_metricas", {})
                if key in rm and isinstance(rm[key], (int, float)):
                    values.append(rm[key])
            if values:
                promedios[key] = round(sum(values) / len(values), 1)

        return {
            "total_checkins": total,
            "promedios": promedios,
            "ultimo_estado_animo_general": latest.get("estado_animo_general"),
            "ultima_frase": latest.get("frase", ""),
            "fecha_ultimo_checkin": latest.get("fecha"),
            "ultimo_tipo_checkin": latest.get("titulo_checkin")
        }

    @staticmethod
    def get_specialist_user_history(id_usuario):
        summary = WellbeingModel.get_user_wellbeing_summary(id_usuario)
        checkins = WellbeingModel.get_user_checkins(id_usuario, limit=20)
        return {
            "resumen": summary,
            "checkins": checkins
        }

    # =====================================================
    # MUSIC SETTINGS
    # =====================================================

    @staticmethod
    def update_music_settings(id_usuario, background_track=None, calm_mode_track=None, favorites=None):
        WellbeingModel.ensure_user_document(id_usuario)
        collection = WellbeingModel._collection()
        update = {"updated_at": WellbeingModel._now()}
        if background_track is not None:
            update["musica.background_track"] = background_track
        if calm_mode_track is not None:
            update["musica.calm_mode_track"] = calm_mode_track
        if favorites is not None:
            update["musica.favoritos"] = favorites
        collection.update_one({"id_usuario": id_usuario}, {"$set": update})
        return {"success": True, "message": "Configuración musical actualizada."}

    @staticmethod
    def get_music_settings(id_usuario):
        doc = WellbeingModel.ensure_user_document(id_usuario)
        musica = doc.get("musica", {})
        return {
            "background_track": musica.get("background_track"),
            "calm_mode_track": musica.get("calm_mode_track"),
            "favorites": musica.get("favoritos", [])
        }

    @staticmethod
    def toggle_favorite_music(id_usuario, track_id):
        WellbeingModel.ensure_user_document(id_usuario)
        collection = WellbeingModel._collection()
        doc = collection.find_one({"id_usuario": id_usuario})
        favoritos = doc.get("musica", {}).get("favoritos", [])
        if track_id in favoritos:
            collection.update_one(
                {"id_usuario": id_usuario},
                {"$pull": {"musica.favoritos": track_id}}
            )
            return {"success": True, "favorite": False, "message": "Favorito eliminado."}
        else:
            collection.update_one(
                {"id_usuario": id_usuario},
                {"$push": {"musica.favoritos": track_id}}
            )
            return {"success": True, "favorite": True, "message": "Favorito agregado."}
