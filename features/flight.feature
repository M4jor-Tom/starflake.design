Feature: Flight
  How a ship moves. The same rules apply to the player ship and to enemy
  ships, except at the bounds of the star system.

  Scenario: Thrust accelerates the ship along its nose
    Given a player ship at rest whose ship class has an acceleration of 20 metres per second squared
    When the player holds "thrust" for 1 second
    Then the ship moves at 20 metres per second in the direction of its nose

  Scenario: Reverse accelerates the ship away from its nose
    Given a player ship at rest whose ship class has an acceleration of 20 metres per second squared
    When the player holds "reverse" for 1 second
    Then the ship moves at 20 metres per second in the direction opposite to its nose

  Scenario: Without throttle, drag brings the ship to rest
    Given a player ship moving at 30 metres per second
    When the player holds neither "thrust" nor "reverse"
    Then the ship slows down at the "flight.drag_fraction" of its ship class acceleration
    And the ship stays at rest once its speed reaches 0

  Scenario: Speed never exceeds the max speed of the ship class
    Given a player ship moving at its ship class max speed of 120 metres per second
    When the player holds "thrust" for 1 second
    Then the ship moves at 120 metres per second

  Scenario: Pitch turns the ship about its own lateral axis
    Given a player ship whose ship class has a turn rate of 1.5 radians per second
    When the player holds "pitch_up"
    Then the nose rises at 1.5 radians per second relative to the ship itself
    When the player holds "pitch_down"
    Then the nose drops at 1.5 radians per second relative to the ship itself

  Scenario: Yaw turns the ship about its own vertical axis
    Given a player ship whose ship class has a turn rate of 1.5 radians per second
    When the player holds "yaw_left"
    Then the nose swings to the ship's left at 1.5 radians per second
    When the player holds "yaw_right"
    Then the nose swings to the ship's right at 1.5 radians per second

  Scenario: Roll turns the ship about its own nose axis
    Given a player ship whose ship class has a turn rate of 1.5 radians per second
    When the player holds "roll_left"
    Then the ship's left side dips at 1.5 radians per second
    When the player holds "roll_right"
    Then the ship's right side dips at 1.5 radians per second

  Scenario: The player ship slides along the bounds of the star system
    Given a player ship in a star system with a bounds radius of 10000 metres
    When the ship would move farther than 10000 metres from the star
    Then the ship is held at 10000 metres from the star
    And the ship keeps only the part of its velocity that runs along the bounds

  Scenario: Enemy ships are not held by the bounds of the star system
    Given an enemy ship in a star system with a bounds radius of 10000 metres
    When the enemy ship moves farther than 10000 metres from the star
    Then the enemy ship keeps its position and its velocity

  Scenario: Turning does not redirect the ship's velocity
    Given a player ship moving at 30 metres per second along its nose
    When the player turns the ship without holding "thrust" or "reverse"
    Then the ship keeps moving in its former direction while drag slows it

  Scenario: Thrust and reverse held together count as no throttle
    Given a player ship moving at 30 metres per second
    When the player holds "thrust" and "reverse" together
    Then the ship slows down at the "flight.drag_fraction" of its ship class acceleration
