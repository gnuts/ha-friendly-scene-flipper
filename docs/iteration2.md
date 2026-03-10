# Iteration 2: Quality of Life Improvements

## Fix Taxonomy

Refactor naming of things, including the project name.

Have the features clearly and consistently named:

- Friendly Scene Flipper: This project!  "A scene flipper that is easy to understand."
- Scene Flipper: Each generated configuration
- Toggler: Toggle between A and B
- Setter: Replace the current scene with a specific value for A and/or B
- Skipper: Skip the next scene change
- Flipper: Iterate through a list of scenes, separately for A and B. Both directions!
- TimePoints: Points in time where scene A or B or both can be changed, automatically triggered if TimePoint is enabled. Repeatable, e.g., each morning at 7:00, except on weekends.

## Skipper

Allow to skip the next automatic chance of one or both scenes.

That means, Toggler still works as normal and toggles scenes A and B, it only skips the next automatic scene change that would otherwise happen via a TimePoint.

This is useful to say for example by long-pressing the light switch: "hey i am still working, skip automatic scene change to after work mode, keep the current scene even after 19:00"

## Setter

Allow to set the scene A or B value "manually" in an automated way.

For example, if i press another button, set the scene to Fancy Special Light.

Optionally respect if Skipper for this Scene Flipper had activated

## Flipper

Allow for flipping through a list of scenes, replacing the currently active one.

Two separate lists for scene A and B. Skip is performed on the active scene (A or B).
This will be useful to manually flip through scenes instead of selecting a specific one.

If this list is emtpy, the skip feature does nothing.

Optionally respect if Skipper for this Scene Flipper had activated

## TimePoints

Allow for adding any number of points in time where scene A or B or both can be changed.

Useful to e.g., automatically switch from Worklight to Evening Light, to Late Night Candle Light. 

## Easy to understand

Add explanatory text to the user interface.
We should have a low-to-moderate skill level requirement for the user.
We can use thematically fitting emojis. But in a tasteful way, please. That means don't spam and don't make to colorful everywhere. Keep it slick.

