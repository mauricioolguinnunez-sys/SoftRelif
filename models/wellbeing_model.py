from database.mongo_connection import get_wellbeing_collection
from utils.date_utils import now_str


class WellbeingModel:

    COLLECTION = None

    @classmethod
    def _collection(cls):
        if cls.COLLECTION is None:
            cls.COLLECTION = get_wellbeing_collection()
        return cls.COLLECTION

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
            "created_at": now_str(),
            "updated_at": now_str()
        }
        collection.insert_one(doc)
        return doc

    # =====================================================
    # MUSIC SETTINGS
    # =====================================================

    @staticmethod
    def update_music_settings(id_usuario, background_track=None, calm_mode_track=None, favorites=None):
        WellbeingModel.ensure_user_document(id_usuario)
        collection = WellbeingModel._collection()
        update = {"updated_at": now_str()}
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
