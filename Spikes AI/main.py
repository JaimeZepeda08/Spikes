import pygame 
import neat
import pickle 
import numpy as np 
import random
import math
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

#Fonts
FONT = "RussoOne-Regular.ttf"
SCORE_FONT = pygame.font.Font(os.path.join("Assets", FONT), 125)

#Birds
BIRD_IMG1 = pygame.image.load(os.path.join("Assets", "Bird1.webp"))

#Trails
TRAIL_CIRCLE_BLACK = pygame.image.load(os.path.join("Assets", "trail_circle_black.png"))

#Spikes
TOP_SPIKES_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "SpikeBase.png")), ((WIDTH, 16))) 
BOTTOM_SPIKES_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "SpikeBase.png")), (WIDTH, HEIGHT - (CENTER + 324)))
SPIKE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Spike.png")), (30, 50))

#Misc
CIRCLE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "circle.png")), (280, 280))

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

class Bird: 
	def __init__(self):
		self.img = pygame.transform.scale(BIRD_IMG1, (65, 50))
		self.rect = self.img.get_rect()

		self.rect.x = (WIDTH / 2) - (self.img.get_width() / 2)
		self.rect.y = CENTER - (self.img.get_height() / 2)
	
		self.velocity = 5
		self.tick_count = 0 
		self.jump_force = 0
		self.dy = self.jump_force * self.tick_count + 0.5 * self.tick_count ** 2 

		self.idle_count = 0
		self.initial_y_pos = self.rect.y 

		self.trail_img = pygame.transform.scale(TRAIL_CIRCLE_BLACK, (25, 25))
		self.trail_tick = 0
		self.trail_count = 4
		self.trail = []
		self.trail_pos = []
		self.trail_size = []

	def move(self):
		self.rect.x += self.velocity

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

		self.spikes = [None for i in range(self.max_spikes)]

		self.empty_group = [spike for spike in range(len(self.spikes))]
		self.empty_pos = 0 * SPIKE_IMG.get_height() + SPIKE_IMG.get_height() // 2 + self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 

	def get_spikes(self):
		return self.spikes

	def set_empty(self):
		empty = []
		empty_group = []
		for i in range(len(self.spikes)):
			if self.spikes[i] == None:
				empty_group.append(i)
			if self.spikes[i] != None or i == len(self.spikes) - 1:
				if len(empty_group) > 0:
					empty.append(empty_group)
					empty_group = []

		if len(empty) > 0:
			self.empty_group = empty[(len(empty) - 1) // 2]
			if len(self.empty_group) < 2:
				for group in empty:
					if len(group) > len(self.empty_group):
						self.empty_group = group

			empty = self.empty_group[(len(self.empty_group) - 1) // 2]

			self.empty_pos = empty * SPIKE_IMG.get_height() + SPIKE_IMG.get_height() // 2 + self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 

	def get_distance_to_spikes(self, bird):
		x = bird.rect.x 
		y = bird.rect.y 

		spike_1_pos = self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 
		spike_2_pos = len(self.spikes) * SPIKE_IMG.get_height() + self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 

		if self.empty_group[0] != 0: 
			spike_1_pos = (self.empty_group[0] - 1) * SPIKE_IMG.get_height() + SPIKE_IMG.get_height() // 2 + self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 
		if self.empty_group[-1] != len(self.spikes) - 1:	
			spike_2_pos = (self.empty_group[-1] + 1) * SPIKE_IMG.get_height() + SPIKE_IMG.get_height() // 2 + self.TOP_SPIKES_Y + SPIKE_IMG.get_height() 

		if bird.velocity > 0:
			distance_1 = math.dist([WIDTH - SPIKE_IMG.get_width(), spike_1_pos], [x, y])
			distance_2 = math.dist([WIDTH - SPIKE_IMG.get_width(), spike_2_pos], [x, y])
			return distance_1, distance_2
		else:
			distance_1 = math.dist([x, y], [SPIKE_IMG.get_width(), spike_1_pos])
			distance_2 = math.dist([x, y], [SPIKE_IMG.get_width(), spike_2_pos])
			return distance_1, distance_2

	def generate_spikes(self, right):
		self.spikes = []
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
		self.chance_of_spike = 3

	def draw(self, win):
		for spike in self.spikes:
			if (spike != None):
				spike.draw(win)

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
		score_text = SCORE_FONT.render(str(score), 0, color)
		win.blit(score_text, ((WIDTH / 2) - (score_text.get_width() / 2), CENTER - (score_text.get_height() / 2)))

def update(win, birds, spike_manager, background, counter, show_target):
	background.fade_color()
	color = background.get_current_color()
	win.fill(color)

	win.blit(CIRCLE_IMG, ((WIDTH / 2) - (CIRCLE_IMG.get_width() / 2), CENTER - (CIRCLE_IMG.get_height() / 2)))
	if (counter):
		counter.draw(background.get_current_color(), win)

	for bird in birds:
		for i in range(len(bird.get_trail())):
			win.blit(bird.get_trail()[i], bird.get_trail_pos()[i])
		bird.draw(win)

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

	if (show_target):
		x = 0
		for spike in spike_manager.spikes:
			if spike != None:
				x = spike.rect.x
		pygame.draw.rect(win, (255, 255, 50), (x + 5, spike_manager.empty_pos, 20, 20), border_radius=20)

	pygame.display.update()

background = Background()

def eval_genomes(genomes, config):
	clock = pygame.time.Clock()
	last_time = time.time()

	nets = []
	genome_lst = []
	birds = []

	for x, genome in genomes: 
		nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
		birds.append(Bird())
		genome.fitness = 0
		genome_lst.append(genome)

	counter = Counter()
	spike_manager = Spike_Manager()

	run = True 
	while run: 
		clock.tick(FPS)

		current_color_level = counter.get_count()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False 
				pygame.quit()
				quit()

		if len(birds) <= 0:
			background.reset()
			run = False 
			break

		b = None
		for bird in birds:
			if bird:
				b = bird
				break

		if (b.rect.x + b.rect.width > WIDTH) or (b.rect.x < 0):
			spike_manager.reset()
			spike_manager.update_chance_of_spike(counter.get_count())
			spike_manager.generate_spikes(True if b.velocity > 0 else False)
			spike_manager.set_empty()
			counter.increase()

		for i, bird in enumerate(birds):
			bird.move()
			bird.update_trail()

			if (bird.rect.x + bird.rect.width > WIDTH) or (bird.rect.x < 0):
				bird.bounce_off_wall()
				#genome_lst[i].fitness += 0.2

			'''
			if bird.rect.y + BIRD_IMG1.get_height() // 2 > spike_manager.empty_pos - 10 and bird.rect.y + BIRD_IMG1.get_height() // 2 < spike_manager.empty_pos + 10:
				genome_lst[i].fitness += 8
			elif bird.rect.y + BIRD_IMG1.get_height() // 2 > spike_manager.empty_pos - 30 and bird.rect.y + BIRD_IMG1.get_height() // 2 < spike_manager.empty_pos + 30:
				genome_lst[i].fitness += 5
			else:
				genome_lst[i].fitness -= 0.005
			'''

			spike_x = 0
			for spike in spike_manager.spikes:
				if spike != None:
					spike_x = spike.rect.x

			if bird.rect.y + BIRD_IMG1.get_height() // 2 > spike_manager.empty_pos - 3 and bird.rect.y + BIRD_IMG1.get_height() // 2 < spike_manager.empty_pos + 3:
				if bird.velocity > 0 :
					if bird.rect.x + BIRD_IMG1.get_width() >= spike_x + 5:
						genome_lst[i].fitness += 10
				else:
					if bird.rect.x <= spike_x + 5:
						genome_lst[i].fitness += 10

			for spike in spike_manager.get_spikes():
				if spike != None:
					if spike.collide(bird):
						if i < len(genome_lst):
							genome_lst[i].fitness -= 2
							birds.pop(i)
							genome_lst.pop(i)
							nets.pop(i)

			if bird.rect.y > spike_manager.BOTTOM_SPIKES_Y - bird.img.get_height() + 15:
				if i < len(genome_lst):
					genome_lst[i].fitness -= 2
					birds.pop(i)
					genome_lst.pop(i)
					nets.pop(i)

			if bird.rect.y < spike_manager.TOP_SPIKES_Y + SPIKE_IMG.get_height() - 30:
				if i < len(genome_lst):
					genome_lst[i].fitness -= 2
					birds.pop(i)
					genome_lst.pop(i)
					nets.pop(i)

		if time.time() - last_time >= 0.08:
			for i, bird in enumerate(birds):
				inputs = [bird.rect.y, bird.dy, spike_manager.empty_pos, spike_manager.get_distance_to_spikes(bird)[0], spike_manager.get_distance_to_spikes(bird)[1]]
				outputs = nets[i].activate(inputs)
				if outputs[0] > outputs[1]:
					bird.jump(3) 

			last_time = time.time()

		if current_color_level != counter.get_count():
			if counter.get_count() % 5 == 0 and counter.get_count() != 0:
				background.change_color()
				for spike in spike_manager.get_spikes():
					if spike != None:
						spike.change_color()

		update(WINDOW, birds, spike_manager, background, counter, True)

def play_AI(genome, config):
	clock = pygame.time.Clock()
	last_time = time.time()

	counter = Counter()
	spike_manager = Spike_Manager()

	bird = Bird()
	net = neat.nn.FeedForwardNetwork.create(genome, config)

	run = True 
	while run: 
		clock.tick(FPS)

		current_color_level = counter.get_count()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False 
				pygame.quit()
				quit()

		bird.move()
		bird.update_trail()

		if (bird.rect.x + bird.rect.width > WIDTH) or (bird.rect.x < 0):
			bird.bounce_off_wall()
			spike_manager.reset()
			spike_manager.update_chance_of_spike(counter.get_count())
			spike_manager.generate_spikes(True if bird.velocity > 0 else False)
			spike_manager.set_empty()
			counter.increase()

		for spike in spike_manager.get_spikes():
			if spike != None:
				if spike.collide(bird):
					background.reset()
					main()

		if bird.rect.y > spike_manager.BOTTOM_SPIKES_Y - bird.img.get_height() + 15:
			background.reset()
			main()

		if bird.rect.y < spike_manager.TOP_SPIKES_Y + SPIKE_IMG.get_height() - 30:
			background.reset()
			main()

		if time.time() - last_time >= 0.08:
			inputs = [bird.rect.y, bird.dy, spike_manager.empty_pos, spike_manager.get_distance_to_spikes(bird)[0], spike_manager.get_distance_to_spikes(bird)[1]]
			outputs = net.activate(inputs)
			if outputs[0] > outputs[1]:
				bird.jump(3) 

			last_time = time.time()

		if current_color_level != counter.get_count():
			if counter.get_count() % 5 == 0 and counter.get_count() != 0:
				background.change_color()
				for spike in spike_manager.get_spikes():
					if spike != None:
						spike.change_color()

		update(WINDOW, [bird], spike_manager, background, counter, False)


def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(eval_genomes, 200)
	with open("AI_2.pkl", "wb") as file:
		pickle.dump(winner, file)
		file.close()

def load_genome(config_path, genome_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	with open(genome_path, "rb") as file:
		genome = pickle.load(file)

	play_AI(genome, config)

def main():
	clock = pygame.time.Clock()

	spike_manager = Spike_Manager()
	bird = Bird()

	main_menu = True
	while main_menu: 
		clock.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				main_menu = False  
				pygame.quit()
				quit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					local_dir = os.path.dirname(__file__)
					config_path = os.path.join(local_dir, "config_file.txt")
					run(config_path)

				if event.key == pygame.K_a:
					load_genome("config_file.txt", "AI.pkl")

		bird.idle(15)

		update(WINDOW, [bird], spike_manager, background, None, False)

if __name__ == "__main__":
	main()