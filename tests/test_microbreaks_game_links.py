from views.microbreaks_view import get_game_launcher_for_title


def test_break_titles_map_to_games():
    mapping = {
        "Patrones visuales": "LibreriaZen",
        "Toque consciente": "PaisajeBurbujasPastel",
        "Memoria ligera": "MemoramaEsteticoApp",
        "Observa y crece": "RefugioEstudiantil",
    }

    for title, expected_class_name in mapping.items():
        launcher = get_game_launcher_for_title(title)
        assert launcher is not None
        assert launcher.__name__ == expected_class_name
