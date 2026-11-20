Feature: Loot
  How the player ship collects the fuel left by destroyed asteroids and enemies.

  Scenario: A loot drop closer than the magnet radius moves toward the player ship
    Given a player ship whose tank is not full
    And a loot drop closer to the ship than the "loot.magnet_radius" but not closer than the "loot.pickup_radius"
    Then the loot drop moves straight toward the ship at the "loot.magnet_speed"
    When the loot drop is exactly at the "loot.pickup_radius" from the ship
    Then the loot drop still moves toward the ship and is not collected yet

  Scenario: A loot drop at or beyond the magnet radius stays where it is
    Given a player ship whose tank is not full
    And a loot drop farther from the ship than the "loot.magnet_radius"
    Then the loot drop does not move
    When the loot drop is exactly at the "loot.magnet_radius" from the ship
    Then the loot drop still does not move

  Scenario: A loot drop closer than the pickup radius is collected
    Given a player ship holding 10 fuel whose ship class has a fuel capacity of 100
    When a loot drop with a fuel amount of 25 is closer to the ship than the "loot.pickup_radius"
    Then the ship holds 35 fuel
    And the loot drop is removed from the star system

  Scenario: Collected fuel beyond the fuel capacity is lost
    Given a player ship holding 90 fuel whose ship class has a fuel capacity of 100
    When a loot drop with a fuel amount of 25 is closer to the ship than the "loot.pickup_radius"
    Then the ship holds 100 fuel
    And the loot drop is removed from the star system

  Scenario: With a full tank, loot drops are neither attracted nor collected
    Given a player ship holding 100 fuel whose ship class has a fuel capacity of 100
    When a loot drop is closer to the ship than the "loot.pickup_radius"
    Then the loot drop does not move
    And the loot drop stays in the star system
    And the ship holds 100 fuel
