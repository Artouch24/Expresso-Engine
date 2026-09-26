"""Generic poker enumerations."""

from enum import StrEnum


class Street(StrEnum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class ActionType(StrEnum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    POST_SMALL_BLIND = "post_small_blind"
    POST_BIG_BLIND = "post_big_blind"
    ALL_IN = "all_in"


class Position(StrEnum):
    BUTTON = "BTN"
    SMALL_BLIND = "SB"
    BIG_BLIND = "BB"
