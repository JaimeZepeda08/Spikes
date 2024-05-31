import pygame 
import pickle
import neat
import numpy as np 
import pandas as pd
import random
import os
import time

pygame.init()

WIDTH, HEIGHT = 450, 750
CENTER = 325

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Don't Touch the Spikes")

ICON_IMG = pygame.image.load(os.path.join("Assets", "Icon.png"))
pygame.display.set_icon(ICON_IMG)

FPS = 60

STATS_DF = pd.read_csv(os.path.join("CSV Files", "GameStats.csv"))
BIRDS_DF = pd.read_csv(os.path.join("CSV Files", "Birds.csv"))

#Fonts
FONT = "RussoOne-Regular.ttf"
SCORE_FONT = pygame.font.Font(os.path.join("Assets", FONT), 125)
TITLE_FONT = pygame.font.Font(os.path.join("Assets", FONT), 50)
STATSFONT = pygame.font.Font(os.path.join("Assets", FONT), 30)
STATSFONT_2 = pygame.font.Font(os.path.join("Assets", FONT), 20)

#Birds
BIRD_IMG1 = pygame.image.load(os.path.join("Assets", "Bird1.webp"))
BIRD_IMG2 = pygame.image.load(os.path.join("Assets", "Bird2.webp"))
BIRD_IMG3 = pygame.image.load(os.path.join("Assets", "Bird3.webp"))
BIRD_IMG4 = pygame.image.load(os.path.join("Assets", "Bird4.webp"))
BIRD_IMG5 = pygame.image.load(os.path.join("Assets", "Bird5.webp"))
BIRD_IMG6 = pygame.image.load(os.path.join("Assets", "Bird6.webp"))

#Trails
TRAIL_CIRCLE_BLACK = pygame.image.load(os.path.join("Assets", "trail_circle_black.png"))

#Spikes
TOP_SPIKES_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "SpikeBase.png")), ((WIDTH, 16))) 
BOTTOM_SPIKES_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "SpikeBase.png")), (WIDTH, HEIGHT - (CENTER + 324)))
SPIKE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Spike.png")), (30, 50))

#Misc
CANDY_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Candy.webp")), (60, 60))
CIRCLE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "circle.png")), (280, 280))
FRAME_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Frame.png")), (120, 140)) 
FRAME_PRICE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "FramePrice.png")), (120, 40)) 
SELECTED_FRAME_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "SelectedFrame.png")), (120, 140))
SHOP_ICON = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "ShopIcon.png")), (80, 80))

#Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (135, 135, 135)
WHITEGREY = (212, 212, 212) 
ORANGE = (237, 120, 47)
RED = (235, 52, 85)

B_WHITEGREY = [[212, 212, 212], [112, 112, 112]]
B_WHITEBLUE = [[213, 228, 235], [113, 128, 135]]
B_WHITERED = [[240, 216, 209], [140, 116, 109]]
B_WHITEGREEN = [[200, 217, 197], [100, 117, 97]]
B_WHITEPURPLE = [[212, 200, 219], [112, 100, 119]]
B_GREY = [[133, 133, 133], [33, 33, 33]]
B_BLUE = [[11, 113, 150], [0, 13, 50]]
B_GREEN = [[23, 150, 11], [0, 50, 0]]
B_PURPLEBLUE = [[15, 11, 153], [0, 0, 53]]
B_DARKRED = [[153, 11, 70], [53, 0, 0]]
B_ORANGE = [[255, 170, 23], [155, 70, 0]]
B_LIGHTBLUE = [[59, 186, 255], [0, 86, 155]]
B_VIOLET = [[156, 77, 209], [56, 0, 109]]
B_NEONGREEN = [[145, 219, 42], [45, 119, 0]]
B_BLACK = [[0, 0, 0], [100, 100, 100]]
B_PINK = [[234, 185, 237], [134, 85, 137]]
B_GREYBLUE = [[140, 180, 209], [40, 80, 109]]
B_GREYGREEN = [[157, 209, 163], [57, 109, 63]]
B_PURPLE = [[169, 144, 222], [69, 44, 122]]
B_GREENBLUE = [[129, 219, 212], [29, 119, 112]]
B_FINAL = [[0, 0, 0], [150, 0, 0]]

