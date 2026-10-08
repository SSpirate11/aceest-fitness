"""Pure business logic for ACEest Fitness & Gym.

Ported from the Tkinter prototypes (Aceestver-1.0 ... 3.2.4) into
framework-independent functions so they can be unit-tested in isolation.
"""
import random
from datetime import date

PROGRAMS = {
    "FL": {
        "name": "Fat Loss",
        "calorie_factor": 22,
        "workout": [
            "Mon: Back Squat 5x5 + Core",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: Deadlift + Box Jumps",
            "Fri: Zone 2 Cardio 30min",
        ],
        "diet": [
            "Breakfast: Egg Whites + Oats",
            "Lunch: Grilled Chicken + Brown Rice",
            "Dinner: Fish Curry + Millet Roti",
            "Target: ~2000 kcal",
        ],
    },
    "MG": {
        "name": "Muscle Gain",
        "calorie_factor": 35,
        "workout": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10",
        ],
        "diet": [
            "Breakfast: Eggs + Peanut Butter Oats",
            "Lunch: Chicken Biryani",
            "Dinner: Mutton Curry + Rice",
            "Target: ~3200 kcal",
        ],
    },
    "BG": {
        "name": "Beginner",
        "calorie_factor": 26,
        "workout": [
            "Full Body Circuit: Air Squats, Ring Rows, Push-ups",
            "Focus: Technique & Consistency",
        ],
        "diet": [
            "Balanced Tamil Meals: Idli / Dosa / Rice + Dal",
            "Protein Target: 120g/day",
        ],
    },
}

EXERCISE_POOL = {
    "Strength": ["Squat", "Deadlift", "Bench Press", "Overhead Press",
                 "Pull-Up", "Barbell Row"],
    "Hypertrophy": ["Leg Press", "Incline Dumbbell Press", "Lat Pulldown",
                    "Lateral Raise", "Bicep Curl", "Tricep Extension"],
    "Conditioning": ["Running", "Cycling", "Rowing", "Burpees",
                     "Jump Rope", "Kettlebell Swings"],
    "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank",
                  "Dumbbell Row", "Dumbbell Press"],
}

LEVELS = {
    "beginner": {"sets": (2, 3), "reps": (8, 12), "days": 3},
    "intermediate": {"sets": (3, 4), "reps": (8, 15), "days": 4},
    "advanced": {"sets": (4, 5), "reps": (6, 15), "days": 5},
}

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def get_program(code):
    """Return a program by its short code (case-insensitive) or None."""
    if not code:
        return None
    return PROGRAMS.get(code.strip().upper())


def calculate_calories(weight_kg, program_code):
    """Daily calorie target = body weight (kg) x program factor."""
    program = get_program(program_code)
    if program is None:
        raise ValueError(f"Unknown program: {program_code}")
    weight = float(weight_kg)
    if weight <= 0:
        raise ValueError("Weight must be a positive number")
    return int(weight * program["calorie_factor"])


def calculate_bmi(weight_kg, height_cm):
    """Return (bmi, category) using the thresholds from version 2.2.4."""
    weight, height = float(weight_kg), float(height_cm)
    if weight <= 0 or height <= 0:
        raise ValueError("Height and weight must be positive numbers")
    h_m = height / 100.0
    bmi = round(weight / (h_m * h_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


def generate_program(program_code, level, seed=None):
    """AI-style weekly plan generator (ported from version 3.1.2)."""
    level_key = (level or "").strip().lower()
    if level_key not in LEVELS:
        raise ValueError("Level must be beginner, intermediate or advanced")
    program = get_program(program_code)
    name = program["name"] if program else ""
    focus = "Full Body"
    if "Fat Loss" in name:
        focus = "Conditioning"
    elif "Muscle Gain" in name:
        focus = "Hypertrophy"

    cfg = LEVELS[level_key]
    rng = random.Random(seed)
    per_day = 3 if cfg["days"] < 4 else 4
    plan = []
    for day in WEEK_DAYS[:cfg["days"]]:
        for exercise in rng.sample(EXERCISE_POOL[focus], k=per_day):
            plan.append({
                "day": day,
                "exercise": exercise,
                "sets": rng.randint(*cfg["sets"]),
                "reps": rng.randint(*cfg["reps"]),
            })
    return {"focus": focus, "level": level_key, "days": cfg["days"],
            "plan": plan}


def membership_status(end_date, today=None):
    """Return 'Active', 'Expired' or 'Unknown' for an ISO end date."""
    if not end_date:
        return "Unknown"
    today = today or date.today()
    try:
        end = date.fromisoformat(end_date)
    except ValueError:
        return "Unknown"
    return "Active" if end >= today else "Expired"
