Feature: Enemy AI
  How an enemy ship behaves toward the player ship. Enemy ships fly by the
  rules of the Flight feature.

  Scenario: At or beyond its detection range an enemy is idle
    Given an enemy ship whose type has a detection range of 2000 metres
    When the player ship is farther than 2000 metres from it
    Then the enemy ship does not turn
    And the enemy ship does not thrust
    And the enemy ship does not fire
    When the player ship is exactly 2000 metres from it
    Then the enemy ship still does not turn, thrust or fire

  Scenario: Closer than its detection range an enemy closes in to the keep distance
    Given an enemy ship whose type has a detection range of 2000 metres
    When the player ship is closer than 2000 metres to it and farther than the "enemy_ai.keep_distance"
    Then the enemy ship turns its nose toward the player ship
    And the enemy ship thrusts at full throttle

  Scenario: At or within the keep distance an enemy stops thrusting
    Given an enemy ship whose type has a detection range of 2000 metres
    When the player ship is closer to it than the "enemy_ai.keep_distance"
    Then the enemy ship turns its nose toward the player ship
    And the enemy ship does not thrust
    When the player ship is exactly at the "enemy_ai.keep_distance" from it
    Then the enemy ship still does not thrust

  Scenario: An enemy steers harder the farther the player is off its nose
    Given an enemy ship that has detected the player ship ahead of it
    Then its pitch and yaw inputs are the sideways offsets of the player's direction multiplied by the "enemy_ai.steering_gain"
    And each input is capped at a full turn input
    And the enemy ship never rolls

  Scenario: With the player behind it, an enemy yaws at the full turn rate toward the nearer side
    Given an enemy ship that has detected the player ship behind it
    When the player ship is on its right
    Then the enemy ship yaws right at the turn rate of its ship class, without pitching
    When the player ship is straight behind it
    Then the enemy ship yaws right at the turn rate of its ship class, without pitching
    When the player ship is on its left
    Then the enemy ship yaws left at the turn rate of its ship class, without pitching

  Scenario: An enemy fires only in range and with the player inside its aim cone
    Given an enemy ship that has detected the player ship
    And the longest max range among the weapons of its ship class is 1500 metres
    When the player ship is closer than 1500 metres and the angle between the enemy's nose and the player's direction is less than the "enemy_ai.aim_cone"
    Then the enemy ship fires every weapon of its ship class, each at its own fire rate
    When the player ship is 1500 metres away or farther
    Then the enemy ship does not fire
    When the angle between the enemy's nose and the player's direction is the "enemy_ai.aim_cone" or more
    Then the enemy ship does not fire