COLORLIST = [B_WHITEGREY, B_WHITEBLUE, B_WHITERED, B_WHITEGREEN, 
			B_WHITEPURPLE, B_GREY, B_BLUE, B_GREEN, B_PURPLEBLUE,
			B_DARKRED, B_ORANGE, B_LIGHTBLUE, B_VIOLET, B_NEONGREEN, B_BLACK, 
			B_PINK, B_GREYBLUE, B_GREYGREEN, B_PURPLE, B_GREENBLUE, B_FINAL]

class Game_Manager:
	def __init__(self):
		self.best_score = 0 
		self.games_played = 0 
		self.candy = 0

		self.bird = None

		self.main_screen = True
		self.game_started = False
		self.in_shop = False

		self.config = None

	def load_stats(self, stats_csv):
		self.best_score = stats_csv["Best Score"][0]
		self.games_played = stats_csv["Games Played"][0]
		self.candy = stats_csv["Candy"][0]

	def save_stats(self, stats_csv):
		stats_csv["Best Score"][0] = self.best_score 
		stats_csv["Games Played"][0] = self.games_played 
		stats_csv["Candy"][0] = self.candy

	def get_best_score(self):
		return self.best_score

	def get_games_played(self):
		return self.games_played
	
	def get_candy(self):
		return self.candy

	def set_best_score(self, best_score):
		self.best_score = best_score

	def increase_games_played(self):
		self.games_played += 1

	def set_candy(self, amount):
		self.candy += amount

	def load_birds(self, birds_csv, birds_arr):
		for i in range(len(birds_arr)):
			key = "bird" + str(i + 1)
			is_unlocked = True if birds_csv[key][0] == 1 else False
			is_selected = True if birds_csv[key][1] == 1 else False
			birds_arr[i].set_unlocked(is_unlocked)
			birds_arr[i].set_selected(is_selected)

	def save_birds(self, birds_csv, birds_arr):
		for i in range(len(birds_arr)):
			key = "bird" + str(i + 1)
			is_unlocked = 1 if birds_arr[i].unlocked == True else 0
			is_selected = 1 if birds_arr[i].selected == True else 0
			birds_csv[key][0] = is_unlocked
			birds_csv[key][1] = is_selected

	def get_bird(self):
		return self.bird

	def set_bird(self, new_bird):
		self.bird = new_bird

	def start_game(self):
		self.main_screen = False
		self.game_started = True
		self.in_shop = False

	def go_to_main_screen(self):
		self.main_screen = True
		self.game_started = False
		self.in_shop = False

	def open_shop(self):
		self.main_screen = False
		self.game_started = False
		self.in_shop = True

	def reset_game(self, bird, spike_manager, counter, background):
		bird.reset()
		spike_manager.reset()
		counter.reset()
		background.reset()

