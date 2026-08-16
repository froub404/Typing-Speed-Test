import pygame
import classes
from event_data import events

def grab_text(level):
    with open(f"paragraphs/level{level}.txt", "r", encoding="utf-8") as f:
        return f.read()

def grab_instructions(level):
    with open(f"intermissions/level{level}.txt", "r", encoding="utf-8") as f:
        return [s.strip() for s in f.readlines() if s.strip()]

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.swidth, self.sheight = 800, 600
        self.screen = pygame.display.set_mode((self.swidth, self.sheight))
        pygame.display.set_caption('Typing Simulator')
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True

        self.fontSM = pygame.font.Font(None, 24)
        self.fontNM = pygame.font.Font(None, 36)
        self.fontMD = pygame.font.Font(None, 48)
        self.fontLG = pygame.font.Font(None, 72)

        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        self.face = pygame.image.load('assets/image.jpeg').convert_alpha()
        self.face.set_alpha(0)
        self.face = pygame.transform.scale(self.face, (self.swidth, self.sheight))

        pygame.mixer.music.load('assets/intermission.wav')
        pygame.mixer.music.play(-1)

        self.INTERMISSION = 0
        self.PLAYING = 1

        self.stage = self.INTERMISSION

        self.level = 0
        self.wpm = 0
        self.typing_space = pygame.Rect(10, self.sheight//3, self.swidth - 10, self.sheight//2)
        self.instructions_space = pygame.Rect(self.swidth//3, self.sheight//4, 400, 200)

        self.paragraph = classes.Paragraph(grab_text(self.level), self.typing_space, self.fontMD)
        self.buddy = classes.Buddy()
        self.buddy.instructions = grab_instructions(self.level)
        self.buddy.speaking = True

    def next_level(self):
        self.level += 1
        self.wpm = round((self.paragraph.paragraph.count(" ") / self.paragraph.timelapse) * 60, 2)
        self.stage = self.INTERMISSION
        self.paragraph = classes.Paragraph(grab_text(self.level), self.typing_space, self.fontMD)
        self.buddy.instructions = grab_instructions(self.level)
        self.buddy.speaking = True

        if self.level % 3 == 0: self.face.set_alpha(self.face.get_alpha()+1)
        if self.level == 14: pygame.mixer.music.stop()

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.stage == self.INTERMISSION:
                    if event.key == pygame.K_RETURN and self.buddy.instructions and not self.buddy.speaking:
                        self.buddy.current_letter = 0
                        self.buddy.instructions.pop(0)
                        self.buddy.speaking = True
                    elif event.key == pygame.K_RETURN and not self.buddy.instructions:
                        self.stage = self.PLAYING
                if self.stage == self.PLAYING:
                    self.paragraph.type(event.unicode)

    def update_events(self):
        if self.level in events:
            data = events[self.level]
            if self.paragraph.absolute_letter == data[0] and not self.paragraph.inEvent:
                self.paragraph.start_event(data[2])
            elif self.paragraph.absolute_letter == data[1] and self.paragraph.inEvent:
                if self.level == 14:
                    self.next_level()
                else:
                    self.paragraph.end_event()

    def update(self):
        if self.stage == self.PLAYING:
            if self.paragraph.timelapse != -1:
                self.next_level()
            else:
                self.update_events()
        elif self.stage == self.INTERMISSION:
            self.buddy.speak()

        if self.level == 14 and self.white != (0,0,0):
            self.white = tuple([max((n-3),0) for n in self.white])
            self.black = tuple([min((n+3),255) for n in self.black])
            self.face.set_alpha(10)
        elif self.level == 16 and self.paragraph.inEvent:
            self.face.set_alpha(self.face.get_alpha()+3)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load('assets/crash.mp3')
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play()

        if self.face.get_alpha() >= 255:
            quit()

    def display_stats(self):
        level_txt = self.fontSM.render(f"Level: {self.level}", True, self.black)
        self.screen.blit(level_txt, (10, 10))

        wpm_txt = self.fontSM.render(f"{self.wpm} WPM", True, self.black)
        self.screen.blit(wpm_txt, (self.swidth-wpm_txt.get_width()-5, 10))

    def display_instructions(self):
        x, y = self.instructions_space.x, self.instructions_space.y
        if self.buddy.instructions:
            text = self.buddy.instructions[0][:self.buddy.current_letter+1]
            lines = classes.generate_lines(text, self.instructions_space, self.fontNM)
            for line in lines:
                render = self.fontNM.render(line, True, self.black)
                self.screen.blit(render, (x, y))
                y += render.get_height()
        else:
            text = "Press 'Enter' to start!" if self.level < 16 else "Go ahead."
            render = self.fontNM.render(text, True, self.black)
            self.screen.blit(render, (x, y))

    def display_paragraph(self):
        x, y = self.typing_space.x, self.typing_space.y
        temp_y = y
        for line in self.paragraph.lines:
            render = self.fontMD.render(line, True, self.black)
            self.screen.blit(render, (x, temp_y))
            temp_y += render.get_height()

        lsize = self.fontMD.size(self.paragraph.lines[0][self.paragraph.current_letter])
        lx = x + self.fontMD.size(self.paragraph.lines[0][:self.paragraph.current_letter])[0]
        pygame.draw.line(self.screen, self.black, (lx, y + lsize[1]), (lx + lsize[0], y + lsize[1]), 3)

    def draw(self):
        self.screen.fill(self.white)
        self.screen.blit(self.face, pygame.Rect(0, 0, self.swidth, self.sheight))
        if self.stage == self.INTERMISSION:
            self.display_instructions()
        elif self.stage == self.PLAYING:
            self.display_paragraph()
        self.display_stats()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(self.FPS)
        quit()