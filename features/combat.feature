Feature: Combat
  Firing, bolts and damage. The Destruction feature covers what a hit to zero leaves.

  Scenario: Holding fire fires every weapon of the ship class, each at its own fire rate
    Given a player ship whose ship class has a weapon with a fire rate of 2 shots per second
    And another weapon with a fire rate of 5 shots per second
    When the player starts holding "fire"
    Then each weapon fires one bolt at once
    And the first weapon fires again every 0.5 seconds while "fire" is held
    And the second weapon fires again every 0.2 seconds while "fire" is held

  Scenario: A bolt starts ahead of the nose and inherits the shooter's velocity
    Given a ship moving at 50 metres per second along its nose
    And a weapon with a projectile speed of 400 metres per second
    When the ship fires the weapon
    Then the bolt starts on the line of the ship's nose, ahead of the ship by the "flight.ship_hit_radius" plus the "flight.muzzle_clearance"
    And the bolt flies straight at 450 metres per second in the direction of the nose

  Scenario: A bolt disappears beyond the max range of its weapon
    Given a bolt of a weapon with a max range of 1500 metres
    When the bolt is farther than 1500 metres from where it started
    Then the bolt disappears

  Scenario: A player bolt damages the asteroid it meets
    Given an asteroid with 30 integrity
    And a bolt fired by the player ship from a weapon with a damage of 10
    When the path of the bolt passes within the radius of the asteroid's type
    Then the asteroid has 20 integrity
    And the bolt disappears

  Scenario: A player bolt damages the enemy ship it meets
    Given an enemy ship with 30 hull
    And a bolt fired by the player ship from a weapon with a damage of 10
    When the path of the bolt passes within the "flight.ship_hit_radius" of the enemy ship
    Then the enemy ship has 20 hull
    And the bolt disappears

  Scenario: Damage never takes integrity or hull below zero
    Given an asteroid with 5 integrity
    When it is hit by a bolt from a weapon with a damage of 10
    Then the asteroid has 0 integrity

  Scenario: Enemy bolts hit only the player ship
    Given a bolt fired by an enemy ship from a weapon with a damage of 10
    When the path of the bolt passes through an asteroid or another enemy ship
    Then the asteroid or enemy ship is not damaged and the bolt flies on
    When the path of the bolt passes within the "flight.ship_hit_radius" of the player ship
    Then the player ship loses 10 hull
    And the bolt disappears

  Scenario: Releasing fire does not let a weapon beat its fire rate
    Given a player ship whose ship class has a weapon with a fire rate of 2 shots per second
    And the weapon has just fired
    When the player releases "fire" and holds it again 0.2 seconds later
    Then the weapon fires its next bolt 0.5 seconds after the previous one

  Scenario: Bolts in flight disappear when the player ship jumps
    Given bolts are in flight in a star system
    When the player ship jumps to another star system
    Then those bolts are gone, also when the player ship comes back
