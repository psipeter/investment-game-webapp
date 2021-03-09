ROUNDS = 5
CAPITAL = 10  # don't change this
MATCH = 3  # don't change this
REQUIRED = 10
MAX = 40
FIXED_REWARD = 2
BONUS = [
	[0, 0.05],
	[60, 0.10],
	[80, 0.15],
	[100, 0.20],
	[120, 0.25],
	[150, 0.25],
]
REQUIRED_ROLES = [
	# ["userRole", "agentRole"],
	["B", "A"],
	["B", "A"],
	["B", "A"],
	["B", "A"],
	["A", "B"],
	["A", "B"],
	["B", "A"],
	["B", "A"],
	["B", "A"],
	["B", "A"],
]
REQUIRED_AGENTS = [
	"Expect_X05",
	"Expect_X03",
	"Expect_X03",
	"Greedy",
	"T4T",
	"T4T",
	"T4T",
	"T4T",
	"T4T",
	"T4T",
]
BONUS_AGENTS_F_B = [
	"T4T",
]
BONUS_AGENTS_F_A = [
	"T4T",
]
BONUS_AGENTS_P_B = [
	"T4T",
]
BONUS_AGENTS_P_A = [
	"T4T",
]