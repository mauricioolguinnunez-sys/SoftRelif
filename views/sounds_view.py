import re
import customtkinter as ctk

from components import (
    SoftCard,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    SmallLabel,
    PrimaryButton,
    SecondaryButton,
)

from database.connection import get_connection
from utils.theme_manager import ThemeManager
from utils.music_catalog import get_all_music, get_music_by_id
from utils.music_state import (
    get_user_music_settings,
    update_user_music_setting,
    toggle_favorite_track,
)
from utils.sound_player import SoundPlayer
from utils.i18n import Lang


class SoundsView(ctk.CTkFrame):

    @staticmethod
    def get_filter_labels():
        return {
            "todos": Lang.get("sounds_filter_todos"),
            "concentracion": Lang.get("sounds_filter_concentracion"),
            "relajacion": Lang.get("sounds_filter_relajacion"),
            "sueno": Lang.get("sounds_filter_sueno"),
            "favoritos": Lang.get("sounds_filter_favoritos"),
            "sugeridos": Lang.get("sounds_filter_sugeridos"),
        }

    @staticmethod
    def get_filter_values():
        return [
            Lang.get("sounds_filter_todos"),
            Lang.get("sounds_filter_concentracion"),
            Lang.get("sounds_filter_relajacion"),
            Lang.get("sounds_filter_sueno"),
            Lang.get("sounds_filter_favoritos"),
            Lang.get("sounds_filter_sugeridos"),
        ]

    def __init__(self, master, app):
        self.app = app
        self.current_user = getattr(app, "current_user", None)

        self.theme_name = "light"

        if self.current_user:
            self.theme_name = self.current_user.get("tema_visual", "light")

        self.theme = ThemeManager.get_theme(self.theme_name)

        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=0
        )

        self.all_tracks = get_all_music()
        self.filtered_tracks = []
        self.recommendations = self.load_specialist_recommendations()
        self.specialist_suggestions = [
            recommendation["track_id"]
            for recommendation in self.recommendations
        ]

        self.selected_filter = "todos"
        self.selected_track = None

        self.current_columns = 2
        self.resize_job = None

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.apply_filters)

        self.filter_var = ctk.StringVar(value=Lang.get("sounds_filter_todos"))
        self.volume_var = ctk.DoubleVar(
            value=SoundPlayer.get_status().get("volume", 0.65)
        )

        self.track_grid = None
        self.message_label = None

        self.control_card = None
        self.player_icon = None
        self.player_title = None
        self.player_subtitle = None
        self.player_mode_label = None

        self.build_view()
        self.bind("<Configure>", self.on_resize)

    # =====================================================
    # HELPERS
    # =====================================================

    def c(self, key, default):
        return self.theme.get(key, default)

    def user_id(self):
        if not self.current_user:
            return None

        return self.current_user.get("id_usuario")

    def user_name(self):
        if not self.current_user:
            return "Usuario"

        return self.current_user.get("nombre", "Usuario")

    def clear_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()

    def get_music_settings(self):
        if not self.user_id():
            return {
                "calm_mode_track": None,
                "background_track": None,
                "favorites": [],
            }

        return get_user_music_settings(self.user_id())

    def show_message(self, text, error=False):
        if not self.message_label:
            return

        self.message_label.configure(
            text=text,
            text_color="#DC2626" if error else self.c("text_soft", "#6B7280")
        )

    def get_filter_id_from_label(self, label):
        label = str(label).lower()

        for filter_id, filter_label in self.get_filter_labels().items():
            if filter_label.lower() == label:
                return filter_id

        return "todos"

    # =====================================================
    # BUILD
    # =====================================================

    def build_view(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.build_header()
        self.build_toolbar()
        self.build_main_area()

        self.apply_filters()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(24, 12)
        )

        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        icon = ctk.CTkLabel(
            header,
            text="♫",
            width=72,
            height=72,
            corner_radius=36,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#8B5CF6"),
            font=("Arial", 34, "bold")
        )
        icon.grid(row=0, column=0, padx=(0, 18))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")

        TitleLabel(
            title_box,
            Lang.get("sounds_title"),
            size=34,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="w")

        SubtitleLabel(
            title_box,
            Lang.get("sounds_subtitle"),
            size=16,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="w", pady=(2, 0))

        user_box = ctk.CTkFrame(header, fg_color="transparent")
        user_box.grid(row=0, column=2, sticky="e")

        SmallLabel(
            user_box,
            Lang.get("sounds_hello", name=self.user_name()),
            size=14,
            text_color=self.c("text", "#1E1B4B")
        ).pack(anchor="e")

        SmallLabel(
            user_box,
            Lang.get("sounds_balance"),
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).pack(anchor="e")

    def build_toolbar(self):
        toolbar = SoftCard(
            self,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=22
        )
        toolbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 16)
        )

        toolbar.grid_columnconfigure(0, weight=0)
        toolbar.grid_columnconfigure(1, weight=1)
        toolbar.grid_columnconfigure(2, weight=0)

        segmented = ctk.CTkSegmentedButton(
            toolbar,
            values=self.get_filter_values(),
            variable=self.filter_var,
            height=36,
            corner_radius=14,
            selected_color=self.c("accent", "#8B5CF6"),
            selected_hover_color=self.c("button_hover", "#7C3AED"),
            unselected_color=self.c("app_bg", "#F6F7FB"),
            unselected_hover_color=self.c("menu_hover", "#F3F4F6"),
            text_color="#FFFFFF",
            command=self.on_filter_change
        )
        segmented.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=16
        )

        search = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            height=36,
            corner_radius=14,
            placeholder_text=Lang.get("sounds_search_placeholder"),
            fg_color=self.c("app_bg", "#F6F7FB"),
            border_color=self.c("card_border", "#E5E7EB"),
            text_color=self.c("text", "#1E1B4B")
        )
        search.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(16, 12),
            pady=16
        )

        SecondaryButton(
            toolbar,
            text=Lang.get("sounds_sort"),
            width=100,
            height=36,
            fg_color=self.c("app_bg", "#F6F7FB"),
            hover_color=self.c("menu_hover", "#F3F4F6"),
            text_color=self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            command=self.sort_tracks
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=(0, 18),
            pady=16
        )

    def build_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 18)
        )

        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 16)
        )
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        self.build_recommendation_box(left)
        self.build_tracks_area(left)

        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(
            row=0,
            column=1,
            sticky="nsew"
        )
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.build_music_control(right)

    def build_recommendation_box(self, parent):
        if not self.recommendations:
            spacer = ctk.CTkFrame(parent, fg_color="transparent", height=1)
            spacer.grid(row=0, column=0, sticky="ew")
            return

        card = ctk.CTkFrame(
            parent,
            fg_color="#FEF3C7",
            corner_radius=22,
            border_width=1,
            border_color="#F59E0B"
        )
        card.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 16)
        )
        card.grid_columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(
            card,
            text="★",
            width=58,
            height=58,
            corner_radius=29,
            fg_color="#F59E0B",
            text_color="#FFFFFF",
            font=("Arial", 28, "bold")
        )
        icon.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(18, 14),
            pady=18
        )

        TitleLabel(
            card,
            Lang.get("sounds_recommendation"),
            size=20,
            text_color="#78350F"
        ).grid(
            row=0,
            column=1,
            sticky="w",
            pady=(18, 2)
        )

        first = self.recommendations[0]
        track = first["track"]

        BodyLabel(
            card,
            Lang.get("sounds_recommendation_text", title=track['title'], description=track['description']),
            size=13,
            text_color="#92400E",
            wraplength=640
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(0, 18)
        )

        PrimaryButton(
            card,
            text=Lang.get("sounds_select"),
            width=130,
            height=36,
            command=lambda t=track: self.select_track(t)
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            padx=18,
            pady=18,
            sticky="e"
        )

    def build_tracks_area(self, parent):
        self.track_grid = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.c("card_border", "#E5E7EB"),
            scrollbar_button_hover_color=self.c("accent", "#8B5CF6")
        )
        self.track_grid.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

    def build_music_control(self, parent):
        self.control_card = SoftCard(
            parent,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            corner_radius=24
        )
        self.control_card.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.control_card.grid_columnconfigure(0, weight=1)
        self.control_card.grid_rowconfigure(7, weight=1)

        TitleLabel(
            self.control_card,
            Lang.get("sounds_control_title"),
            size=24,
            text_color=self.c("text", "#1E1B4B")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(24, 8)
        )

        self.player_icon = ctk.CTkLabel(
            self.control_card,
            text="♪",
            width=96,
            height=96,
            corner_radius=24,
            fg_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#8B5CF6"),
            font=("Arial", 42, "bold")
        )
        self.player_icon.grid(
            row=1,
            column=0,
            pady=(4, 14)
        )

        self.player_title = TitleLabel(
            self.control_card,
            Lang.get("sounds_no_sound_selected"),
            size=20,
            text_color=self.c("text", "#1E1B4B")
        )
        self.player_title.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 4)
        )

        self.player_subtitle = BodyLabel(
            self.control_card,
            Lang.get("sounds_select_hint"),
            size=13,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=280,
            justify="center"
        )
        self.player_subtitle.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 16)
        )

        controls = ctk.CTkFrame(self.control_card, fg_color="transparent")
        controls.grid(
            row=4,
            column=0,
            pady=(0, 16)
        )

        self.round_button(
            controls,
            text="▶",
            command=self.play_selected_preview,
            column=0,
            primary=True
        )

        self.round_button(
            controls,
            text="Ⅱ",
            command=self.pause_sound,
            column=1
        )

        self.round_button(
            controls,
            text="■",
            command=self.stop_sound,
            column=2
        )

        PrimaryButton(
            self.control_card,
            text=Lang.get("sounds_use_background"),
            height=38,
            command=self.set_selected_as_background
        ).grid(
            row=5,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 10)
        )

        SecondaryButton(
            self.control_card,
            text=Lang.get("sounds_use_calm_mode"),
            height=38,
            fg_color=self.c("app_bg", "#F6F7FB"),
            hover_color=self.c("menu_hover", "#F3F4F6"),
            text_color=self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            command=self.set_selected_as_calm_mode
        ).grid(
            row=6,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 16)
        )

        volume_box = ctk.CTkFrame(self.control_card, fg_color="transparent")
        volume_box.grid(
            row=8,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 14)
        )
        volume_box.grid_columnconfigure(0, weight=1)

        SmallLabel(
            volume_box,
            Lang.get("sounds_volume"),
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8)
        )

        slider = ctk.CTkSlider(
            volume_box,
            from_=0,
            to=1,
            variable=self.volume_var,
            command=self.change_volume,
            progress_color=self.c("accent", "#8B5CF6"),
            button_color=self.c("accent", "#8B5CF6"),
            button_hover_color=self.c("button_hover", "#7C3AED")
        )
        slider.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.message_label = SmallLabel(
            self.control_card,
            "",
            size=12,
            text_color=self.c("text_soft", "#6B7280")
        )
        self.message_label.grid(
            row=9,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 20)
        )

    def round_button(self, parent, text, command, column, primary=False):
        button = ctk.CTkButton(
            parent,
            text=text,
            width=46,
            height=46,
            corner_radius=23,
            fg_color=self.c("accent", "#8B5CF6") if primary else self.c("app_bg", "#F6F7FB"),
            hover_color=self.c("button_hover", "#7C3AED"),
            text_color="#FFFFFF" if primary else self.c("text_soft", "#6B7280"),
            border_width=0 if primary else 1,
            border_color=self.c("card_border", "#E5E7EB"),
            font=("Arial", 18, "bold"),
            command=command
        )
        button.grid(row=0, column=column, padx=6)

    # =====================================================
    # RESPONSIVE
    # =====================================================

    def on_resize(self, event):
        if event.widget != self:
            return

        if self.resize_job:
            self.after_cancel(self.resize_job)

        self.resize_job = self.after(150, self.update_columns)

    def update_columns(self):
        width = self.winfo_width()

        if width < 950:
            columns = 1
        elif width < 1350:
            columns = 2
        else:
            columns = 3

        if columns != self.current_columns:
            self.current_columns = columns
            self.draw_tracks()

    # =====================================================
    # FILTROS
    # =====================================================

    def on_filter_change(self, label):
        self.selected_filter = self.get_filter_id_from_label(label)
        self.apply_filters()

    def sort_tracks(self):
        self.all_tracks = sorted(
            self.all_tracks,
            key=lambda track: track.get("title", "")
        )
        self.apply_filters()
        self.show_message(Lang.get("sounds_sorted"))

    def apply_filters(self, *args):
        query = self.search_var.get().strip().lower()
        settings = self.get_music_settings()
        favorites = settings.get("favorites", [])

        tracks = self.all_tracks[:]

        if self.selected_filter == "favoritos":
            tracks = [
                track for track in tracks
                if track["id"] in favorites
            ]

        elif self.selected_filter == "sugeridos":
            tracks = [
                track for track in tracks
                if track["id"] in self.specialist_suggestions
            ]

        elif self.selected_filter != "todos":
            tracks = [
                track for track in tracks
                if track.get("category") == self.selected_filter
            ]

        if query:
            tracks = [
                track for track in tracks
                if query in track.get("title", "").lower()
                or query in track.get("description", "").lower()
                or query in track.get("category", "").lower()
            ]

        self.filtered_tracks = tracks
        self.draw_tracks()

    # =====================================================
    # CARDS
    # =====================================================

    def draw_tracks(self):
        if not self.track_grid:
            return

        self.clear_container(self.track_grid)

        for column in range(4):
            self.track_grid.grid_columnconfigure(column, weight=0)

        for column in range(self.current_columns):
            self.track_grid.grid_columnconfigure(
                column,
                weight=1,
                uniform="tracks"
            )

        if not self.filtered_tracks:
            BodyLabel(
                self.track_grid,
                Lang.get("sounds_no_results"),
                size=14,
                text_color=self.c("text_soft", "#6B7280")
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=12,
                pady=20
            )
            return

        for index, track in enumerate(self.filtered_tracks):
            row = index // self.current_columns
            column = index % self.current_columns
            self.create_track_card(track, row, column)

    def create_track_card(self, track, row, column):
        settings = self.get_music_settings()
        favorites = settings.get("favorites", [])

        is_selected = (
            self.selected_track
            and self.selected_track.get("id") == track.get("id")
        )

        is_favorite = track["id"] in favorites
        is_background = settings.get("background_track") == track["id"]
        is_calm = settings.get("calm_mode_track") == track["id"]
        is_suggested = track["id"] in self.specialist_suggestions

        card = SoftCard(
            self.track_grid,
            fg_color=self.c("card_bg", "#FFFFFF"),
            border_width=2 if is_selected else 1,
            border_color=self.c("accent", "#8B5CF6")
            if is_selected
            else self.c("card_border", "#E5E7EB"),
            corner_radius=24
        )
        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=8,
            pady=8
        )

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)

        cover = ctk.CTkLabel(
            card,
            text=track.get("icon", "♪"),
            width=92,
            height=92,
            corner_radius=18,
            fg_color=self.get_cover_color(track),
            text_color="#FFFFFF",
            font=("Arial", 36, "bold")
        )
        cover.grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(16, 14),
            pady=16,
            sticky="nw"
        )

        text_box = ctk.CTkFrame(card, fg_color="transparent")
        text_box.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(0, 14),
            pady=(16, 4)
        )
        text_box.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(text_box, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        TitleLabel(
            title_row,
            track["title"],
            size=17,
            text_color=self.c("text", "#1E1B4B")
        ).grid(row=0, column=0, sticky="w")

        fav_icon = "♥" if is_favorite else "♡"

        ctk.CTkButton(
            title_row,
            text=fav_icon,
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            hover_color=self.c("accent_soft", "#EDE9FE"),
            text_color=self.c("accent", "#8B5CF6")
            if is_favorite
            else self.c("text_soft", "#6B7280"),
            font=("Arial", 18, "bold"),
            command=lambda t=track: self.toggle_favorite(t)
        ).grid(row=0, column=1, sticky="e")

        BodyLabel(
            text_box,
            track.get("description", Lang.get("sounds_ambient")),
            size=12,
            text_color=self.c("text_soft", "#6B7280"),
            wraplength=240
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 8)
        )

        SmallLabel(
            text_box,
            self.get_badges_text(is_calm, is_background, is_suggested, track),
            size=11,
            text_color=self.c("accent", "#8B5CF6")
            if is_calm or is_background or is_suggested
            else self.c("text_soft", "#6B7280")
        ).grid(
            row=2,
            column=0,
            sticky="w"
        )

        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=16,
            pady=(0, 16)
        )
        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=0)

        SecondaryButton(
            action_row,
            text=Lang.get("sounds_select"),
            height=34,
            fg_color=self.c("accent_soft", "#EDE9FE")
            if is_selected
            else self.c("app_bg", "#F6F7FB"),
            hover_color=self.c("menu_hover", "#F3F4F6"),
            text_color=self.c("accent", "#8B5CF6")
            if is_selected
            else self.c("text", "#1E1B4B"),
            border_width=1,
            border_color=self.c("card_border", "#E5E7EB"),
            command=lambda t=track: self.select_track(t)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        PrimaryButton(
            action_row,
            text="▶",
            width=48,
            height=34,
            command=lambda t=track: self.play_preview(t)
        ).grid(row=0, column=1)

    def get_badges_text(self, is_calm, is_background, is_suggested, track):
        badges = []

        if is_suggested:
            badges.append(Lang.get("sounds_badge_recommendation"))

        if is_calm:
            badges.append(Lang.get("sounds_badge_calm_mode"))

        if is_background:
            badges.append(Lang.get("sounds_badge_background"))

        if badges:
            return " · ".join(badges)

        return track.get("duration", Lang.get("sounds_duration"))

    def get_cover_color(self, track):
        category = track.get("category")

        colors = {
            "relajacion": "#7CDBB8",
            "concentracion": "#8B5CF6",
            "sueno": "#1E3A8A",
        }

        return colors.get(category, self.c("accent", "#8B5CF6"))

    # =====================================================
    # REPRODUCCIÓN
    # =====================================================

    def select_track(self, track):
        self.selected_track = track
        self.update_player(track, Lang.get("sounds_selected"))
        self.draw_tracks()
        self.show_message(Lang.get("sounds_selected_track", title=track['title']))

    def update_player(self, track, status):
        if self.player_icon:
            self.player_icon.configure(text=track.get("icon", "♪"))

        if self.player_title:
            self.player_title.configure(text=track.get("title", "Sin título"))

        if self.player_subtitle:
            self.player_subtitle.configure(text=status)

    def play_preview(self, track):
        self.selected_track = track

        result = SoundPlayer.play_preview(track["file"])

        if result["success"]:
            self.update_player(track, Lang.get("sounds_preview"))
            self.draw_tracks()
            self.show_message(Lang.get("sounds_playing", title=track['title']))
        else:
            self.show_message(result["message"], error=True)

    def play_selected_preview(self):
        if not self.selected_track:
            self.show_message(Lang.get("sounds_select_first"), error=True)
            return

        self.play_preview(self.selected_track)

    def pause_sound(self):
        result = SoundPlayer.pause()
        self.show_message(result["message"], error=not result["success"])

    def stop_sound(self):
        result = SoundPlayer.stop()
        self.show_message(result["message"], error=not result["success"])

    def change_volume(self, value):
        SoundPlayer.set_volume(value)

    # =====================================================
    # ASIGNACIONES
    # =====================================================

    def set_selected_as_calm_mode(self):
        if not self.selected_track:
            self.show_message(Lang.get("sounds_select_first"), error=True)
            return

        if not self.user_id():
            self.show_message(Lang.get("sounds_no_user"), error=True)
            return

        result = update_user_music_setting(
            self.user_id(),
            "calm_mode_track",
            self.selected_track["id"]
        )

        if result["success"]:
            self.show_message(
                Lang.get("sounds_calm_mode_set", title=self.selected_track['title'])
            )
            self.apply_filters()
        else:
            self.show_message(result["message"], error=True)

    def set_selected_as_background(self):
        if not self.selected_track:
            self.show_message(Lang.get("sounds_select_first"), error=True)
            return

        if not self.user_id():
            self.show_message(Lang.get("sounds_no_user"), error=True)
            return

        result = update_user_music_setting(
            self.user_id(),
            "background_track",
            self.selected_track["id"]
        )

        if not result["success"]:
            self.show_message(result["message"], error=True)
            return

        play_result = SoundPlayer.play_background(self.selected_track["file"])

        if play_result["success"]:
            self.update_player(
                self.selected_track,
                Lang.get("sounds_background_active")
            )
            self.show_message(
                Lang.get("sounds_background_set", title=self.selected_track['title'])
            )
            self.apply_filters()
        else:
            self.show_message(play_result["message"], error=True)

    def toggle_favorite(self, track):
        if not self.user_id():
            self.show_message(Lang.get("sounds_no_user"), error=True)
            return

        result = toggle_favorite_track(
            self.user_id(),
            track["id"]
        )

        self.show_message(result["message"], error=not result["success"])
        self.apply_filters()

    # =====================================================
    # RECOMENDACIONES DEL ESPECIALISTA
    # =====================================================

    def load_specialist_recommendations(self):
        if not self.current_user:
            return []

        id_usuario = self.current_user.get("id_usuario")

        if not id_usuario:
            return []

        conexion = None
        cursor = None

        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    b.descripcion,
                    b.fecha_evento,
                    especialista.nombre AS especialista_nombre
                FROM bitacora_cuenta b
                LEFT JOIN usuario especialista
                    ON b.id_admin = especialista.id_usuario
                WHERE b.id_usuario = %s
                  AND b.accion = 'sugerir_musica'
                ORDER BY b.fecha_evento DESC;
            """, (id_usuario,))

            rows = cursor.fetchall()
            recommendations = []

            for row in rows:
                track_id = self.extract_track_id(row.get("descripcion", ""))
                track = get_music_by_id(track_id)

                if not track:
                    continue

                recommendations.append({
                    "track_id": track_id,
                    "track": track,
                    "fecha_evento": row.get("fecha_evento"),
                    "especialista_nombre": row.get("especialista_nombre", "Especialista"),
                })

            return recommendations

        except Exception:
            return []

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    def extract_track_id(self, descripcion):
        descripcion = str(descripcion)

        patterns = [
            r"ID:\s*([a-zA-Z0-9_\-]+)",
            r"Track:\s*([a-zA-Z0-9_\-]+)",
            r"track_id:\s*([a-zA-Z0-9_\-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, descripcion)

            if match:
                return match.group(1).strip()

        return None