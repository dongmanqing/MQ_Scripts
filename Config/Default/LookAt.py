from math import radians


class Priority:
    """
    List of interest levels
    """

    REJECT: int = -500
    BORED_OF_THIS_ITEM = -300
    NONE: int = 0
    NOT_VERY_INTERESTED: int = 50
    IDLE: int = 100
    FOUND: int = 200
    INTERESTED: int = 300
    VERY_INTERESTED: int = 600
    REQUESTED: int = 1000
    REQUIRED: int = 2000


# Parameters specific to each contributor
# For each contributor, you can optionally define:
# - priority: the default score of the LookAtItems from this contributor
# - lifetime: the length of time after which a LookAtItem is dropped if it is not looked at.
# - clear_after_look: if true, the item is cleared after being looked at. Defaults to false.
# - boredom_period: the (min, max) time an item gets boring after when it is being looked at
# - interested_period: the (min, max) time an object stays interesting for when it enters a scene.
# - eyes_only: if True, only the eyes should look at this. Defaults to False.
CONTRIBUTORS = {
    "sound": {
        # A sound has high priority, and a short lifetime. It is only looked at briefly.
        "priority": Priority.VERY_INTERESTED,
        "lifetime": 0.5,
        "boredom_period": (0.1, 0.2),
    },
    "glance": {
        # A glance has high priority - it should be prioritised over most other items. It only affects the eyes.
        "priority": Priority.VERY_INTERESTED,
        "lifetime": 0.2,
        "eyes_only": True,
    },
    "thinking_look_up": {
        # Thinking looking up is REQUIRED priority and a long lifetime as it should usually be disabled
        # by the thinking script before that lifetime is done
        "priority": Priority.REQUIRED,
        "lifetime": 8,
        "min_active_duration": 0.5,
        "eyes_only": True,
    },
    "look_around": {
        # Lookaround items are very low priority, short lifetime and short lookat period. They should
        # only take effect when nothing else is active.
        "priority": Priority.NOT_VERY_INTERESTED,
        "lifetime": 0.1,
        "min_active_duration": 0.5,
    },
    "telepresence_click": {
        # Telepresence clicks have REQUESTED priority, and last a relatively long time.
        "priority": Priority.REQUESTED,
        "lifetime": 5,
    },
    "user_request": {
        # User requests (e.g. user says "Please look up") have Very high priority, and quite a long lifetime
        "priority": Priority.REQUESTED,
        "lifetime": 0.6,
        "min_active_duration": 0.8,
    },
    "sequence_gaze_target": {
        # sequence gaze targets have REQUIRED priority, and must be explicitly cancelled by scripts
        "priority": Priority.REQUIRED,
        "min_active_duration": 0.3,
        "eyes_only": True,
    },
    "faces": {
        # Faces have quite high priority, and no lifetimes (they are explictly dropped by the script) which
        # manages them. They are interestig when new, and get boring after being looked at for a while.
        "priority": Priority.INTERESTED,
        "boredom_period": (5, 10),
        "interested_period": (1, 2),
        "min_active_duration": 0.4,
    },
}


# Glance configuration
GLANCES_PERIOD_RANGE = (2, 6)
GLANCES_X_DIST = 5
GLANCES_Y_RANGE = (1, 2)
GLANCES_Z_RANGE = (-1, 1)


# Sound lookaround configuration
SOUND_COOLDOWN_TIME = 2  # Cooloff time for sounds from a given direction
SOUND_DIFF_THRESHOLD = 5  # Difference threshold for sounds from the same direction
SOUND_LOOKAROUND_HEIGHT = 1.7  # Height to look at for sounds


# The score added by the AngleScorer to items outside of the range
ANGLE_OVER_MAX_SCORE = Priority.REJECT
ANGLE_MAX_THETA = radians(50)
ANGLE_MAX_PHI = radians(70)


# The score added by the lazy contributor to the currently active item
LAZY_ACTIVE_SCORE = Priority.NOT_VERY_INTERESTED


# The bored scorer is responsible for enforcing thr lookat period
BORED_SCORE = Priority.BORED_OF_THIS_ITEM
INTERESTED_SCORE = Priority.FOUND
MIN_INTERESTED_TIME_S = 1  # Minimum time while an object stays interesting
MAX_INTERESTED_TIME_S = 2  # Maximum time while an object stays interesting

# Lookaround settings
LOOKAROUND_DELAY = (0.8, 2)
LOOKAROUND_Y_RANGE = (-2, 2)
LOOKAROUND_Z_RANGE = (1.3, 1.8)
LOOKAROUND_N_Y_ZONES = 3
LOOKAROUND_N_Z_ZONES = 2
LOOKAROUND_ZONE_COOLDOWN_TIME = 5
