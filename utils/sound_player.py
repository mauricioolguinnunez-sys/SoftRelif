from pathlib import Path
import threading
import time

import pygame


class SoundPlayer:
    """
    Reproductor global de SoftRelief.

    Funciones:
    - Reproducir vista previa.
    - Reproducir música para Modo Calma.
    - Reproducir Background Sound en loop.
    - Detener música al cerrar sesión.
    - Transición suave entre repeticiones.
    """

    initialized = False
    current_track = None
    current_mode = None
    volume = 0.65
    paused = False

    _loop_token = 0
    _fade_ms = 1200

    @classmethod
    def initialize(cls):
        if cls.initialized:
            return {
                "success": True,
                "message": "Audio inicializado."
            }

        try:
            pygame.mixer.init()
            cls.initialized = True

            return {
                "success": True,
                "message": "Audio inicializado."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo inicializar el audio: {error}"
            }

    @classmethod
    def get_length(cls, file_path):
        try:
            sound = pygame.mixer.Sound(str(file_path))
            return sound.get_length()
        except Exception:
            return None

    @classmethod
    def _play_once(cls, path, fade_ms=400):
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(cls.volume)
        pygame.mixer.music.play(loops=0, fade_ms=fade_ms)

    @classmethod
    def play(cls, file_path, mode="preview", loop=False, smooth_loop=False):
        init_result = cls.initialize()

        if not init_result["success"]:
            return init_result

        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "message": f"No existe el archivo de audio: {path}"
            }

        try:
            cls._loop_token += 1
            token = cls._loop_token

            try:
                pygame.mixer.music.fadeout(350)
                time.sleep(0.08)
            except Exception:
                pass

            cls.current_track = str(path)
            cls.current_mode = mode
            cls.paused = False

            if loop and smooth_loop:
                duration = cls.get_length(path)

                if not duration or duration <= 4:
                    pygame.mixer.music.load(str(path))
                    pygame.mixer.music.set_volume(cls.volume)
                    pygame.mixer.music.play(loops=-1, fade_ms=cls._fade_ms)

                    return {
                        "success": True,
                        "message": "Loop iniciado."
                    }

                cls._play_once(path, fade_ms=cls._fade_ms)

                thread = threading.Thread(
                    target=cls._smooth_loop_worker,
                    args=(path, duration, token),
                    daemon=True
                )
                thread.start()

                return {
                    "success": True,
                    "message": "Loop suave iniciado."
                }

            loops = -1 if loop else 0

            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(cls.volume)
            pygame.mixer.music.play(
                loops=loops,
                fade_ms=cls._fade_ms if loop else 350
            )

            return {
                "success": True,
                "message": "Reproducción iniciada."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo reproducir el audio: {error}"
            }

    @classmethod
    def _smooth_loop_worker(cls, path, duration, token):
        fade_seconds = cls._fade_ms / 1000
        restart_at = max(0.5, duration - fade_seconds)

        while token == cls._loop_token:
            time.sleep(0.25)

            if cls.paused:
                continue

            try:
                position_ms = pygame.mixer.music.get_pos()
            except Exception:
                break

            if position_ms < 0:
                continue

            position_seconds = position_ms / 1000

            if position_seconds >= restart_at:
                try:
                    pygame.mixer.music.fadeout(cls._fade_ms)
                    time.sleep(fade_seconds + 0.08)

                    if token != cls._loop_token:
                        break

                    cls._play_once(path, fade_ms=cls._fade_ms)

                except Exception:
                    break

    @classmethod
    def play_preview(cls, file_path):
        return cls.play(
            file_path=file_path,
            mode="preview",
            loop=False,
            smooth_loop=False
        )

    @classmethod
    def play_background(cls, file_path):
        return cls.play(
            file_path=file_path,
            mode="background",
            loop=True,
            smooth_loop=True
        )

    @classmethod
    def play_calm_mode(cls, file_path):
        return cls.play(
            file_path=file_path,
            mode="calm_mode",
            loop=True,
            smooth_loop=True
        )

    @classmethod
    def pause(cls):
        init_result = cls.initialize()

        if not init_result["success"]:
            return init_result

        try:
            pygame.mixer.music.pause()
            cls.paused = True

            return {
                "success": True,
                "message": "Música pausada."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo pausar la música: {error}"
            }

    @classmethod
    def resume(cls):
        init_result = cls.initialize()

        if not init_result["success"]:
            return init_result

        try:
            pygame.mixer.music.unpause()
            cls.paused = False

            return {
                "success": True,
                "message": "Música reanudada."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo reanudar la música: {error}"
            }

    @classmethod
    def stop(cls):
        if not cls.initialized:
            return {
                "success": True,
                "message": "Música detenida."
            }

        try:
            cls._loop_token += 1
            pygame.mixer.music.fadeout(450)

            cls.current_track = None
            cls.current_mode = None
            cls.paused = False

            return {
                "success": True,
                "message": "Música detenida."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo detener la música: {error}"
            }

    @classmethod
    def set_volume(cls, value):
        init_result = cls.initialize()

        if not init_result["success"]:
            return init_result

        try:
            value = float(value)
            value = max(0.0, min(1.0, value))

            cls.volume = value
            pygame.mixer.music.set_volume(value)

            return {
                "success": True,
                "message": "Volumen actualizado."
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"No se pudo actualizar el volumen: {error}"
            }

    @classmethod
    def get_status(cls):
        return {
            "track": cls.current_track,
            "mode": cls.current_mode,
            "volume": cls.volume,
            "paused": cls.paused,
        }