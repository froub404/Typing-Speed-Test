from visuals import pygame
import time

def generate_lines(text: str, space: pygame.Rect, font: pygame.font.Font):
    lines = []
    current_line = ""
    for word in text.split(" "):
        new_line = (current_line + " " + word).strip()
        width, height = font.size(new_line)
        if width > space.width:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line = new_line
    lines.append(current_line.strip())

    return lines

class Paragraph:
    def __init__(self, paragraph, space, font):
        self.paragraph = paragraph
        self.space = space
        self.font = font
        self.lines = generate_lines(paragraph, space, font)
        self.original_length = 0

        self.absolute_letter = 0
        self.current_letter = 0
        self.start = -1
        self.timelapse = -1

        self.inEvent = False

    def type(self, letter):
        if letter == self.lines[0][self.current_letter]:
            if self.current_letter+1 == len(self.lines[0]):
                self.lines.pop(0)
                self.current_letter = 0
            else:
                self.current_letter += 1
            self.absolute_letter += 1

            if self.start == -1:
                self.start = time.time()
            elif len(self.lines) == 0:
                self.timelapse = time.time() - self.start


    def start_event(self, change=""):
        self.lines += generate_lines(change, self.space, self.font)
        self.inEvent = True

    def end_event(self):
        self.lines = self.lines[:-1]
        self.inEvent = False

class Buddy:
    def __init__(self):
        self.instructions = []
        self.current_letter = 0
        self.speaking = False
        self.debounce = 1

    def speak(self):
        if self.speaking and self.instructions:
            if self.debounce >= 0:
                self.debounce -= 1
            else:
                self.debounce = 1
                if self.current_letter + 1 < len(self.instructions[0]):
                    self.current_letter += 1
                else:
                    self.speaking = False