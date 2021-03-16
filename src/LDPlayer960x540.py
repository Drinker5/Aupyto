
from PIL import Image


class Images:
    additional_cargo = Image.open('images/additional_cargo.png')
    autopilot_disabled = Image.open('images/autopilot_disabled.png')
    autopilot_enabled = Image.open('images/autopilot_enabled.png')
    autopilot_stopped = Image.open('images/autopilot_stopped.png')
    delivery_hold = Image.open('images/delivery_hold.png')
    dialog_showing = Image.open('images/dialog_showing.png')
    docked = Image.open('images/docked.png')
    docked_citadel = Image.open('images/docked_citadel.png')
    engine_100 = Image.open('images/engine_100.png')
    inventory = Image.open('images/inventory.png')
    journal_delivery_mission_failed = Image.open(
        'images/journal_delivery_mission_failed.png')
    journal_delivery_mission_normal = Image.open(
        'images/journal_delivery_mission_normal.png')
    journal_have_items = Image.open('images/journal_have_items.png')
    local_window = Image.open('images/local_window.png')
    move_to = Image.open('images/move_to.png')
    move_to_window = Image.open('images/move_to_window.png')
    news_chain = Image.open('images/news_chain.png')
    npc_dialog_reply = Image.open('images/npc_dialog_reply.png')
    standings_ally = Image.open('images/standings_ally.png')
    standings_fleet = Image.open('images/standings_fleet.png')
    standings_green = Image.open('images/standings_green.png')
    standings_minus = Image.open('images/standings_minus.png')
    standings_plus = Image.open('images/standings_plus.png')
    warp_command = Image.open('images/warp_command.png')
    lock_command = Image.open('images/lock_command.png')
    approach_command = Image.open('images/approach_command.png')
    item_mode_compact = Image.open('images/item_mode_compact.png')
    selected_item_move_to = Image.open('images/selected_item_move_to.png')
    load_amount_window = Image.open('images/load_amount_window.png')
    ore_hold = Image.open('images/ore_hold.png')
    mineral_hold = Image.open('images/mineral_hold.png')


