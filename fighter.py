## Fighter Game, created by Uxbal 
## davidia@hotmail.com
## "Truth is singular; its versions are mistruths"

import pygame, sys, random, time, os
import badguy
from pygame.locals import *

# Setting the constants
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'assets')
FPS = 900
WINDOWHEIGHT = 300
WINDOWWIDTH = 500
BULLETSPEED = 8
BULLETWIDTH = 5
BULLETLENGTH = 10
ENEMYSPEED = 1
STARTINGAMOUNT = 10 # starting amount of bad guys
BUBASPEED = 20
TOPMARGIN = 5
LEFTMARGIN = 5
LIFEWIDTH = 100
UPLIMIT = int(WINDOWHEIGHT - (WINDOWHEIGHT - (0.2 * WINDOWHEIGHT)))
DOWNLIMIT = int(WINDOWHEIGHT - UPLIMIT)

# Colours        R   G     B
BlACK =       (  0,   0,   0)
WHITE =       (225, 225, 225)
ORANGE =      (225,  87,  51)
LIGHTBLUE =   ( 93, 173, 226)
GREEN =       ( 46, 204, 113)
GREY =        ( 97, 106, 107) 
DARKBLUE =    ( 33,  47,  61)
RED =         (255,   0,   0)


BGCOLOUR = GREY 
BUBA = 'buba'
BADGUY = 'bad guy'
LEFT = 'left'
RIGHT = 'right'
INJURY = 'injury'
VICTORY = 'victory'

# Paths to varies resources used in the game. Fonts, images, etc.
BUBA_PATH = os.path.join(RESOURCES_PATH, 'buba.png')
ENEMY_PATH = os.path.join(RESOURCES_PATH, 'bad_guy.png')
FONT_PATH = os.path.join(RESOURCES_PATH, 'Exo-Light.otf')

# Setup Buba and enemy image.
ENEMYIMG = pygame.image.load(ENEMY_PATH)
BUBA = pygame.image.load(BUBA_PATH)

# A tuple of every valid Y-coordinate an enemy can appear on. 
POSSIBLE_ENEMY_Y = tuple([y for y in range(UPLIMIT, DOWNLIMIT, BUBASPEED)])

def main():
	# I feel weird having this many global variables. Don't know any other way 
	# I can do it. :(
	global FPSCLOCK, DISPLAYSURF, BASICFONT, LEVELSURF, LEVELRECT, BUBA, bubax,bubay, life, score
	global SCORESURF, SCORERECT

	assert (DOWNLIMIT > 160), "screen is too small"

	pygame.init()
	FPSCLOCK = pygame. time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('Buba')
	BASICFONT = pygame.font.Font(FONT_PATH, 12)

	DISPLAYSURF.fill(BGCOLOUR)

	# useful variables.
	level = 1
	life = 100
	score = 0
	bubax = LEFTMARGIN
	bubay = WINDOWHEIGHT / 2
		
	enemyList = [] # List to hold all bad guys on board (enemy)
	firstAttempt = True # Flag for when its player's first attempt
	
	
	# Main game loop
	while True:
		bubaRect = BUBA.get_rect()
		bubaHeight = bubaRect.bottom - bubaRect.top

		# Check is Buba's life is 0
		life = checkEnemyHit(bubaHeight, enemyList)
		if life <= 0:
			# If your life is finished, display hasLost text and reset everything.
			hasLost()
			pygame.display.update()
			pygame.time.wait(3000)
			life = 100
			score = 0
			level = 0
			enemyList = []
			starting = True

		# Life rect to display Buba's remaining life.
		lifeRect = pygame.Rect(LEFTMARGIN, TOPMARGIN, life, 10)
		beneathLifeRect = pygame.Rect(LEFTMARGIN, TOPMARGIN, LIFEWIDTH, 10)

		# Text surf to show current level.
		LEVELSURF = BASICFONT.render("LEVEL: " + str(level),1, GREEN)
		LEVELRECT = LEVELSURF.get_rect()
		LEVELRECT.topleft = (LEFTMARGIN + LIFEWIDTH * 3, TOPMARGIN)

		# Text to display score
		SCORESURF = BASICFONT.render("Score: " + str(score), 1, RED)
		SCORERECT = SCORESURF.get_rect()
		SCORERECT.topleft = (LEFTMARGIN + LIFEWIDTH * 1.5, TOPMARGIN)
		
		
		
		DISPLAYSURF.fill(BGCOLOUR)
		pygame.draw.rect(DISPLAYSURF, BlACK, beneathLifeRect)
		pygame.draw.rect(DISPLAYSURF, GREEN, lifeRect)

		
		
		# Check if the game is just starting (First attempt)
		if firstAttempt:
			enemyList = createRandomEnemies(STARTINGAMOUNT, ENEMYSPEED, enemyList)			
		else:
			# Check if all enemies are dead. If True, increment level and
			# Create more enemies. 
			if len(enemyList) == 0: 
				level += 1			
				enemyList = createRandomEnemies(STARTINGAMOUNT * (level), ENEMYSPEED + level, enemyList)
			else:
				# there are still bad guys
				# Animate the bad guys
				for enemy in enemyList:
					enemyAnimation(enemy, ENEMYSPEED)


		checkForQuit()
		# main event handling loop
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_UP and bubay > UPLIMIT:
					bubay -= BUBASPEED
				if event.key == K_DOWN and bubay < DOWNLIMIT:					
					bubay += BUBASPEED
				if event.key == K_SPACE:
					shoot(bubaHeight, RIGHT, bubax, bubay, enemyList)
					shot = True

		firstAttempt = False # During the first loop, flag set to False

		DISPLAYSURF.blit(LEVELSURF, LEVELRECT)
		DISPLAYSURF.blit(BUBA, (bubax, bubay))
		DISPLAYSURF.blit(SCORESURF, SCORERECT)
		pygame.display.update()
		FPSCLOCK.tick(FPS)

