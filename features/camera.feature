Feature: Camera
  How the player ship is framed.

  Scenario: The camera sits behind and above the ship and looks where it points
    Given a player ship flying steadily
    Then the camera is at the "camera.offset" in the ship's own frame
    And the camera looks along the "camera.aim", with the ship's up as its up
    And the field of view is the "camera.fov_degrees"
    And nothing farther than the "camera.far_plane" is drawn

  Scenario: The camera follows the ship smoothly
    When the ship moves or turns
    Then the camera closes the gap to its "camera.offset" position at the "camera.follow_rate"

  Scenario: The camera snaps into place when a session starts and after a jump
    When a solo session starts
    Then the camera is at once at its "camera.offset" position
    When the player ship jumps to another star system
    Then the camera is at once at its "camera.offset" position

  Scenario: The camera does not snap on respawn
    When the player ship is destroyed and comes back at the arrival point
    Then the camera closes the gap to its "camera.offset" position at the "camera.follow_rate"
