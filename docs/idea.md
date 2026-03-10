# Summary

This is an Home Assistant project to create a comfortable to use "smart" scene toggler:

Iteration 1:

- toggle between two scenes in an automation
- change one or both scenes, if changing the currently active scene, reactivate with new value
- Allow to create any number of scene togglers

For example:

Iteration 1:

Have a home automation light switch button.
a scene toggler is configured: it switches between "Daylight" and "All lights off"
i press the button and the light goes on and of.
then, at 19:00, a home assistant timer changes scene A to "Evening". As the light is currently on, the scene fades over from "Daylight" to "Evening".
At 23:30, another timer changes scene A to "candle light". It fades over to this scene, as scene A was still the active state.
Then i turn off lights at the end of the day.
At 08:00, a timer changes scene A to "Daylight". As the current state is scene B, nothing is triggered, lights stay off.

I create one of these setups for each room.

# Homework to do before anything is created

- update the CLAUDE.md with persistent instructions when appropriate.
- use subagents. detect and discuss, what agents would make sense for this project.
- take a look at existing home assistant projects, to get a feel about current best practice.
- discuss technical approaches to this project, if there are options.
- suggest good names for this project.
- use git.
- use uv.
- create unittests using pytest
- use conventional commits.
- commit each funtional set of changes seperately
- increase version number accordingly 
- be verbose throughout the blueprint.
- create documentation in a way that is best practive for home assistant projects.

