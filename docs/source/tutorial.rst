Tutorial and introduction to :mod:`floodestimation`
===================================================

Installation and requirements
-----------------------------

The :mod:`floodestimation` package will be available (TODO!) on the Python Package Index (PyPI) website. Installation would be
straightforward and is typically done like this from a shell prompt:

.. code-block:: shell

    pip install floodestimation

On Windows `pip` is typically installed under `C:\\Program Files\\Python33\\Scripts\\pip.exe` or somewhere similar.

In case of downloading the package manually, the following other packages are required and must be availabe:

- `appdirs`
- `sqlalchemy`

The :mod:`floodestimation` package has been tested with Python 3.2 to 3.4.

Typical workflow
----------------

A typical workflow for using the :mod:`floodestimation` package is as follows:

1. Start with an *ungauged* catchment with catchment details in a `CD3`-file, e.g. `River Dee.CD3`
2. Load the catchment
3. Estimate the median annual flood (QMED)
4. Estimate the flood growth curve
5. Estimate the flood frequency curve
6. Create an analysis report

Estimating QMED
~~~~~~~~~~~~~~~

Steps 1 to 3 could be coded as follows:

.. code-block:: python

    from floodestimation.loaders import load_catchment
    from floodestimation import db
    from floodestimation.collections import CatchmentCollections
    from floodestimation.analysis import QmedAnalysis

    db_session = db.Session()

    dee_catchment = load_catchment('River Dee.CD3')
    gauged_catchments = CatchmentCollections(db_session)

    qmed_analysis = QmedAnalysis(dee_catchment, gauged_catchments)
    dee_catchment_qmed = qmed_analysis.qmed()

    db_session.close()

Explained step by step:

.. code-block:: python

    db_session = db.Session()

This creates a connection with a sqlite database which will hold data on gauged catchments (catchment descriptors and
annual maximum flow data). The `Session object <http://docs.sqlalchemy.org/en/rel_0_9/orm/session.html>`_ can be re-used
throughout the program.

.. code-block:: python

    dee_catchment = load_catchment('River Dee.CD3')

This loads the catchment from the `.CD3` file as an :class:`floodestimation.entities.Catchment` object. See the
`reference manual <entities.html>`_ for a detailed description of all object attributes.

.. code-block:: python

    gauged_catchments = CatchmentCollections(db_session)

This creates a :class:`floodestimation.collections.CatchmentCollections` object for quick access to gauged catchment
data stored in the database. The **first time**, when the database is still empty, the data will be automatically
downloaded from the `National River Flow Archive website <http://www.ceh.ac.uk/data/nrfa/peakflow_overview.html>`_. This
might take a little while.

.. code-block:: python

    analysis = QmedAnalysis(dee_catchment, gauged_catchments)
    dee_catchment_qmed = qmed_analysis.qmed()

The :class:`floodestimation.analysis.QmedAnalysis` object provides a comprehensive set of methods to estimate QMED. The
library will automatically identify the best method based on which data is available when calling :meth:`qmed()` without
arguments. The following methods are available:

- Using annual maximum flow records (for gauged catchments)
- Using the Flood Estimation Handbook regression method (`science report SC050050
  <https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/291096/scho0608boff-e-e.pdf>`_) based on
  catchment descriptors and further correction using nearby donor stations (if the gauged catchments
  collection is supplied)
- Emperical estimate using catchment surface area only
- Emperical estimated using the river channel width only

See the `reference manual <analysis.html>`_ for a detailed description how to use the different methods.

Estimating the flood frequency curve
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Step 4 and 5 can be done like this:

.. code-block:: python

    # continue from script above but keep database session open
    # db_session.close()

    from floodestimation.analysis import GrowthCurveAnalysis

    gc_analysis = GrowthCurveAnalysis(dee_catchment, gauged_catchments)
    dee_growth_curve = gc_analysis.growth_curve()
    aeps = [0.5, 0.01, 0.005, 0.001]
    dee_flood_flows = dee_catchment_qmed * dee_growth_curve(aeps)

    db_session.close()