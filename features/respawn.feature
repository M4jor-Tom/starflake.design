Feature: Respawn
  What happens when the player ship is destroyed.

  Scenario: A destroyed player ship comes back repaired at the arrival point, keeping its fuel
    Given a player ship holding 35 fuel whose ship class has a max hull of 100
    When a hit takes its hull to 0
    Then the ship has 100 hull
    And the ship holds 35 fuel
    And the ship is in the same star system
    And the ship is at rest at the arrival point of that star system, facing the star
    And the HUD flashes "ship_destroyed"

  Scenario: The star system is unchanged by a respawn
    Given a star system holding 3 asteroids, 2 enemy ships and 1 loot drop
    When the player ship is destroyed there
    Then the star system holds the same 3 asteroids, 2 enemy ships and 1 loot drop
    And each enemy ship keeps its hull, its position and its velocity
