import pygame, random
import numpy as np

WINDOW = 750
TILE_SIZE = 50
RANGE = (TILE_SIZE // 2, WINDOW - TILE_SIZE // 2, TILE_SIZE)

getRandomPosition = lambda: [random.randrange(*RANGE), random.randrange(*RANGE)]

snake = pygame.rect.Rect([0, 0, TILE_SIZE - 2, TILE_SIZE - 2])
snake.center = getRandomPosition()

length = 1
segments = [snake.copy()]

snakeDirection = (0, 0)

time = 0
timeStep = 110

food = snake.copy()
food.center = getRandomPosition()

screen = pygame.display.set_mode([WINDOW] * 2)
pygame.display.set_caption('AI Plays Snake (Score: 0, Max Score: 0)')

clock = pygame.time.Clock()

score, maxScore = 0, 0

qTable = np.zeros((8, 16, 4))

directions = [(0, -TILE_SIZE), (0, TILE_SIZE), (-TILE_SIZE, 0), (TILE_SIZE, 0)]

epsilon = 1
epsilonDecay = 0.00005

def chooseAction(state, qTable):
	appleDirection, dangerDirection = state
	if np.random.uniform(0, 1) < epsilon:
		return random.choice(directions)
	else:
		return directions[np.argmax(qTable[appleDirection, dangerDirection])]

def getState(snake, food, segments):
	dx = food.x - snake.x
	dy = food.y - snake.y

	if dx == 0 and dy < 0:
		appleDirection = 0  # Up
	elif dx > 0 and dy < 0:
		appleDirection = 1  # Up-Right
	elif dx > 0 and dy == 0:
		appleDirection = 2  # Right
	elif dx > 0 and dy > 0:
		appleDirection = 3  # Down-Right
	elif dx == 0 and dy > 0:
		appleDirection = 4  # Down
	elif dx < 0 and dy > 0:
		appleDirection = 5  # Down-Left
	elif dx < 0 and dy == 0:
		appleDirection = 6  # Left
	else:
		appleDirection = 7  # Up-Left

	dangerDirection = 0

	danger = [
		snake.move(0, -TILE_SIZE),  # Up
		snake.move(0, TILE_SIZE),   # Down
		snake.move(-TILE_SIZE, 0),  # Left
		snake.move(TILE_SIZE, 0),   # Right
	]

	dangerCheck = [
		danger[0].top < 0 or danger[0].collidelist(segments[:-1]) != -1,
		danger[1].bottom > WINDOW or danger[1].collidelist(segments[:-1]) != -1,
		danger[2].left < 0 or danger[2].collidelist(segments[:-1]) != -1,
		danger[3].right > WINDOW or danger[3].collidelist(segments[:-1]) != -1,
	]

	dangerDirection = dangerCheck[0] * 1 + dangerCheck[1] * 2 + dangerCheck[2] * 4 + dangerCheck[3] * 8;

	return appleDirection, dangerDirection

learningRate = 0.1
discountFactor = 0.9

def updateQTable(qTable, state, action, reward, newState):
	appleDirection, dangerDirection = state
	actionIndex = directions.index(action)
	newAppleDirection, newDangerDirection = newState

	oldQValue = qTable[appleDirection, dangerDirection, actionIndex]
	maxNewQValue = np.max(qTable[newAppleDirection, newDangerDirection])

	newQValue = (1 - learningRate) * oldQValue + learningRate * (reward + discountFactor * maxNewQValue)

	qTable[appleDirection, dangerDirection, actionIndex] = newQValue

while True:
	epsilon -= epsilonDecay

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				snakeDirection = (0, -TILE_SIZE)
			if event.key == pygame.K_s:
				snakeDirection = (0, TILE_SIZE)
			if event.key == pygame.K_a:
				snakeDirection = (-TILE_SIZE, 0)
			if event.key == pygame.K_d:
				snakeDirection = (TILE_SIZE, 0)
			if event.key == pygame.K_r:
				snake.center, food.center = getRandomPosition(), getRandomPosition()
				length, snakeDirection = 1, (0, 0)
				segments = [snake.copy()]
				score = 0

	print(epsilon)

	screen.fill("black")

	pygame.display.set_caption(f'AI Plays Snake (Score: {score}, Max Score: {maxScore})')

	pygame.draw.rect(screen, "red", food)

	[pygame.draw.rect(screen, "green", segment) for segment in segments]

	timeNow = pygame.time.get_ticks()
	if timeNow - time > timeStep:
		time = timeNow

		state = getState(snake, food, segments)
		action = chooseAction(state, qTable)
		snakeDirection = action
		snake.move_ip(snakeDirection)

		reward = 0
		if snake.center == food.center:
			reward = 10
		elif snake.left < 0 or snake.right > WINDOW or snake.top < 0 or snake.bottom > WINDOW or pygame.Rect.collidelist(snake, segments[:-1]) != -1:
			reward = -10
		else:
			reward = -0.1

		segments.append(snake.copy())
		segments = segments[-length:]

		newState = getState(snake, food, segments)
		updateQTable(qTable, state, action, reward, newState)

	selfEating = pygame.Rect.collidelist(snake, segments[:-1]) != -1
	if snake.left < 0 or snake.right > WINDOW or snake.top < 0 or snake.bottom > WINDOW or selfEating:
		snake.center, food.center = getRandomPosition(), getRandomPosition()
		length, snakeDirection = 1, (0, 0)
		segments = [snake.copy()]
		score = 0

	if snake.center == food.center:
		food.center = getRandomPosition()
		length += 1
		score += 1
		if score > maxScore:
			maxScore = score

	pygame.display.flip()

	if pygame.key.get_pressed()[pygame.K_DOWN]:
		timeStep = 110
		clock.tick(60)
	else:
		timeStep = 1
		clock.tick(480)