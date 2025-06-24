import pygame as pg
import sys
from events import TEXT_EVENT, TEXT_FINISH_EVENT
from settings import *

class SpeechBubble:
    def __init__(self, game, character):
        self.font = pygame.font.SysFont(None, 24)
        self.game = game
        self.character = character
        self.full_text = ""
        self.visible_text = ""
        self.width = min(200, len(self.full_text)*10)
        self.height = 40 * (len(self.full_text) // 20)
        self.line_spacing = 15
        self.padding = 10
        

    def set_text(self, text):
        self.full_text = text
        self.width = min(max(100, len(self.full_text)*10),500)
        self.height = 25 * (len(self.full_text) // 20)
        self.visible_text = ""
        self.index = 0
        pg.time.set_timer(TEXT_EVENT, 20)

    def _wrap_text(self, text, font, max_width):
        """
        Split text into lines that fit within max_width, avoiding word breaks.
        """
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw(self):
        """
        instantaneously draw whatever text is passed - this will be called 
        many times as text is added one character at a time.
        """
#        if len(self.visible_text) == 0:
#            return
        if self.character.id == "player":
            pos = 500, HALF_HEIGHT + HALF_HEIGHT // 2
        else: # npc character talking
            pos = self.character.screen_x, HALF_HEIGHT
        bubble_rect = pygame.Rect(pos[0]-self.width //2, pos[1] - self.height, self.width, self.height)
        pygame.draw.rect(self.game.screen, (255,255,255), bubble_rect, border_radius=10 )
        pygame.draw.rect(self.game.screen, (0, 0, 0), bubble_rect, 2, border_radius=10 )
        # Word wrap visible_text
        lines = self._wrap_text(self.visible_text, self.font, self.width - 2 * self.padding)
 
        x, y = bubble_rect.center 
        x -= self.width // 2 
        y -= self.height // 2 
        for line in lines:
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.game.screen.blit(text_surface, (x+self.padding, y+self.padding))
            y += text_surface.get_height() + self.line_spacing

    def typing_input(self, event):
        self.width = min(max(100, len(self.visible_text)*20),500)
        self.height = max(100, 15 * (len(self.visible_text) // 20))
        if event.key == pg.K_BACKSPACE and len(self.visible_text) > 0:
            self.visible_text = self.visible_text[:-1]
        else:
            self.visible_text += event.unicode  # Add typed character


    def handle_event(self, event):
        # if text is being set by "set_text" function (i.e. for NPC)
        if event.type == TEXT_EVENT and self.full_text:
            if self.index < len(self.full_text):
                self.visible_text += self.full_text[self.index]
                self.index += 1
            elif self.game.conversation.now_talking.thinking:
                # don't send a TEXT_FINISH_EVENT
                pass
            else:
                pg.time.set_timer(TEXT_EVENT, 0)
                pg.time.set_timer(TEXT_FINISH_EVENT, 1000)
        # otherwise, text is set by player input
        elif event.type == pg.KEYDOWN and self.character.id == "player":
            if event.key == pg.K_RETURN:
                self.game.conversation.conversation_so_far.append(f"player: {self.visible_text}")
                pg.time.set_timer(TEXT_FINISH_EVENT, 500)
            else:
                self.typing_input(event)
