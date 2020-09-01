# Contributing to BBO

Contributions are welcome, and they are greatly appreciated! Every
little bit helps. Also, receiving feedback in order to accommodate for our users' need is very important to us.

## Want to implement a new heuristic ?

If you want to use a heuristic that is not yet available in the BBO package, no problem ! The package's philosophy is to provide an easy interface for adding new heuristics on the fly.
Your new algorithm will need to inherit from the ```Heuristic``` class and respect its conditions. For more precisions about the mandatory methods and attributes,
please refer to the class documentation.

For your unit testing (that is of course mandatory if you want your PR to be merged ;)), please add the tests for your
heuristics in the file [tests/test_heuristics.py](tests/test_heuristics.py) and the tests for the functions that are specific to the new heuristic in a file that you will call ```test_nameofmyheuristic.py```.

## Found an issue or a Bug?

If you find a bug in the source code, you can help us by submitting an issue to our Repository. Even better, you can submit a Pull Request with a fix. We'll review it, and, once accepted,
you will be able to merge it with the rest of the code.

## Author contact information

If you want to contact me in order to discuss the ```BBO``` package, please feel
free to e-mail me at [sophie.robert@atos.net](sophie.robert@atos.net).