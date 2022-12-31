def get_tip():
    if tip_available == False:
        return {'Error': "Stock", "Required": "Restock"}
    else:
        def prepare_tip_for_pickup():
            if tip_available_in_tray == False:
                def discard_current_tray():
                    if current_tray_present:
                        def slider_move_to_discard():
                            pass
                        def discard_pickup_current_tray():
                            pass
                        if discard_success == False:
                            return {"Error":"Tray", "Required":"Maintenance"}
            if tip_available_in_tray == True:
                def load_new_tray():
                    if tray_available ==False:
                        return {"Error":"Stock", "Required":"Restock"}
                    def slider_move_to_load():
                        pass
                    def load_nex_tray():
                        pass
                    if load_success == False:   
                        return {"Error":"Load", "Required":"Maintenance"}
            def move_tip_slider_to_pos():
                if already_in_pos == False:
                    def move_tip_slider():
                        pass
                    if slider_reached == False:
                        return {"Error":"Tray", "Required":"Maintenance"}
        def pick_up_using_orchestrator():
            def pick_up_tip():
                pass
            if caught_tip_firm_and_orient == False:
                def discard_tip():
                    def goto_discard_position():
                        pass
                    def prepare_to_discard():
                        pass
                    def eject_tip():
                        pass
                    if discard_up_success == False:
                        if retry_count_below_threshold:
                            return {"Error":"Tip", "Required":"Maintenance"}
                        else:
                            return {"Exception":"Retry", "Retry_count":count+1}
        def pick_up_success():
            pass