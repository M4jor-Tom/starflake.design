Feature: Session
  What a solo session starts with, and how star systems are populated.

  Scenario: A new solo session starts with a full hull and an empty tank
    Given a content pack whose starting ship class has a max hull of 100
    When a solo session starts
    Then the player ship is of the starting ship class
    And the player ship is in the galaxy's starting system
    And the player ship has 100 hull and 0 fuel
    And the player ship is at rest at the arrival point of that star system, facing the star

  Scenario: The arrival point lies on the +Z axis of the star system
    Given a star system with a bounds radius of 10000 metres
    Then its arrival point is on its +Z axis, at the "flight.arrival_distance_fraction" of the bounds radius from the star

  Scenario: A star system spawns its regions on the first visit
    Given a star system that no ship has visited
    And it has an asteroid field with a spawn count of 5
    And it has an enemy group with a spawn count of 2
    When the player ship enters the star system
    Then the star system holds 5 asteroids of the field's asteroid type, each at its max integrity
    And the star system holds 2 enemy ships of the group's enemy type, each at the max hull of its ship class
    And each of them is within the radius of its region, measured from the region's center

  Scenario: A revisited star system keeps its state
    Given the player ship has broken 2 of the 5 asteroids of a star system
    And 1 loot drop is left floating there
    When the player ship jumps away and comes back
    Then the star system holds the same 3 asteroids, where they were
    And the same loot drop, where it was
    And nothing has spawned again

  Scenario: Enemy ships of a revisited star system are as they were left
    Given an enemy ship that has lost 20 of its hull and is moving
    When the player ship jumps away and comes back
    Then the enemy ship has the same hull, position, velocity and attitude as when the player ship left
