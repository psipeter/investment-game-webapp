ROUNDS = 5  # rounds per game
CAPITAL = 10  # don't change this - money available to A 
MATCH = 3  # don't change this  - multiplication of A's investment to B
REQUIRED = 20  # number of required games
EPSILON = 0.0  # probability agent will move randomly
SIGMA = 0.0  # standard deviation added to agent move
BONUS = [  # thresholds for bonus winnings based on performance, [threshold, money]
	[0, 0.10],
	[60, 0.15],
	[80, 0.20],
	[100, 0.25],
	[120, 0.30],
	[150, 0.30],
]
PLAYERS = [  # ["userRole", "agentRole"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["A", "B"],
	["B", "A"],
	["B", "A"],
	["B", "A"],
]

AGENTS_A_1 = [  # learn to be generous group
	"T4T_X04",
	"T4T_X06",
	"T4T_X04",
	"T4T_X06",
	"T4T_X06",
	"T4T_X04",
	"T4T_X06",
	"T4T_X04",
	"T4T_X04",
	"T4T_X06",
]
AGENTS_B_1 = [
	"T4T",
	"Fixed_M05",
	"T4T",
	"Fixed_M08",
	"T4T",
	"T4T",
	"Fixed_M05",
	"Fixed_M08",
	"T4T",
	"Fixed_M05",
]
AGENTS_A_2 = [  # learn to be greedy group
	"Fixed_M05",
	"T4T_X02",
	"Fixed_M08",
	"T4T_X04",
	"T4T_X02",
	"Fixed_M05",
	"T4T_X02",
	"Fixed_M08",
	"T4T_X02",
	"Fixed_M05",
]
AGENTS_B_2 = [
	"Fixed_M02",
	"Greedier",
	"Fixed_M02",
	"Greedier",
	"Greedier",
	"Fixed_M02",
	"Greedier",
	"Fixed_M02",
	"Fixed_M02",
	"Greedier",
]