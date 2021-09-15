Tutorial
========

BioSimulators-XPP is available as a command-line program and as a command-line program encapsulated into a Docker image.


Creating COMBINE/OMEX archives and encoding simulation experiments into SED-ML
------------------------------------------------------------------------------

Information about how to create COMBINE/OMEX archives which can be executed by BioSimulators-XPP is available at `BioSimulators <https://biosimulators.org/help>`_.

A list of the algorithms and algorithm parameters supported by XPP is available at `BioSimulators <https://biosimulators.org/simulators/xpp>`_.

Models (XPP)
^^^^^^^^^^^^

BioSimulators-XPP can execute models encoded in XPP format (``urn:sedml:language:xpp``).


Simulation experiments (SED-ML, KISAO)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

BioSimulators-XPP can execute simulation experiments encoded in SED-ML, using KiSAO to indicate specific algorithms and their parameters. Information about the algorithms (KiSAO terms), algorithm parameters (KiSAO terms), and outputs (names for variables) supported by BioSimulators-XPP is available from the `BioSimulators registry <https://biosimulators.org/simulators/xpp>`_.


Models (``sedml.Model``)
""""""""""""""""""""""""

Models should be specified using language URN ``urn:sedml:language:xpp``. Model sources can be specified in two ways:

* Path to ``.ode`` files.
* Directories which contain ``.ode`` and optionally set (``.set``), parameter (``.par``), and/or initial conditions (``.ic``) files. ``.set``, ``.par``, and ``.ic`` files can have any filename that ends in these extensions. Directories should contain at most one of each of these three types of files. If supplied, the content of``.set`` files first overrides ``.ode`` files and then ``.par`` and ``.ic`` files can further override definitions of models.

.. code-block:: text

    <model id="model" language="urn:sedml:language:xpp" source="model.ode" />


Targets for model changes (``sedml.AttributeChange``)
"""""""""""""""""""""""""""""""""""""""""""""""""""""
Targets for changes to model parameters should be encoded using the name of the parameter as ``target="{ parameter name }"`` such as ``target="k1"``. The names are parameters are not case sensitive.::

    <attributeChange target="k1" newValue="0.1" />

Targets for changes to initial conditions should be encoded using the name of the variable as ``target="{ variable name }"`` such as ``target="X"``. The names are variables are not case sensitive.::

    <attributeChange target="X" newValue="10.0" />


Simulations (``sedml.UniformTimeCourse``, ``sedml.Algorithm``)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Simulations should be encoded using the ``UniformTimeCourse`` class with simulation algorithms such as ``KISAO_0000019`` (CVODE) and algorithm parameters such as ``KISAO_0000209`` (relative tolerance). Information about the algorithm and algorithm parameter KiSAO terms recognized by BioSimulators-XPP is available from the `BioSimulators registry <https://biosimulators.org/simulators/xpp>`_.::

    <uniformTimeCourse id="simulation">
      <algorithm kisaoID="KISAO:0000019">
         <algorithmParameter kisaoID="KISAO:0000209" newValue="1e-9" />
      </algorithm>
    </uniformTimeCourse>


Targets for observables (``sedml.Variable`` of ``sedml.DataGenerator``)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Targets for XPP variables should be encoded using the name of the variable as ``target="{ variable name }"`` such as ``target="X"``. The names are variables are not case sensitive.::

    <dataGenerator id="data_generator_X">
      <math xmlns="http://www.w3.org/1998/Math/MathML">
        <ci> variable_X </ci>
      </math>
      <listOfVariables>
        <variable id="variable_X" target="X" taskReference="task"/>
      </listOfVariables>
    </dataGenerator>


Example COMBINE/OMEX archives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Examples of COMBINE/OMEX archives for simulations which BioSimulators-XPP can execute are available in the `BioSimulators test suite <https://github.com/biosimulators/Biosimulators_test_suite/tree/deploy/examples>`_.


Command-line program
--------------------

The command-line program can be used to execute COMBINE/OMEX archives that describe simulations as illustrated below.

.. code-block:: text

    usage: biosimulators-xpp [-h] [-d] [-q] -i ARCHIVE [-o OUT_DIR] [-v]

    BioSimulators-compliant command-line interface to the XPP <http://www.math.pitt.edu/~bard/xpp/xpp.html> simulation program.

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           full application debug mode
      -q, --quiet           suppress all console output
      -i ARCHIVE, --archive ARCHIVE
                            Path to OMEX file which contains one or more SED-ML-
                            encoded simulation experiments
      -o OUT_DIR, --out-dir OUT_DIR
                            Directory to save outputs
      -v, --version         show program's version number and exit

For example, the following command could be used to execute the simulations described in ``./modeling-study.omex`` and save their results to ``./``:

.. code-block:: text

    biosimulators-xpp -i ./modeling-study.omex -o ./


Docker image with a command-line entrypoint
-------------------------------------------

The entrypoint to the Docker image supports the same command-line interface described above.

For example, the following command could be used to use the Docker image to execute the same simulations described in ``./modeling-study.omex`` and save their results to ``./``:

.. code-block:: text

    docker run \
        --tty \
        --rm \
        --mount type=bind,source="$(pwd),target=/tmp/working-dir \
        ghcr.io/biosimulators/xpp:latest \
            -i /tmp/working-dir/modeling-study.omex \
            -o /tmp/working-dir
