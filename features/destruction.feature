Feature: Destruction
  What a destroyed asteroid or enemy ship leaves behind.

  Scenario: A destroyed asteroid leaves a loot drop holding its fuel
    Given an asteroid whose type has a fuel drop of 15
    When a hit takes its integrity to 0
    Then the asteroid is removed from the star system
    And a loot drop with a fuel amount of 15 floats where the asteroid was

  Scenario: A destroyed enemy ship leaves a loot drop holding its fuel
    Given an enemy ship whose type has a fuel drop of 40
    When a hit takes its hull to 0
    Then the enemy ship is removed from the star system
    And a loot drop with a fuel amount of 40 floats where the enemy ship was