class Bird: 
	def __init__(self, img, trail_img):
		self.img = pygame.transform.scale(img, (65, 50))
		self.rect = self.img.get_rect()

		self.rect.x = (WIDTH / 2) - (self.img.get_width() / 2)
		self.rect.y = CENTER - (self.img.get_height() / 2)
	
		self.velocity = 5
		self.tick_count = 0 
		self.jump_force = 0
		self.dy = self.jump_force * self.tick_count + 0.5 * self.tick_count ** 2 

		self.idle_count = 0
		self.initial_y_pos = self.rect.y 

		self.trail_img = pygame.transform.scale(trail_img, (25, 25))
		self.trail_tick = 0
		self.trail_count = 4
		self.trail = []
		self.trail_pos = []
		self.trail_size = []

		self.genome = None

	def get_distance_from_wall(self):
		if self.velocity > 0:
			return WIDTH - self.rect.x
		else:
			return self.rect.x 

	def move(self):
		#Horizontal movement 
		self.rect.x += self.velocity

		#Vertical Movement 
		self.tick_count += 0.35

		self.dy = self.jump_force * self.tick_count + 0.5 * self.tick_count ** 2 
		if self.dy >= 10:
			self.dy = 10 
		if self.dy < 0:
			self.dy -= 1 

		self.rect.y += self.dy

	def idle(self, amplitude):
		self.idle_count += 1
		self.rect.y = self.initial_y_pos + (amplitude * np.sin(self.idle_count / 15))

	def bounce_off_wall(self):
		self.velocity *= -1
		self.img = pygame.transform.flip(self.img, True, False)

	def jump(self, force):
		self.tick_count = 0
		self.jump_force = -1 * force 

		self.trail_tick = 0 
		self.trail_count = 4

	def update_trail(self):
		self.trail_tick += 1
		if (self.trail_tick % 5 == 0 and self.trail_count > 0):
			self.trail.append(self.trail_img)
			if (self.velocity > 0):
				self.trail_pos.append((self.rect.x - (self.img.get_width() / 4), self.rect.y + (self.img.get_height() / 1.5)))
			else:
				self.trail_pos.append((self.rect.x + (self.img.get_width() / 2), self.rect.y + (self.img.get_height() / 1.5)))
			self.trail_size.append(25)
			self.trail_count -= 1

		if (self.trail_tick % 2 == 0):
			for i in range(len(self.trail)):
				self.trail_size[i] -= 3
				if (self.trail_size[i] > 1):
					self.trail[i] = pygame.transform.scale(self.trail[i], (self.trail_size[i], self.trail_size[i]))
				else: 
					self.trail.remove(self.trail[i])
					self.trail_pos.remove(self.trail_pos[i])
					self.trail_size.remove(self.trail_size[i])
					break

	def get_trail(self):
		return self.trail

	def get_trail_pos(self):
		return self.trail_pos

	def reset(self):
		self.rect.x = (WIDTH / 2) - (self.img.get_width() / 2)
		self.rect.y = CENTER - (self.img.get_height() / 2)

		if (self.velocity < 0):
			self.bounce_off_wall()

		self.trail_tick = 0
		self.trail_count = 4
		self.trail = []
		self.trail_pos = []
		self.trail_size = []

	def draw(self, win):
		win.blit(self.img, self.rect)


class Collidable:
	def __init__(self, x_pos, y_pos, img):
		self.img = img 
		self.rect = img.get_rect()

		self.rect.x = x_pos 
		self.rect.y = y_pos 

	def collide(self, bird):
		mask = pygame.mask.from_surface(self.img)
		bird_mask = pygame.mask.from_surface(bird.img)
		x_offset =  bird.rect.x - self.rect.x
		y_offset = bird.rect.y - self.rect.y
		point_of_intersection = mask.overlap(bird_mask, (x_offset, y_offset))
		if (point_of_intersection != None):
			return True
		else:
			return False

class Spike(Collidable): 
	def __init__(self, x_pos, y_pos, right):
		if (right):
			self.img = pygame.transform.flip(SPIKE_IMG, True, False)  
		else: 
			self.img = SPIKE_IMG
		self.rect = self.img.get_rect()

		self.rect.x = x_pos 
		self.rect.y = y_pos

		super().__init__(self.rect.x, self.rect.y, self.img)

		self.colors = COLORLIST
		self.color_index = background.get_color_index()
		self.current_color = self.colors[background.get_color_index()][1]
		self.new_color = None 
		self.changing_color = False
		self.change_rate = 1

	def get_current_color(self):
		return self.current_color

	def change_color(self):
		if (self.color_index < len(self.colors) - 1):
			self.color_index += 1
		self.new_color = self.colors[background.get_color_index()][1]

		self.changing_color = True

	def fade_color(self):
		if (self.changing_color):
			updated_color = [self.current_color[0], self.current_color[1], self.current_color[2]]
			
			if (self.current_color[0] == self.new_color[0] and self.current_color[1] == self.new_color[1] and self.current_color[2] == self.new_color[2]):
				self.changing_color = False

			if (self.current_color[0] > self.new_color[0]):
				updated_color[0] -= self.change_rate
			elif (self.current_color[0] < self.new_color[0]):
				updated_color[0] += self.change_rate

			if (self.current_color[1] > self.new_color[1]):
				updated_color[1] -= self.change_rate
			elif (self.current_color[1] < self.new_color[1]):
				updated_color[1] += self.change_rate

			if (self.current_color[2] > self.new_color[2]):
				updated_color[2] -= self.change_rate
			elif (self.current_color[2] < self.new_color[2]):
				updated_color[2] += self.change_rate

			self.current_color = [updated_color[0], updated_color[1], updated_color[2]]

	def draw(self, win):
		win.blit(self.img, (self.rect.x, self.rect.y))

