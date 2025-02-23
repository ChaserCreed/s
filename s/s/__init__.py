# s/__init__.py

"""
s package

Provides functions to set up a Selenium driver with advanced anti-detection measures
and utilities for interacting with web pages.
"""

from .core import (
    set_up_driver,
    keep_awake,
    find,
    find_by_text,
    get_info,
    click_button,
    fill_text,
    select_dropdown
)

__all__ = [
    "set_up_driver",
    "keep_awake",
    "find",
    "find_by_text",
    "get_info",
    "click_button",
    "fill_text",
    "select_dropdown"
]
