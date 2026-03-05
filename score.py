"""Score tracking and ranking system."""

import time as time_module


class ScoreTracker:
    """Tracks the player's performance across a full game run.

    Calculates a final score based on time taken, decoys used,
    and number of times caught.

    Attributes:
        level_times: List of seconds taken per level.
        total_decoys_used: Total decoys deployed across all levels.
        total_deaths: Number of times caught by enemies.
    """

    def __init__(self):
        self.level_start_time = 0
        self.level_times = []
        self.total_decoys_used = 0
        self.total_deaths = 0
        self.decoys_at_level_start = 3

    def start_level(self, decoy_count):
        """Record the start time of a new level."""
        self.level_start_time = time_module.time()
        self.decoys_at_level_start = decoy_count

    def finish_level(self, decoys_remaining):
        """Record level completion and calculate decoys used."""
        elapsed = time_module.time() - self.level_start_time
        self.level_times.append(elapsed)
        self.total_decoys_used += (self.decoys_at_level_start - decoys_remaining)

    def record_death(self):
        """Increment the death counter."""
        self.total_deaths += 1

    def get_total_time(self):
        """Get total time across all completed levels."""
        return sum(self.level_times)

    def get_final_score(self):
        """Calculate the final score (higher is better).

        Formula: base 10000 - (time penalty) - (decoy penalty) - (death penalty)
        Minimum score is 0.

        Returns:
            Integer score value.
        """
        base = 10000
        time_penalty = int(self.get_total_time() * 15)
        decoy_penalty = self.total_decoys_used * 200
        death_penalty = self.total_deaths * 1500
        return max(0, base - time_penalty - decoy_penalty - death_penalty)

    def get_rank(self):
        """Return a letter rank based on the final score."""
        score = self.get_final_score()
        if score >= 8000:
            return "S"
        elif score >= 6000:
            return "A"
        elif score >= 4000:
            return "B"
        elif score >= 2000:
            return "C"
        else:
            return "D"

    def reset(self):
        """Reset all tracking data for a new game."""
        self.level_times = []
        self.total_decoys_used = 0
        self.total_deaths = 0
        self.decoys_at_level_start = 3
        self.level_start_time = 0