class Spike_Manager: 
	def __init__(self):
		self.TOP_SPIKES_Y = 10
		self.BOTTOM_SPIKES_Y = CENTER + 350 - SPIKE_IMG.get_height() 

		self.chance_of_spike = 3 
		self.max_spikes = (HEIGHT - (HEIGHT - self.BOTTOM_SPIKES_Y) - (self.TOP_SPIKES_Y + SPIKE_IMG.get_height())) // SPIKE_IMG.get_height()

		self.spikes = []
 	
	def get_spikes(self):
		return self.spikes

	def generate_spikes(self, right):
		for i in range(self.max_spikes):
			rand = random.randint(1, 10)
			if (rand <= self.chance_of_spike):
				y_pos = (i * SPIKE_IMG.get_height()) + self.TOP_SPIKES_Y + SPIKE_IMG.get_height()
				if (right):
					self.spikes.append(Spike(WIDTH - SPIKE_IMG.get_width(), y_pos, right)) 
				else:
					self.spikes.append(Spike(0, y_pos, right)) 
			else:
				self.spikes.append(None)

		total_spikes = 0
		for spike in self.spikes: 
			if spike != None:
				total_spikes += 1
		if total_spikes == 0:
			self.generate_spikes(right)
		if total_spikes == self.max_spikes:
			self.generate_spikes(right)

	def update_chance_of_spike(self, score):
		if (self.chance_of_spike < 6):
			self.chance_of_spike += score / 10
	
	def reset(self):
		self.spikes = []
		self.chance_of_spike = 2

	def draw(self, win):
		for spike in self.spikes:
			if (spike != None):
				spike.draw(win)

class Candy(Collidable): 
	def __init__(self):
		self.img = CANDY_IMG
		self.rect = self.img.get_rect()

		self.rect.x = SPIKE_IMG.get_width() + 10
		self.rect.y = random.randint(20 + SPIKE_IMG.get_height() + 15, CENTER + 320 - SPIKE_IMG.get_height() - CANDY_IMG.get_height() - 15) 

		self.right = True

		self.initial_y_pos = self.rect.y
		self.idle_count = 0 

		super().__init__(self.rect.x, self.rect.y, self.img)

	def spawn_candy(self):
		if (self.right):
			self.rect.x = WIDTH - self.img.get_width() - SPIKE_IMG.get_width() - 10
			self.right = False
		else:
			self.rect.x = SPIKE_IMG.get_width() + 10
			self.right = True

		self.rect.y = random.randint(20 + SPIKE_IMG.get_height() + 15, CENTER + 320 - SPIKE_IMG.get_height() - self.img.get_height() - 15) 
		self.initial_y_pos = self.rect.y

	def idle(self, amplitude):
		self.idle_count += 1
		self.rect.y = self.initial_y_pos + (amplitude * np.sin(self.idle_count / 15))

	def draw(self, win):
		win.blit(self.img, (self.rect.x, self.rect.y))

class Background(): 
	def __init__(self):
		self.colors = COLORLIST
		self.color_index = 0
		self.current_color = self.colors[self.color_index][0]
		self.new_color = None 
		self.changing_color = False
		self.change_rate = 2

	def get_current_color(self):
		return self.current_color
	
	def get_color_index(self):
		return self.color_index

	def change_color(self):
		if (self.color_index < len(self.colors) - 1):
			self.color_index += 1
		self.new_color = self.colors[self.color_index][0]

		self.changing_color = True

	def fade_color(self):
		if (self.changing_color):
			updated_color = [self.current_color[0], self.current_color[1], self.current_color[2]]
			
			if (self.current_color[0] == self.new_color[0] and self.current_color[1] == self.new_color[1] and self.current_color[2] == self.new_color[2]):
				self.changing_color = False

			if (self.current_color[0] > self.new_color[0]):
				updated_color[0] -= self.change_rate
			elif (self.current_color[0] < self.new_color[0]):
				updated_color[0] += self.change_rate

			if (self.current_color[1] > self.new_color[1]):
				updated_color[1] -= self.change_rate
			elif (self.current_color[1] < self.new_color[1]):
				updated_color[1] += self.change_rate

			if (self.current_color[2] > self.new_color[2]):
				updated_color[2] -= self.change_rate
			elif (self.current_color[2] < self.new_color[2]):
				updated_color[2] += self.change_rate

			self.current_color = (updated_color[0], updated_color[1], updated_color[2])

	def reset(self):
		self.changing_color = False
		self.color_index = 0
		self.current_color = self.colors[self.color_index][0]