class Coordinates:
    window_rect = (0, 0, 960, 540)
    delta = (1, 36)

    menuButton = (10, 10, 79, 44)
    autopilot_rect = (0, 107, 40, 40)
    closeButton = (910, 15, 33, 33)
    undock_button = (800, 154, 155, 54)
    undock_button_citadel = (873, 149, 88, 52)

    quick_panel_first_button_rect = (2, 68, 72, 35)

    npc_dialog_rect = (7, 176, 432, 109)
    npc_dialog_with_reply_rect = (8, 290, 33, 86)
    npc_dialog_first_reply_rect = (14, 293, 416, 35)
    dialog_cancel_button = (622, 383, 155, 54)
    dialog_confirm_button = (789, 383, 155, 54)

    class Local:
        local_window_rect = (195, 55, 263, 328)
        users_relative_rect = (11, 41, 168, 176)

    class Menu:
        inventory_button = (208, 214, 85, 85)
        encountersButton = (97, 340, 174, 85)

    class Encounters:
        newsButton = (60, 80, 57, 131)
        journalButton = (843, 91, 54, 32)
        first_accepted_mission_rect = (397, 255, 425, 75)
        first_accepted_mission_react_button = (827, 255, 70, 75)

        class News:
            refresh_button = (539, 89, 119, 43)
            news_rect = (159, 261, 699, 230)
            accept_delta = (0, 50)

        class Journal:
            first_accepted_mission_rect = (156, 150, 335, 72)
            time_rect = (735, 45, 75, 26)
            mission_begin_button = (569, 429, 278, 47)
            mission_abandon_button = (746, 101, 103, 33)
            stage_rect = (560, 103, 62, 32)

    class Inventory:
        staton_toggle_rect = (10, 60, 190, 38)
        left_menu_rect = (10, 60, 190, 425)
        item_hangar_button = (13, 103, 186, 72)
        select_all_button = (697, 454, 77, 69)
        move_to_button = (17, 80, 197, 61)
        move_to_item_hangar_button = (360, 95, 146, 62)
        additional_cargo_search_rect = (470, 84, 185, 81)
        delivery_hold_additional_cargo_search_rect = (390, 17, 475, 192)
        item_mode_button = (739, 14, 38, 32)
        compact_items_grid = [
            (221, 65, 86, 101),
            (312, 65, 86, 101),
            (403, 65, 86, 101),
            (494, 65, 86, 101),
            (585, 65, 86, 101),
            (676, 65, 86, 101),
            (767, 65, 86, 101),
            (858, 65, 86, 101),

            (221, 170, 86, 101),
            (312, 170, 86, 101),
            (403, 170, 86, 101),
            (494, 170, 86, 101),
            (585, 170, 86, 101),
            (676, 170, 86, 101),
            (767, 170, 86, 101),
            (858, 170, 86, 101)
        ]
        item_move_to_ships = [
            (605, 96, 293, 57),
            (605, 162, 293, 57),
            (605, 226, 293, 57),
            (605, 288, 293, 57)
        ]
        item_move_to_ships_additional_cargo = [
            (911, 96, 40, 57),
            (911, 162, 40, 57),
            (911, 226, 40, 57),
            (911, 288, 40, 57)
        ]
        item_move_to_selected_ship_additional_cargo = (785, 42, 168, 45)
        move_to_load_maximum_point = (920, 178, 30, 47)
        move_to_load_ok_button = (837, 433, 107, 58)
        active_ship_with_toggled_station_rect = (12, 144, 116, 75)

    class Space:
        info_rect = (166, 378, 649, 36)
        engine_100_rect = (338, 467, 31, 16)
        zoom_rect = (462, 453, 36, 22)
        check_warp_pixel = (460, 495)
        not_in_warp_pixel_color = (201, 201, 199)
        # нумерация модулей справа на лево, снизу вверх
        # цифра - сетка из модулей
        modules = {
            8: [
                (886, 465, 67, 67),
                (808, 465, 67, 67),
                (730, 465, 67, 67),
                (657, 465, 67, 67),
                (886, 390, 67, 67),
                (808, 390, 67, 67),
                (730, 390, 67, 67),
                (657, 390, 67, 67)],
            12: [
                (892, 471, 54, 54),
                (834, 471, 54, 54),
                (777, 471, 54, 54),
                (717, 471, 54, 54),
                (660, 471, 54, 54),
                (601, 471, 54, 54),

                (892, 406, 54, 54),
                (834, 406, 54, 54),
                (777, 406, 54, 54),
                (717, 406, 54, 54),
                (660, 406, 54, 54),
                (601, 406, 54, 54)],
        }

        class Bookmarks:
            close_bookmarks_button = (177, 162, 39, 31)
            set_as_destination_button = (231, 162, 165, 53)
            bookmarks = [
                (2, 197, 170, 58),
                (2, 261, 170, 53),
                (2, 317, 170, 53)
            ]
            start_autopilot_buttons = [
                (174, 197, 50, 58),
                (174, 263, 50, 46),
                (174, 320, 50, 46)
            ]

        class Grid:
            open_grid_button = (908, 286, 31, 33)
            change_grid_dropdown_rect = (729, 1, 136, 38)
            select_grid_filter_rect = (727, 69, 186, 473)
            target_commands_rect = (539, 42, 185, 500)
            locked_target_commands_rect = (416, 78, 523, 302)

            first_lockable_target_rect = (647, 18, 47, 47)
            targets = [
                (726, 42, 187, 51),
                (726, 95, 187, 51),
                (726, 148, 187, 51),
                (726, 201, 187, 51),
                (726, 254, 187, 51),
                (726, 307, 187, 51),
                (726, 360, 187, 51),
                (726, 413, 187, 51),
                (726, 466, 187, 51)
            ]

            filters = [
                (727, 69, 186, 52),
                (727, 123, 186, 52),
                (727, 177, 186, 52),
                (727, 231, 186, 52),
                (727, 285, 186, 52),
                (727, 336, 186, 52),
                (727, 390, 186, 52),
                (727, 443, 186, 52),
                (727, 496, 186, 46),
            ]

            filter_tags = [
                (916, 41, 43, 45),
                (916, 87, 43, 45),
                (916, 133, 43, 45),
                (916, 179, 43, 45),
                (916, 225, 43, 45),
                (916, 271, 43, 45),
                (916, 317, 43, 45),
                (916, 363, 43, 45),
                (916, 409, 43, 45)
            ]
