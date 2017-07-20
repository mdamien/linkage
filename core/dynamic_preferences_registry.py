# blog/dynamic_preferences_registry.py

from dynamic_preferences.types import IntegerPreference, Section
from dynamic_preferences.registries import global_preferences_registry

# we create some section objects to link related preferences together
linkage_cpp = Section('linkage_cpp')


@global_preferences_registry.register
class LDAOuterTitle(IntegerPreference):
    section = linkage_cpp
    name = 'max_outer_lda'
    default = 10


@global_preferences_registry.register
class LDAOuterTitle(IntegerPreference):
    section = linkage_cpp
    name = 'max_inner_lda'
    default = 10


@global_preferences_registry.register
class LDARepeatTitle(IntegerPreference):
    section = linkage_cpp
    name = 'n_repeat'
    default = 4