class Counter: 
	def __init__(self):
		self.count = 0 

	def increase(self):
		self.count += 1

	def get_count(self):
		return self.count

	def reset(self):
		self.count = 0

	def draw(self, color, win):
		if (self.count < 10):
			score = "0" + str(self.count)
		else:
			score = self.count
		score_text = SCORE_FONT.render(str(score), 0, background.get_current_color())
		win.blit(score_text, ((WIDTH / 2) - (score_text.get_width() / 2), CENTER - (score_text.get_height() / 2)))

class Button:
	def __init__(self, x_pos, y_pos, img):
		self.img = img

		self.rect = img.get_rect()

		self.rect.x = x_pos
		self.rect.y = y_pos

	def isOver(self):
		mouse_pos = pygame.mouse.get_pos()
		if (mouse_pos[0] > self.rect.x and mouse_pos[0] < self.rect.x + self.img.get_width()):
			if (mouse_pos[1] > self.rect.y and mouse_pos[1] < self.rect.y + self.img.get_height()):
				return True
		return False

	def draw(self, win):
		win.blit(self.img, (self.rect.x, self.rect.y))

class Shop: 
	def __init__(self, item_list):
		self.item_list = item_list

		self.columns = 3
		if (len(item_list) < 3):
			self.columns = len(item_list)

		n_items = len(self.item_list)
		if (n_items % self.columns == 0):
			self.rows = int(n_items / self.columns)
		else: 
			self.rows = int(n_items / self.columns) + 1

		self.buffer = 50

		self.space_between_horizontal = (WIDTH - (self.columns * self.item_list[0].get_frame().get_width())) / (self.columns + 1)
		self.space_between_vertical = ((HEIGHT - self.buffer) - (self.rows * self.item_list[0].get_frame().get_height())) / (self.rows + 1)

	def arrange_shop(self): 
		x_pos = self.space_between_horizontal
		y_pos = self.space_between_vertical + self.buffer

		for item in range(len(self.item_list)):
			self.item_list[item].set_pos(x_pos, y_pos)
			if ((item + 1) % self.columns == 0):
				x_pos = self.space_between_horizontal
				y_pos += self.space_between_vertical + self.item_list[item].get_frame().get_height()
			else:
				x_pos += self.space_between_horizontal + self.item_list[item].get_frame().get_width()

	def open(self, win):
		self.arrange_shop()
		for item in self.item_list:
			item.draw(win)

