class Door:
    def __init__(self, segment, engine):
        self.segment = segment
        self.id = segment.linedef_id
        self.is_opening = False
        self.is_closing = False
        self.is_open = False
        self.is_closed = True
        self.sound_effect = engine.door_sound
        self.target_height = self.segment.front_sector.ceil_height
        self.open_speed = 30
        

    def toggle_open(self):
        if self.is_open:
            self.is_closing = True
        else:
            self.is_opening = True

        self.sound_effect.play()


    def update(self):
        if self.is_opening:
            if self.segment.back_sector.ceil_height == self.target_height:
                print("DOOR OPEN!")
                self.is_opening = False
            else:
                self.segment.back_sector.ceil_height = min(
                    self.target_height,
                    self.segment.back_sector.ceil_height + self.open_speed
                )
        if self.is_open:
            self.segment.linedef.front_sidedef.middle_texture = None
            self.is_opening = False
