Feature: Loot
  How the player ship collects the fuel left by destroyed asteroids and enemies.

  Scenario: A loot drop within the magnet radius moves toward the player ship
    Given a player ship whose tank is not full
    And a loot drop within the "loot.magnet_radius" of the ship but outside the "loot.pickup_radius"
    Then the loot drop moves straight toward the ship at the "loot.magnet_speed"

  Scenario: A loot drop beyond the magnet radius stays where it is
    Given a player ship whose tank is not full
    And a loot drop farther from the ship than the "loot.magnet_radius"
    Then the loot drop does not move

  Scenario: A loot drop within the pickup radius is collected
    Given a player ship holding 10 fuel whose ship class has a fuel capacity of 100
    When a loot drop with a fuel amount of 25 is within the "loot.pickup_radius" of the ship
    Then the ship holds 35 fuel
    And the loot drop is removed from the star system

  Scenario: Collected fuel beyond the fuel capacity is lost
    Given a player ship holding 90 fuel whose ship class has a fuel capacity of 100
    When a loot drop with a fuel amount of 25 is within the "loot.pickup_radius" of the ship
    Then the ship holds 100 fuel
    And the loot drop is removed from the star system

  Scenario: With a full tank, loot drops are neither attracted nor collected
    Given a player ship holding 100 fuel whose ship class has a fuel capacity of 100
    When a loot drop is within the "loot.pickup_radius" of the ship
    Then the loot drop does not move
    And the loot drop stays in the star system
    And the ship holds 100 fuel
