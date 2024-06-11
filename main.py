import random
import time

import pygame
import requests
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
from random_word import RandomWords

from assets.wordle_words import *


def game():
    # Initialize pygame
    pygame.init()

    # Screen dimensions
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (190, 190, 190)
    LIGHT_GREY = (220, 220, 220)
    YELLOW = (255, 220, 0)
    GREEN = (0, 255, 0)

    # Fonts
    FONT_SIZE = 30
    FONT = pygame.font.SysFont(None, FONT_SIZE)

    # Create the screen object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Typing Game')

    # Initialize clock
    clock = pygame.time.Clock()

    # Game variables
    SPEED = 1.3
    user_word = ''
    score = 0
    lives = 5
    freezes = 0
    cooldown = 60
    max_cooldown = 60

    # Sound assets
    shoot_sound = pygame.mixer.Sound('assets/bap.mp3')
    ow_sound = pygame.mixer.Sound('assets/ow.mp3')

    # Level descriptions
    level_descriptions = {
        1: 'just type! press the space bar to complete a word',
        2: 'how many can you get?',
        3: f'do a wordle!'
    }

    # Level 1 variables
    words = []
    r = RandomWords()

    # Level 2 variables
    equations = []
    user_word_math = ''
    math_total = 0

    # Word class, handles position and speed
    class word:
        def __init__(self, name, x, y, speed=SPEED, answer=None):
            self.name = name
            self.x = x
            self.y = y
            self.speed = speed
            self.answer = answer

    # Used to create an instance of the word class
    def create_word(name=None, speed=None, answer=None):
        if not name:
            name = r.get_random_word()

            while len(name) > 8:
                name = r.get_random_word()

        right_bound = SCREEN_WIDTH - len(name) * FONT_SIZE

        x = random.randint(0, right_bound)
        y = 0

        if not speed:
            speed = SPEED

        return word(name, x, y, speed, answer)

    # Makes words visible
    def paste_text(text, topleft=None, center=None, font=FONT, color=BLACK, surface=screen):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        # pygame.draw.rect(surface, color, textRect, 0)
        if topleft:
            textrect.topleft = topleft
        else:
            textrect.center = center
        surface.blit(textobj, textrect)

    # Specialized for color coding wordle words
    def paste_wordle(text, font=FONT, colors=[GREY, GREY, GREY, GREY, GREY], surface=screen, y=0):
        textobjs = [font.render(text[i], 1, colors[i]) for i in range(5)]
        textrects = [textobj.get_rect() for textobj in textobjs]

        for i in range(5):
            textrects[i].center = (SCREEN_WIDTH / 2 + (i - 3) * FONT_SIZE / 2, y)
            surface.blit(textobjs[i], textrects[i])

    # Generate math equation and answer
    def create_math(operation=None):
        if not operation:
            operation = random.randint(1, 4)

        if operation == 1:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            c = a + b
            return (f'{a}+{b}', c)

        if operation == 2:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            c = abs(a - b)
            return (f'{max(a, b)}-{min(a, b)}', c)

        if operation == 3:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            c = a * b
            return (f'{a}*{b}', c)

        if operation == 4:
            b = random.randint(1, 10)
            c = random.randint(1, 10)
            a = b * c

            return (f'{a}/{b}', c)

    # Shows directions before level
    def show_title(n):
        skip = False

        now = pygame.time.get_ticks()
        while pygame.time.get_ticks() - now < 3000 and not skip:
            screen.fill(WHITE)

            paste_text(level_descriptions[n], center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        skip = True

                # check for quit
                elif event.type == QUIT:
                    skip = True

    # Main logic behind levels
    def dolevel(curr_level):
        nonlocal cooldown, words, user_word, user_word_math, math_total, score, lives, freezes, SPEED

        # Main typing level
        if curr_level in [1, 3]:
            show_title(1)

            SPEED += 0.4

            next_level = False
            while not next_level:

                screen.fill(WHITE)

                # determines frequency of words
                cooldown = max(0, cooldown - 1)

                # create word
                if cooldown == 0 and random.randint(1, int(max_cooldown)) == 1:
                    words.append(create_word())
                    cooldown = 60

                # move words
                for element in words:

                    try:
                        if pygame.time.get_ticks() - frozen_time > 4000:
                            element.y += element.speed
                    except:
                        element.y += element.speed

                    if element.y > SCREEN_HEIGHT - 50:
                        words.remove(element)
                        lives -= 1

                        pygame.mixer.Sound.play(ow_sound)

                        if lives == 0:
                            screen.fill(WHITE)

                            paste_text('You lose!', center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                            pygame.display.flip()

                            time.sleep(3)
                            return True

                    # show words
                    paste_text(element.name, topleft=(element.x, element.y))

                # Look at every event in the queue
                for event in pygame.event.get():

                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            return True

                        else:
                            key = pygame.key.name(event.key).lower()

                            if key == 'space':
                                if user_word == 'freeze' and freezes > 0:
                                    frozen_time = pygame.time.get_ticks()
                                    freezes -= 1

                                # remove object with corresponding word
                                first = len(words)
                                words = [word for word in words if word.name != user_word]
                                user_word = ''
                                last = len(words)

                                if first != last:
                                    score += 1

                                    if score % 10 == 0:
                                        next_level = True

                            elif key == 'backspace':
                                user_word = user_word[:-1]

                            else:
                                pygame.mixer.Sound.play(shoot_sound)
                                user_word += key

                    # check for quit
                    elif event.type == QUIT:
                        return True

                # display user's word
                paste_text(user_word, center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25))

                # scoreboard
                pygame.draw.rect(screen, GREY, pygame.Rect(10, 10, 150, 70))
                paste_text('Score: ' + str(score), topleft=(20, 20))
                paste_text('Lives: ' + str(lives), topleft=(20, 50))

                pygame.draw.rect(screen, GREY, pygame.Rect(SCREEN_WIDTH - 160, 10, 150, 70))
                paste_text('Freezes: ' + str(freezes), topleft=(SCREEN_WIDTH - 150, 20))

                pygame.display.flip()
                clock.tick(60)

        # Math level
        elif curr_level == 2:
            show_title(2)

            now = pygame.time.get_ticks()
            math_total = 0
            equations = []
            user_word_math = ''

            next_level = False
            while not next_level and pygame.time.get_ticks() - now < 15000:
                cooldown = max(0, cooldown - 1)

                # create word
                # print(cooldown, max_cooldown)
                if cooldown == 0 and random.randint(1, 10) == 1:
                    # words.append(create_word(name=random.choice(word_list)))
                    new_math = create_math()

                    new_equation = create_word(name=new_math[0], answer=new_math[1])
                    equations.append(new_equation)
                    # print(new_equation.name, new_equation.x, new_equation.y, new_equation.answer)
                    cooldown = 20

                screen.fill(WHITE)

                # move words
                for element in equations:
                    element.y += element.speed

                    if element.y > SCREEN_HEIGHT - 50:
                        equations.remove(element)

                    # show words
                    paste_text(element.name, topleft=(element.x, element.y), color=BLACK)

                # Look at every event in the queue
                for event in pygame.event.get():

                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            return True

                        else:
                            key = pygame.key.name(event.key).lower()

                            if key == 'space':
                                # remove object with corresponding word
                                try:
                                    user_word_math = int(user_word_math)
                                except:
                                    continue

                                for equation in equations:
                                    if equation.answer == int(user_word_math):
                                        math_total += equation.answer
                                        equations.remove(equation)

                                user_word_math = ''

                            elif key == 'backspace':
                                user_word_math = user_word_math[:-1]

                            else:
                                pygame.mixer.Sound.play(shoot_sound)

                                try:
                                    if int(key) in range(10):
                                        user_word_math += key
                                except:
                                    continue

                                # print(user_word_math)

                    # check for quit
                    elif event.type == QUIT:
                        return True

                paste_text(user_word_math, center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25), color=BLACK)

                pygame.draw.rect(screen, LIGHT_GREY, pygame.Rect(10, 10, SCREEN_WIDTH - 20, 70))
                pygame.draw.rect(screen, GREY,
                                 pygame.Rect(10, 10, min((SCREEN_WIDTH - 20) * math_total / 300, SCREEN_WIDTH - 20),
                                             70))
                paste_text('Total: ' + str(math_total), topleft=(20, 20))

                clock.tick(60)
                pygame.display.flip()

            # awards player a freeze
            freezes += 1 * (math_total > 300)

        # wordle level
        elif curr_level == 4:
            show_title(3)

            screen.fill(WHITE)

            # for today's wordle
            # current_date = datetime.now()
            # formatted_date = current_date.strftime('%Y-%m-%d')

            # generates random wordle
            while True:
                try:
                    year = random.choice(['2021', '2022', '2023', '2024'])

                    month = random.randint(1, 12)
                    if month < 10:
                        month = '0' + str(month)
                    else:
                        month = str(month)

                    day = random.randint(1, 31)
                    if day < 10:
                        day = str('0' + str(month))
                    else:
                        day = str(month)

                    formatted_date = f'{year}-{month}-{day}'

                    url = f"https://www.nytimes.com/svc/wordle/v2/{formatted_date}.json"

                    response = requests.get(url)
                    data = dict(response.json())
                    break

                except:
                    continue

            wordle_guess = ''
            wordle_display = ['?????']
            colors = [[GREY, GREY, GREY, GREY, GREY]]

            wordle_guess = ''

            wordle = create_word(name=wordle_guess, speed=0.1, answer=data['solution'])
            wordle.x = SCREEN_WIDTH / 2

            # print(wordle.answer, formatted_date)

            next_level = False
            now = pygame.time.get_ticks()
            while not next_level and pygame.time.get_ticks() - now < 120000:

                screen.fill(WHITE)

                # Look at every event in the queue
                for event in pygame.event.get():

                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            return True

                        else:
                            key = pygame.key.name(event.key).lower()

                            if key == 'space':
                                if len(wordle_guess) == 5 and wordle_guess in all_words:
                                    if '?????' in wordle_display:
                                        colors = []
                                        wordle_display = [wordle_guess]
                                    else:
                                        wordle_display.append(wordle_guess)

                                    temp_colors = [GREY, GREY, GREY, GREY, GREY]
                                    for i in range(5):
                                        if wordle_guess[i] == wordle.answer[i]:
                                            temp_colors[i] = GREEN

                                        elif wordle_guess[i] in wordle.answer:
                                            temp_colors[i] = YELLOW

                                    colors.append(temp_colors)

                                    if wordle_guess == wordle.answer:
                                        lives += 1
                                        next_level = True

                                    elif len(wordle_display) == 6:
                                        next_level = True

                                wordle_guess = ''

                            elif key == 'backspace':
                                wordle_guess = wordle_guess[:-1]

                            else:
                                pygame.mixer.Sound.play(shoot_sound)

                                wordle_guess += key

                    # check for quit
                    elif event.type == QUIT:
                        return True

                paste_text(wordle_guess, center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25), color=BLACK)

                for i in range(len(wordle_display)):
                    paste_wordle(wordle_display[i], colors=colors[i], y=200 + i * FONT_SIZE)

                clock.tick(60)
                pygame.display.flip()

                if next_level:
                    time.sleep(3)

    # initialize level at 1
    curr_level = 1

    #  main game loop; iterates through levels 1-4
    while True:
        if dolevel(curr_level):
            break
        else:
            curr_level = (curr_level + 1) % 4 + 4 * (curr_level == 3)


if __name__ == '__main__':
    game()