def terminate():
	pygame.quit()
	sys.exit()

def checkForQuit():
	for event in pygame.event.get(QUIT):
		terminate()
	for event in pygame.event.get(KEYUP):
		if event.key == K_ESCAPE:
			terminate()
		pygame.event.post(event)


def enemyAnimation(enemy, speed):
	# Enemy animation makes your enemies move across the screen at speed.
	enemy.x -= speed
	DISPLAYSURF.blit(LEVELSURF, LEVELRECT)
	DISPLAYSURF.blit(BUBA, (bubax, bubay))
	DISPLAYSURF.blit(enemy.image, (enemy.x, enemy.y))
	DISPLAYSURF.blit(SCORESURF, SCORERECT)


def shootAnimation(x, y, adjx=0, adjy=0):
	# Animate bullet going across board.
	pygame.draw.rect(DISPLAYSURF, RED, (x + adjx, y + adjy, BULLETLENGTH, BULLETWIDTH))
	DISPLAYSURF.blit(LEVELSURF, LEVELRECT)
	DISPLAYSURF.blit(BUBA, (bubax, bubay))
	DISPLAYSURF.blit(SCORESURF, SCORERECT)


def checkHit(bulletx, bullety, charHeight, enemyList):
	# checks if a Buba's bullet hit an enemy
	# if yes, remove the enemy from the list and increment Buba's score. 
	global score
	hit = False
	for enemy in enemyList:
		enemyRect = pygame.Rect(enemy.x, enemy.y, 30, 32)
		if enemyRect.collidepoint(bulletx, bullety):
			enemyList.remove(enemy)
			score += 1
			hit = True
			break
	return hit

def checkEnemyHit(charHeight, enemyList):
	# Checks if an Enemy reached the end of the window
	# Or if the enemy collided with Buba
	global life
	if enemyList:
		bubaRect = pygame.Rect(bubax, bubay, charHeight, charHeight) # So we know where Buba is.
		for enemy in enemyList:		
			if enemy.x == 0: # 32 is a Magick number. FInd a way to change this. 
				life = 0
				break			
			elif bubaRect.collidepoint(enemy.x, enemy.y):
				life -= 20	
				break			
			else:
				life = life
			
	else:
		life = life

	return life


def shoot(charHeight, direction, shooterx, shootery, enemyList):
	# 'shoot' should generate a bullet from the middle of the shooter.
	# Bullet should then travel horizontally across board until it reaches WINDOWWIDTH
	baseSurf = DISPLAYSURF.copy()

	# Get half of character height
	half = int(charHeight / 2)
	
	for i in range(shooterx, WINDOWWIDTH + BULLETSPEED, BULLETSPEED):
		DISPLAYSURF.blit(baseSurf, (0, 0))
		if direction == RIGHT:
			shootAnimation(shooterx, shootery , i, half )
			if checkHit(shooterx + i, shootery + half, charHeight, enemyList):
				break
		elif direction == LEFT:
			shootAnimation(shooterx, shootery, -i, half )
		
		pygame.display.update()
		FPSCLOCK.tick(FPS)


def createRandomEnemies(amount, speed, enemyList):
	# creates 'amount' number of enemies on random (x, y) positions.
	# x must be greater than WINDOWWIDTH, to allow for them to gradually appear on screen.
	# y must be within all possible enemy y-positions, stored in POSSIBLE_ENEMY_Y
	# I created a class called BadGuy in a module called badguy, since every enemy 
	# will have similar properties. 
	# Each instance of BadGuy classs has (x, y) coords, speed, and an image
	for i in range(amount):
		y = random.choice(POSSIBLE_ENEMY_Y)
		x = random.randint(WINDOWWIDTH, WINDOWWIDTH + 300)
		enemy = badguy.BadGuy(x, y, speed, ENEMYIMG)
		enemyList.append(enemy)
	return enemyList

def hasLost():
	# When the game is lost.
	loserSurf = BASICFONT.render('You are such a loser, smh', True, RED, WHITE)
	loserRect = loserSurf.get_rect()
	loserRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

	DISPLAYSURF.blit(loserSurf, loserRect)





if __name__ == '__main__':
	main()