import pygame
import os
import random
import csv
import button

pygame.init()

screen_width = 500
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("The Traveller's Mission")

#framerate
clock = pygame.time.Clock()
FPS = 60

start_game = False

#world
G = 0.75
rows = 16
columns = 150
tile_size = screen_height // rows
tile_types = 20
level = 1

#scrolling
scroll_thresh = 125
cam_scroll = 0
#bg_scroll = 0

#player actions
moving_left = False
moving_right = False
shoot = False

#images
#title screen
landscape_img = pygame.image.load('assets/img/background/TitleScreenBG.jpg').convert_alpha()
landscape_img = pygame.transform.scale(landscape_img, (int(landscape_img.get_width() * 0.28), int(landscape_img.get_height() * 0.28)))
#rect = landscape_img.get_rect()
#rect.center = (x, y)
#buttons
start_img = pygame.image.load('assets/img/start_btn.png').convert_alpha()
quit_img = pygame.image.load('assets/img/exit_btn.png').convert_alpha()
#background
sky_img = pygame.image.load('assets/img/background/sky.png').convert_alpha()
sky_img = pygame.transform.scale(sky_img, (int(sky_img.get_width() * 0.625), int(sky_img.get_height() * 0.625)))
mountains_img = pygame.image.load('assets/img/background/mountains.png').convert_alpha()
mountains_img = pygame.transform.scale(mountains_img, (int(mountains_img.get_width() * 0.625), int(mountains_img.get_height() * 0.625)))
trees1_img = pygame.image.load('assets/img/background/trees1.png').convert_alpha()
trees1_img = pygame.transform.scale(trees1_img, (int(trees1_img.get_width() * 0.625), int(trees1_img.get_height() * 0.625)))
trees2_img = pygame.image.load('assets/img/background/trees2.png').convert_alpha()
trees2_img = pygame.transform.scale(trees2_img, (int(trees2_img.get_width() * 0.625), int(trees2_img.get_height() * 0.625)))
#tiles
tiles = []
for x in range(tile_types):
	img = pygame.image.load(f'assets/img/tile/{x}.png')
	img = pygame.transform.scale(img, (tile_size, tile_size))
	tiles.append(img)
