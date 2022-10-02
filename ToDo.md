# ToDo:

* define entity data structure with visual geometry and collision geometry. Collision geometry may contain only rectangles
and circles for representing the visual geometry's perimeter.

* make an Entity class that both Tank and Shell derive from. The entity class has data like it's collision geometry and methods for updating it's position. Once derived, methods for updating geometry, exploding, etc.

* add a 'Delete All' menu option to delete all save files. Prompt user to confirm action.

* hook up easy/med/hard setting and have it add a random value to the aim angle. Difficulty setting affects the magnitude of the range inputted to the random number generator.

* add more of a visual indicator for the tank whose turn it is