class Shop_Item(Button):
	def __init__(self, bird, price, unlocked, selected):
		self.bird = bird 
		self.price = price
		self.unlocked = unlocked
		self.selected = selected

		self.frame = FRAME_IMG
		self.rect = FRAME_IMG.get_rect()
		self.selected_frame = SELECTED_FRAME_IMG
		self.frame_price = FRAME_PRICE_IMG
		self.bird_img = pygame.transform.scale(bird.img, (int(self.frame.get_width() / 1.5) , int(self.frame.get_width() / 1.5) - 15))
		self.candy_img = pygame.transform.scale(CANDY_IMG, (50, 50))

		super().__init__(self.rect.x, self.rect.y, FRAME_IMG)

	def set_unlocked(self, is_unlocked):
		self.unlocked = is_unlocked

	def set_selected(self, is_selected):
		self.selected = is_selected

	def buy(self, game_manager): 
		if (game_manager.get_candy() >= self.price):
			game_manager.set_candy(-1 * self.price) 
			self.unlocked = True

	def set_pos(self, new_x, new_y):
		self.rect.x = new_x
		self.rect.y = new_y

	def get_bird(self):
		return self.bird

	def get_frame(self):
		return self.frame

	def draw(self, win):
		win.blit(self.frame, (self.rect.x, self.rect.y))
		if (self.selected):
			win.blit(self.selected_frame, (self.rect.x, self.rect.y))

		bird_x = self.rect.x + (self.frame.get_width() / 2) - (self.bird_img.get_width() / 2)
		if (self.unlocked):
			bird_y = self.rect.y + (self.frame.get_width() / 2) - (self.bird_img.get_width() / 2) + 10
		else:
			bird_y = self.rect.y + 10
		win.blit(self.bird_img, (bird_x, bird_y))
		
		if (not(self.unlocked)):
			win.blit(self.frame_price, (self.rect.x, self.rect.y + self.frame.get_height() - self.frame_price.get_height()))
			win.blit(self.candy_img, (self.rect.x, self.rect.y + self.frame.get_height() + 5 - self.candy_img.get_height()))
			price_text = STATSFONT.render(str(self.price), 0, ORANGE)
			win.blit(price_text, (self.rect.x + self.candy_img.get_width() + 5, self.rect.y + self.frame.get_height() - price_text.get_height()))			

#Misc
game_manager = Game_Manager()
background = Background()
counter = Counter()

#Birds
BIRD_1 = Bird(BIRD_IMG1, TRAIL_CIRCLE_BLACK)
BIRD_2 = Bird(BIRD_IMG2, TRAIL_CIRCLE_BLACK)
BIRD_3 = Bird(BIRD_IMG3, TRAIL_CIRCLE_BLACK)
BIRD_4 = Bird(BIRD_IMG4, TRAIL_CIRCLE_BLACK)
BIRD_5 = Bird(BIRD_IMG5, TRAIL_CIRCLE_BLACK)
BIRD_6 = Bird(BIRD_IMG6, TRAIL_CIRCLE_BLACK) 

#Shop 
bird_1 = Shop_Item(BIRD_1, 0, False, False)
bird_2 = Shop_Item(BIRD_2, 200, False, False)
bird_3 = Shop_Item(BIRD_3, 250, False, False)
bird_4 = Shop_Item(BIRD_4, 450, False, False)
bird_5 = Shop_Item(BIRD_5, 900, False, False)
bird_6 = Shop_Item(BIRD_6, 600, False, False)

birds_arr = [bird_1, bird_2, bird_3, bird_4, 
			bird_5, bird_6] 

shop = Shop(birds_arr)

#Spikes
spike_manager = Spike_Manager()

#Candy
candy_spawner = Candy()

#Buttons 
SHOP_BUTTON = Button((WIDTH / 2) - (SHOP_ICON.get_width() / 2), CENTER + 330, SHOP_ICON)

