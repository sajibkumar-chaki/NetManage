"""Deliberately failing CI evidence. This branch must never be merged."""


def test_intentional_failure_blocks_delivery():
    assert False, "Intentional assessment pipeline check; do not merge this branch."