#bullet
bullet_img = pygame.image.load('assets/img/icons/IonBullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (int(bullet_img.get_width() * 2), int(bullet_img.get_height() * 2)))
#pick-ups
reload_img = pygame.image.load('assets/img/icons/ReloadBox.png').convert_alpha()
reload_img = pygame.transform.scale(reload_img, (int(reload_img.get_width() * 2/3), int(reload_img.get_height() * 2/3)))
key_img = pygame.image.load('assets/img/icons/Key.png').convert_alpha()
key_img = pygame.transform.scale(key_img, (int(key_img.get_width() * 2/3), int(key_img.get_height() * 2/3)))
items = {
	'Reload'	: reload_img,
	'Key'			: key_img
}
#icons
h_img = pygame.image.load('assets/img/icons/Health.png').convert_alpha()
r_img = pygame.image.load('assets/img/icons/Reload.png').convert_alpha()
a_img = pygame.image.load('assets/img/icons/Ammo.png').convert_alpha()
health = pygame.image.load('assets/img/icons/PlusHealth.png').convert_alpha()
#heart = pygame.transform.scale(heart, (int(heart.get_width() * 1.5), int(heart.get_height() * 1.5)))
shield = pygame.image.load('assets/img/icons/PlusShield.png').convert_alpha()
#shield = pygame.transform.scale(shield, (int(shield.get_width() * 1.5), int(shield.get_height() * 1.5)))
#exit
exit_img = pygame.image.load('assets/img/tile/19.png').convert_alpha()

#colours
BG = (28, 35, 51)
grey = (192, 192, 192)
white = (255, 255, 255)
blue = (0, 176, 240)
red = (255, 0, 0)
green = (146, 208, 80)
transparent_black = (0, 0, 0)
#transparent_black.set_alpha(50)

#fonts
font = pygame.font.Font('BAHNSCHRIFT.TTF', 20)
title_font = pygame.font.Font('BAHNSCHRIFT.TTF', 50)
sub_font = pygame.font.Font('BAHNSCHRIFT.TTF', 30)

#buttons
start_button = button.Button(30, screen_height - 130, start_img, 0.4)
quit_button = button.Button(30, screen_height - 70, quit_img, 0.4)


def title_screen():
	screen.blit(landscape_img, (-100, 0))
	draw_text("The Traveller's", title_font, grey, screen_width // 6, 50)
	draw_text('Mission', sub_font, grey, screen_width // 3 + 30, 100)
	#draw buttons
	global start_game
	if start_button.draw(screen):
		start_game = True
	if quit_button.draw(screen):
		pygame.quit()

def draw_bg():
	#screen.fill(BG)
	#pygame.draw.line(screen, grey, (35, 9), (35, 113))
	screen.blit(sky_img, (0, 0))
	screen.blit(mountains_img, (0, screen_height - mountains_img.get_height() - 187.5))
	screen.blit(trees1_img, (0, screen_height - trees1_img.get_height() - 93.75))
	screen.blit(trees2_img, (0, screen_height - trees2_img.get_height()))
	#pygame.draw.rect(screen, transparent_black, (0, 0, 104, 14))

def draw_text(text, font, colour, x, y):
	img = font.render(text, True, colour)
	screen.blit(img, (x, y))


class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.shield = 100
		self.max_shield = self.shield
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animations = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#player specific variables
		self.healups = 3
		self.reloads = 3
		self.max_reloads = 10
		self.keys = 0
		#ai specific variables
		self.move_counter = 0
		self.idle = False
		self.idle_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		#load all images for player
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			#reset temporary image list
			temp_list = []
			#count number of files in folder
			num_frames = len(os.listdir(f'assets/img/{self.char_type}/{animation}'))
			for i in range(num_frames):
				img = pygame.image.load(f'assets/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animations.append(temp_list)
		self.image = self.animations[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.update_animation()
		self.check_alive()
		#update shooting cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
	
	def move(self, moving_left, moving_right):
    #reset movement variables
		global cam_scroll
		dx = 0
		dy = 0
    #assign movement variables for left and right
		if moving_left:
			dx = -self.speed
			self.direction = -1
			self.flip = True
		if moving_right:
			dx = self.speed
			self.direction = 1
			self.flip = False
		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -10
			self.jump = False
			self.in_air = True
		#apply gravity
		self.vel_y += G
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y
		#check collision with obstacles
		for tile in world.obstacles:
			#x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				if self.in_air == False:
					self.update_action(0) #0: idle
			#y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if jumping below ground above
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if falling above ground below
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom
		#check water collision
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0
    #update rectangle position
		self.rect.x += dx
		self.rect.y += dy
		#update camera scroll with player position
		if self.char_type == 'player':
			if self.rect.right > screen_width - scroll_thresh or self.rect.left < screen_width:
				self.rect.x -= dx
				cam_scroll = -dx
		return cam_scroll

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#decrement ammo
			self.ammo -= 1

	def ai(self):
		if self.alive and player.alive:
			if self.idle == False and random.randint(1, 200) == 1:
				self.update_action(0) #0: idle
				self.idle = True
				self.idle_counter = 50
			#check if player is in enemy vision
			if self.vision.colliderect(player.rect):
				#stop running and face player
				self.update_action(0) #0: idle
				self.shoot()
			else:
				if self.idle == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1) #1: run
					self.move_counter += 1
					#update vision rectangle as enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					if self.move_counter > tile_size:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idle_counter -= 1
					if self.idle_counter <= 0:
						self.idle = False
		elif self.alive and player.alive == False:
			self.update_action(0) #0: idle
		#scroll
		self.rect.x += cam_scroll

	def update_animation(self):
		#update animation
		animation_cooldown = 100
		#update image for current frame
		self.image = self.animations[self.action][self.frame_index]
		#check if enough time passed since last update
		if pygame.time.get_ticks() - self.update_time > animation_cooldown:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#reset animation if cycle complete
		if self.frame_index >= len(self.animations[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animations[self.action]) - 1
			else:
				self.frame_index = 0

	def update_action(self, new_action):
		#check if new action is different to previous
		if new_action != self.action:
			self.action = new_action
			#update animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3) #3: death

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacles = []

	def process_data(self, data):
		#iterate through level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = tiles[tile]
					img_rect = img.get_rect()
					img_rect.x = x * tile_size
					img_rect.y = y * tile_size
					tile_data = (img, img_rect)
					if tile in range(9):
						self.obstacles.append(tile_data)
					elif tile in range(9, 11):
						#water
						water = Water(img, x * tile_size, y * tile_size)
						water_group.add(water)
					elif tile in range(11, 15):
						#decoration
						decoration = Decoration(img, x * tile_size, y * tile_size)
						decoration_group.add(decoration)
					elif tile == 15:
						#player
						player = Soldier('player', x * tile_size, y * tile_size, 1.5, 3, 10)
						health_bar = HealthBar(40, 10, player.health, player.health)
						shield_bar = ShieldBar(40, 10, player.shield, player.shield)
					elif tile == 16:
						#enemy
						enemy = Soldier('enemy', x * tile_size, y * tile_size, 1.5, 2, 20)
						enemy_group.add(enemy)
					elif tile == 17:
						#reload box
						item = Item('Reload', x * tile_size, y * tile_size)
						item_group.add(item)
					elif tile == 18:
						#key
						item = Item('Key', x * tile_size, y * tile_size)
						item_group.add(item)
					elif tile == 19:
						#exit
						exit = Exit(exit_img, x * tile_size, y * tile_size)
						exit_group.add(exit)
		return player, health_bar, shield_bar

	def draw(self):
		for tile in self.obstacles:
			#scroll
			tile[1][0] += cam_scroll
			screen.blit(tile[0], tile[1])


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += cam_scroll

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += cam_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += cam_scroll

class Item(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = items[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += cam_scroll
		#check for collision with player
		if pygame.sprite.collide_rect(self, player):
			#check item type
			if self.item_type == 'Reload' and player.reloads < player.max_reloads:
				player.reloads += 1
				#delete item
				self.kill()
			elif self.item_type == 'Key':
				player.keys += 1
				self.kill()
				print(player.keys)


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health factor
		factor = self.health / self.max_health
		#draw health bar
		pygame.draw.rect(screen, grey, (self.x, self.y, 104, 14))
		pygame.draw.rect(screen, BG, (self.x + 1, self.y + 1, 102, 12))
		pygame.draw.rect(screen, white, (self.x + 2, self.y + 2, 100 * factor, 10))
		#pygame.draw.rect(screen, grey, (self.x + 25, self.y, 3, 13))
		#pygame.draw.rect(screen, grey, (self.x + 51, self.y, 3, 13))
		#pygame.draw.rect(screen, grey, (self.x + 77, self.y, 3, 13))
		pygame.draw.line(screen, BG, (self.x + 25, self.y + 1), (self.x + 25, self.y + 11))
		pygame.draw.line(screen, BG, (self.x + 51, self.y + 1), (self.x + 51, self.y + 11))
		pygame.draw.line(screen, BG, (self.x + 77, self.y + 1), (self.x + 77, self.y + 11))


class ShieldBar():
	def __init__(self, x, y, shield, max_shield):
		self.x = x
		self.y = y
		self.shield = shield
		self.max_shield = max_shield

	def draw(self, shield):
		#update with new shield
		self.shield = shield
		#calculate shield factor
		factor = self.shield / self.max_shield
		#draw shield bar
		pygame.draw.rect(screen, grey, (self.x, self.y, 104, 14))
		pygame.draw.rect(screen, BG, (self.x + 1, self.y + 1, 102, 12))
		pygame.draw.rect(screen, white, (self.x + 2, self.y + 2, 100, 10))
		pygame.draw.rect(screen, blue, (self.x + 2, self.y + 2, 100 * factor, 10))
		#pygame.draw.rect(screen, grey, (self.x + 25, self.y, 3, 13))
		#pygame.draw.rect(screen, grey, (self.x + 51, self.y, 3, 13))
		#pygame.draw.rect(screen, grey, (self.x + 77, self.y, 3, 13))
		pygame.draw.line(screen, BG, (self.x + 25, self.y + 1), (self.x + 25, self.y + 11))
		pygame.draw.line(screen, BG, (self.x + 51, self.y + 1), (self.x + 51, self.y + 11))
		pygame.draw.line(screen, BG, (self.x + 77, self.y + 1), (self.x + 77, self.y + 11))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 8
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet and scroll
		self.rect.x += (self.direction * self.speed) + cam_scroll
		#check if bullet is off screen
		if self.rect.right < 0 or self.rect.left > screen_width:
			self.kill()
		#check for collision with world
		for tile in world.obstacles:
			if tile[1].colliderect(self.rect):
				self.kill()
		#check for collision with character
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive and player.shield > 0:
				player.shield -= 20
				self.kill()
			else:
				player.health -= 10
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()


#sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#empty tile list
world_data = []
for row in range(rows):
	r = [-1] * columns
	world_data.append(r)
#load level data and create world
with open(f'level{level}_data.csv', newline = '') as csv_file:
	reader = csv.reader(csv_file, delimiter = ',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar, shield_bar = world.process_data(world_data)


while True:
	
	clock.tick(FPS)

	if start_game == False:
		#display title screen
		title_screen()

	else:
		#update background
		draw_bg()
		#draw world map
		world.draw()
		
		#show health or shield
		if player.shield > 0:
			screen.blit(shield, (12, 11))
			shield_bar.draw(player.shield)
			if player.shield <= 0:
				shield_bar.kill()
		else:
			screen.blit(health, (12, 11))
			health_bar.draw(player.health)
		#show heal-ups
		screen.blit(h_img, (10, 35))
		draw_text(f'x {player.healups}', font, grey, 40, 35)
		#show reloads
		screen.blit(r_img, (10, 65))
		draw_text(f'x {player.reloads}', font, grey, 40, 65)
		#show ammo
		screen.blit(a_img, (10, 95))
		draw_text(f'x {player.ammo}', font, grey, 40, 95)
	
		player.update()
		player.draw()
	
		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()
	
		#update and draw groups
		bullet_group.update()
		item_group.update()
		water_group.update()
		decoration_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		item_group.draw(screen)
		water_group.draw(screen)
		decoration_group.draw(screen)
		exit_group.draw(screen)
	
		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.shoot()
			if player.in_air:
				player.update_action(2) #2: jump
			elif moving_left or moving_right:
				player.update_action(1) #1: run
			else:
				player.update_action(0) #0: idle
			cam_scroll = player.move(moving_left, moving_right)
		else:
			cam_scroll = 0
			start_game = False
		
	for event in pygame.event.get():
    #quit game
		if event.type == pygame.QUIT:
			pygame.quit()
    #keyboard press
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_f and player.healups > 0 and player.health < 100:
				player.health = 100
				player.healups -= 1
			if event.key == pygame.K_r and player.ammo == 0 and player.reloads > 0:
				player.ammo = 10
				player.reloads -= 1
			if event.key == pygame.K_w and player.alive:
				player.jump = True
    #keyboard release
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
	
	pygame.display.update()