def update(win):
	if (game_manager.main_screen):
		win.fill(WHITEGREY)

		#TITLE
		dont_touch = TITLE_FONT.render("DON'T TOUCH", 0, GREY)
		win.blit(dont_touch, ((WIDTH / 2) - (dont_touch.get_width() / 2), 65))
		the_spikes = TITLE_FONT.render("THE SPIKES", 0, GREY)
		win.blit(the_spikes, ((WIDTH / 2) - (the_spikes.get_width() / 2), 105))

		#Circle
		win.blit(CIRCLE_IMG, ((WIDTH / 2) - (CIRCLE_IMG.get_width() / 2), CENTER - (CIRCLE_IMG.get_height() / 2)))

		#PRESS [SPACE] TO JUMP
		press_space = STATSFONT_2.render("PRESS [SPACE]", 0 ,RED)
		win.blit(press_space, ((WIDTH / 2) - (press_space.get_width() / 2), CENTER - 85))
		to_jump = STATSFONT_2.render("TO JUMP", 0 ,RED)
		win.blit(to_jump, ((WIDTH / 2) - (to_jump.get_width() / 2), CENTER - 65))

		#Best score
		best_score = STATSFONT.render("BEST SCORE: " + str(game_manager.get_best_score()), 0, GREY)
		win.blit(best_score, ((WIDTH / 2) - (best_score.get_width() / 2), CENTER + 195))			
		
		#Games Played
		games_played = STATSFONT.render("GAMES PLAYED: " + str(game_manager.get_games_played()), 0, GREY)
		win.blit(games_played, ((WIDTH / 2) - (games_played.get_width() / 2), CENTER + 225))
		
		#Candy
		win.blit(CANDY_IMG, ((WIDTH / 2) - CANDY_IMG.get_width(), CENTER + 155))
		candy = STATSFONT.render(str(game_manager.get_candy()), 0, ORANGE)
		win.blit(candy, ((WIDTH / 2), CENTER + 160))

		#Spikes
		SPIKE_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		SPIKE_IMG.fill(B_WHITEGREY[1][0:3] + [0,], None, pygame.BLEND_RGB_ADD)
		
		num_spikes = 8
		space_between = 26

		win.blit(BOTTOM_SPIKES_IMG, (0, HEIGHT - BOTTOM_SPIKES_IMG.get_height()))
		BOTTOM_SPIKES_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		BOTTOM_SPIKES_IMG.fill(B_WHITEGREY[1][0:3] + [0,], None, pygame.BLEND_RGB_ADD)

		for x in range(num_spikes):
			win.blit(pygame.transform.rotate(SPIKE_IMG, 90), (x * (SPIKE_IMG.get_width() + space_between), spike_manager.BOTTOM_SPIKES_Y))

		win.blit(TOP_SPIKES_IMG, (0, 0))
		TOP_SPIKES_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		TOP_SPIKES_IMG.fill(B_WHITEGREY[1][0:3] + [0,], None, pygame.BLEND_RGB_ADD)
		
		for x in range(num_spikes):
			win.blit(pygame.transform.rotate(SPIKE_IMG, -90), (x * (SPIKE_IMG.get_width() + space_between), spike_manager.TOP_SPIKES_Y))

		#Shop button
		SHOP_BUTTON.draw(win)

		#Bird
		game_manager.get_bird().draw(win)

	elif (game_manager.game_started):
		#Background
		background.fade_color()
		color = background.get_current_color()
		win.fill(color)

		#Counter
		win.blit(CIRCLE_IMG, ((WIDTH / 2) - (CIRCLE_IMG.get_width() / 2), CENTER - (CIRCLE_IMG.get_height() / 2)))
		counter.draw(background.get_current_color(), win)

		#Candy
		candy_spawner.draw(win)

		#Bird
		for i in range(len(game_manager.get_bird().get_trail())):
			win.blit(game_manager.get_bird().get_trail()[i], game_manager.get_bird().get_trail_pos()[i])
		game_manager.get_bird().draw(win)

		#Spikes 
		num_spikes = 8
		space_between = 26

		current_color = COLORLIST[background.get_color_index()][1]

		for spike in spike_manager.get_spikes():
			if (spike != None):	
				spike.fade_color()	
				spike.img.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
				spike.img.fill(spike.get_current_color()[0:3] + [0,], None, pygame.BLEND_RGB_ADD)
				current_color = spike.get_current_color()
				spike.draw(win)

		SPIKE_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		SPIKE_IMG.fill(current_color[0:3] + [0,], None, pygame.BLEND_RGB_ADD)

		win.blit(BOTTOM_SPIKES_IMG, (0, HEIGHT - BOTTOM_SPIKES_IMG.get_height()))
		BOTTOM_SPIKES_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		BOTTOM_SPIKES_IMG.fill(current_color[0:3] + [0,], None, pygame.BLEND_RGB_ADD)
		for x in range(num_spikes):
			win.blit(pygame.transform.rotate(SPIKE_IMG, 90), (x * (SPIKE_IMG.get_width() + space_between), spike_manager.BOTTOM_SPIKES_Y))
		
		win.blit(TOP_SPIKES_IMG, (0, 0))
		TOP_SPIKES_IMG.fill((0, 0, 0, 255), None, pygame.BLEND_RGB_MULT)
		TOP_SPIKES_IMG.fill(current_color[0:3], None, pygame.BLEND_RGB_ADD)
		for x in range(num_spikes):
			win.blit(pygame.transform.rotate(SPIKE_IMG, -90), (x * (SPIKE_IMG.get_width() + space_between), spike_manager.TOP_SPIKES_Y))

	elif (game_manager.in_shop):
		win.fill(WHITEGREY)
		shop.open(win)

	pygame.display.update()

def main():
	clock = pygame.time.Clock()
	last_time = time.time()

	game_manager.load_stats(STATS_DF)
	game_manager.load_birds(BIRDS_DF, birds_arr)

	for bird in birds_arr:
		if (bird.selected):
			game_manager.set_bird(bird.get_bird())

	run = True 
	while(run): 
		clock.tick(FPS)

		current_color_level = counter.get_count()

		for event in pygame.event.get():
			if (event.type == pygame.QUIT):
				run = False

			if (event.type == pygame.KEYDOWN):
				if (event.key == pygame.K_SPACE):
					if (game_manager.main_screen or game_manager.game_started):
						if (game_manager.game_started == False):
							game_manager.increase_games_played()
						game_manager.start_game()
						game_manager.get_bird().jump(3)

				if (event.key == pygame.K_m):
					game_manager.go_to_main_screen()

			if (event.type == pygame.MOUSEBUTTONUP):
				if (game_manager.main_screen):
					if (SHOP_BUTTON.isOver()):
						game_manager.open_shop()

				if (game_manager.in_shop):
					for item in birds_arr:
						if (item.isOver()):
							if (not(item.selected) and item.unlocked):
								for i in birds_arr:
									if (i == item):
										i.set_selected(True)
										game_manager.set_bird(item.get_bird())
									else:
										i.set_selected(False)
							if (not(item.unlocked)):
								item.buy(game_manager)

		if (game_manager.game_started):
			game_manager.get_bird().move()
			game_manager.get_bird().update_trail()
			if ((game_manager.get_bird().rect.x + game_manager.get_bird().rect.width > WIDTH) or (game_manager.get_bird().rect.x < 0)):
				game_manager.get_bird().bounce_off_wall()
				spike_manager.reset()
				spike_manager.update_chance_of_spike(counter.get_count())
				spike_manager.generate_spikes(True if game_manager.bird.velocity > 0 else False)
				counter.increase()

			candy_spawner.idle(8)		

			#Check collision 
			for spike in spike_manager.get_spikes():
				if (spike != None):
					if (spike.collide(game_manager.get_bird())):
						game_manager.reset_game(game_manager.get_bird(), spike_manager, counter, background)
						game_manager.go_to_main_screen()

			if (game_manager.get_bird().rect.y > spike_manager.BOTTOM_SPIKES_Y - game_manager.get_bird().img.get_height() + 15):
				game_manager.reset_game(game_manager.get_bird(), spike_manager, counter, background)
				game_manager.go_to_main_screen()

			if (game_manager.get_bird().rect.y < spike_manager.TOP_SPIKES_Y + SPIKE_IMG.get_height() - 30):
				game_manager.reset_game(game_manager.get_bird(), spike_manager, counter, background)
				game_manager.go_to_main_screen()

			if (candy_spawner.collide(game_manager.get_bird())):
				candy_spawner.spawn_candy()
				game_manager.set_candy(1)
		else:
			game_manager.get_bird().idle(15)

		if (current_color_level != counter.get_count()):
			if (counter.get_count() % 5 == 0 and counter.get_count() != 0):
				background.change_color()
				for spike in spike_manager.get_spikes():
					if (spike != None):
						spike.change_color()

		update(WINDOW)
		
		if (counter.get_count() > game_manager.get_best_score()):
			game_manager.set_best_score(counter.get_count()) 

	game_manager.save_stats(STATS_DF)
	game_manager.save_birds(BIRDS_DF, birds_arr)
	BIRDS_DF.to_csv(os.path.join("CSV Files", "Birds.csv"), index=False)
	STATS_DF.to_csv(os.path.join("CSV FIles", "GameStats.csv"), index=False)
	
	pygame.quit()
	quit()
		
main()
