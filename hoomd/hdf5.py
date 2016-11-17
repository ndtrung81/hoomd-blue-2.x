# Copyright (c) 2009-2016 The Regents of the University of Michigan
# This file is part of the HOOMD-blue project, released under the BSD 3-Clause License.

R""" Commands that require the h5py package at runtime.

All commands that are part of this module require the hdf5 pacakge. In
addition, this module is an opt-in. As a consequence you'll need to
import it via `import hoomd.hdf5` before you can use any command.

"""
from hoomd import _hoomd
from hoomd.analyze import _analyzer
import hoomd
import numpy
import os

try:
    import h5py
except ImportError as error:
    h5py_userwarning = "The current runtime does not support the h5py module."
    h5py_userwarning += " Using the log_hdf5 is not possible."
    hoomd.context.msg.error(h5py_userwarning)
    raise error

class log(hoomd.analyze._analyzer):
    R""" Log a number of calculated quantities or matrices to a hdf5 file.

    Args:
        filename(str): File to log the data
        period(int):  Quantities are loggged every *period* time steps
        quantities(list): Single value quantities to log.
        matriy_quantities(list): Matrix quantities to log.
        overwrite(bool): When False (the default) the existing log will be append. When True the file will be overwritten.
        phase(int): When -1, start on the current time step. When >= 0 execute on steps where *(step +phase) % period == 0*.

    For details on the loggable single values refer :py:class:`hoomd.analyze.log` for details.

    The single values are combined in a single array 'single_values' in the hdf5 file.
    The attributes list all the names of the logged quantities and there position in the file.

    Matrix quantities are logged as a separate data set each in the file. The name of the data set
    corresponds to the name of the quantity. The first dimension of the data set is counting the
    logged time step. The other dimension correspond to the dimensions of the logged matrix.

    Note:
        The number and order of single value logs cannot change compared to data which is already
        stored in the hdf5 file. As a result, if you append to a file make sure you are logging the
        same values as before. In addition, also during a run with multiple `hoomd.run()` commands
        the logged values can not change.
    Note:
        The dimensions of logged matrix quantities cannot change compared to a matrix with same name
        stored in the file. This applies for appending files as well as during a single simulation
        run.

    Examples::

            log = hoomd.hdf5.log(filename='log.h5', quantities=['my_quantity', 'cosm'],matrix_quantities = ['random_matrix'], period=100)
            log.register_callback('my_quantity', lambda timestep: timestep**2)
            log.register_callback('cosm', lambda timestep: math.cos(logger.query('my_quantity')))
            def random_matrix(timestep):
                return numpy.random.rand(23,56)
            log.register_callback('random_matrix',random_matrix,True)

    """
    def __init__(self, filename, period, quantities=[],matrix_quantities=[], overwrite=False, phase=0):
        hoomd.util.print_status_line()

        # store metadata
        self.metadata_fields = ['filename','period']
        self.filename = filename
        self.period = period

        if overwrite:
            try:
                os.remove(filename)
            except OSError:
                pass

        # initialize base class
        _analyzer.__init__(self)

        # create the c++ mirror class
        self.cpp_analyzer = _hoomd.LogHDF5(hoomd.context.current.system_definition, self._write_hdf5)
        self.setupAnalyzer(period, phase);

        # set the logged quantities
        hoomd.util.quiet_status()
        self.set_params(quantities=quantities,matrix_quantities=matrix_quantities)
        hoomd.util.unquiet_status()

        # set the logged matrix quantities
        matrix_quantity_list = _hoomd.std_vector_string();
        for item in matrix_quantities:
            matrix_quantity_list.append(str(item));
        self.cpp_analyzer.setLoggedMatrixQuantities(matrix_quantity_list);


        # add the logger to the list of loggers
        hoomd.context.current.loggers.append(self);

    def set_params(self, quantities=None, matrix_quantities=None):
        R""" Change the parameters of the log.

        Warning:
           Do not change the number or order of logged single quantities compared to values stored in the file.
        """
        hoomd.util.print_status_line();

        if quantities is not None:
            # set the logged quantities
            quantity_list = _hoomd.std_vector_string();
            for item in quantities:
                quantity_list.append(str(item));
            self.cpp_analyzer.setLoggedQuantities(quantity_list);

        if matrix_quantities is not None:
            # set the logged quantities
            matrix_quantity_list = _hoomd.std_vector_string();
            for item in matrix_quantities:
                matrix_quantity_list.append(str(item));
            self.cpp_analyzer.setLoggedMatrixQuantities(matrix_quantity_list);


    def query(self, quantity,matrix=False):
        R""" Get the current value of a logged quantity.

        Note:
            Matrix quantities are not cached by the class, so calling this function multiple time,
            may not be efficient.
        """
        use_cache=True # Log hdf5 does not support init w/o filename
        timestep = hoomd.context.current.system.getCurrentTimeStep()

        if not matrix:
            return self.cpp_analyzer.getQuantity(quantity, timestep, use_cache);
        else:
            return self.cpp_analyzer.getMatrixQuantity(quantity, timestep, use_cache)

    def register_callback(self, name, callback,matrix=False):
        R""" Register a callback to produce a logged quantity.

        Args:
            name (str): Name of the quantity
            callback (callable): A python callable object (i.e. a lambda, function, or class that implements __call__)
            matrix (bool): Is the callback a computing a numpy array matrix?

        The callback method must take a single argument, the current
        timestep, and return a single floating point value to be
        logged. If the callback returns a matrix quantity the return
        value must be a numpy array constant dimensions of each call.

        Note:
            One callback can query the value of another, but logged quantities are evaluated in order from left to right.

        Examples::

            log = hoomd.hdf5.log(filename='log.h5', quantities=['my_quantity', 'cosm'],matrix_quantities = ['random_matrix'], period=100)
            log.register_callback('my_quantity', lambda timestep: timestep**2)
            log.register_callback('cosm', lambda timestep: math.cos(logger.query('my_quantity')))
            def random_matrix(timestep):
                return numpy.random.rand(23,56)
            log.register_callback('random_matrix',random_matrix,True)

        """
        if not matrix:
            self.cpp_analyzer.registerCallback(name, callback);
        else:
            self.cpp_analyzer.registerMatrixCallback(name, callback);


    ## \internal
    # \brief Re-registers all computes and updaters with the logger
    def update_quantities(self):

        # remove all registered quantities
        self.cpp_analyzer.removeAll();

        # re-register all computes and updater
        hoomd.context.current.system.registerLogger(self.cpp_analyzer);

    def disable(self):
        R""" Disable the logger.

        Examples::

            logger.disable()


        Executing the disable command will remove the logger from the system.
        Any :py:func:`hoomd.run()` command executed after disabling the logger will not use that
        logger during the simulation. A disabled logger can be re-enabled
        with :py:meth:`enable()`.
        """
        hoomd.util.quiet_status()
        _analyzer.disable(self)
        hoomd.util.unquiet_status()

        hoomd.context.current.loggers.remove(self)

    def enable(self):
        R""" Enables the logger

        Examples::

            logger.enable()

        See :py:meth:`disable()`.
        """

        hoomd.util.quiet_status()
        _analyzer.enable(self)
        hoomd.util.unquiet_status()

        hoomd.context.current.loggers.append(self)

    ## \internal
    # \brief Writes all C++ side prepare data to hdf5 file.
    def _write_hdf5(self,timestep):

        f = None
        if hoomd.comm.get_rank() == 0:
            f = h5py.File(self.filename,"a")

        self._write_single_values(f,timestep)
        self._write_matrix_values(f,timestep)

        if f is not None:
            f.close()

        return timestep

    ## \internal
    # \brief Writes the single values of the logger as a single array to the hdf5 file.
    def _write_single_values(self,f,timestep):
        #Everything is MPI collective, except writing.
        # prepare and check file for single values
        self._write_header(f)
        new_array = self.cpp_analyzer.get_single_value_array()
        if f is not None: # Handle single values only on root.
            data_set = f["/single_values"]
            old_size = data_set.shape[0]

            if data_set.shape[1] != new_array.shape[0]:
                hoomd.context.msg.error("The number of logged single quantities does not match"
                                        " with the number of quantities stored in the file.")
                raise RuntimeError("Error write single values with log_hdf5.")

            data_set.resize(old_size+1,axis=0)
            data_set[old_size,] = new_array

    ## \internal
    # \brief Writes the logged matrix quantities to file
    def _write_matrix_values(self,f,timestep):
        matrix_quantities = self.cpp_analyzer.getLoggedMatrixQuantities()

        for q in matrix_quantities:
            #Obtain the numpy arrray from cpp class.
            try:
                #This is called on every rank, but only root rank returns "correct data"
                new_matrix = self.cpp_analyzer.getMatrixQuantity(q,timestep)
            except:
                hoomd.context.msg.error("For quantity "+q+" no python type obtainable.")
                raise RuntimeError("Error writing matrix quantity "+q)

            if f != None: #Only the root rank further process the recieved data

                #Check the returned object
                if type(new_matrix) != numpy.ndarray :
                    hoomd.context.msg.error("For quantity "+q+" no matrix obtainable.")
                    raise RuntimeError("Error writing matrix quantity "+q)
                zero_shape = True
                for dim in new_matrix.shape:
                    if dim != 0:
                        zero_shape = False
                if zero_shape:
                    hoomd.context.msg.error("For quantity "+q+" matrix with zero shape obtained.")
                    raise RuntimeError("Error writing matrix quantity "+q)

                if not q in f:
                    #Create a new container in hdf5 file, if not already existing.
                    data_set = f.create_dataset(q,shape=(0,)+new_matrix.shape,maxshape=(None,)+new_matrix.shape)
                else:
                    data_set = f[q]

                    #check compatibility of data in file and returned matrix
                    if len(new_matrix.shape) +1 != len(data_set.shape):
                        msg = "Trying to log matrix "+q+", but dimensions are incompatible with "
                        msg += "dimensions in file."
                        hoomd.context.msg.error(msg)
                        raise RuntimeError("Error writing matrix quntity "+q)

                    for i in range(len(new_matrix.shape)):
                        if data_set.shape[i+1] != new_matrix.shape[i]:
                            msg = "Trying to log matrix "+q+", but dimension "+str(i)+" is "
                            msg += "incompatible with  dimension in file."
                            hoomd.context.msg.error(msg)
                            raise RuntimeError("Error writing matrix quantity "+q)

                old_size = data_set.shape[0]

                data_set.resize(old_size+1,axis=0)
                data_set[old_size,] = new_matrix


    ## \internal
    # \brief prepare and check the hdf5 file for single value dump
    def _write_header(self,f):

        quantities = self.cpp_analyzer.getLoggedQuantities()

        if f is not None:
            if "single_values" in f:
                data_set = f["single_values"]
                if  data_set.shape[1] != len(quantities):
                    if data_set.shape[0] == 0:
                        data_set.resize( (0,len(quantities)) )
                        for key in data_set.attrs.keys():
                            del data_set.attrs[key]
                    else:
                        hoomd.context.msg.error("Changing the number of logged quantites is impossible"
                                        " if there are already logged quantities.")
                        raise RuntimeError("Error updating quantities with log_hdf5.")
            else:
                data_set = f.create_dataset("single_values",shape=(0,len(quantities)),maxshape=(None,len(quantities)) )

            #Ensure quantities in the attribute match with new setting.
            for i in range(len(quantities)):
                try:
                    if i != data_set.attrs[quantities[i]]:
                        hoomd.context.msg.error("Quantity "+quantities[i]+" is not stored in the correct position."
                                                " stored: "+str(data_set.attrs[quantities[i]])+" new: "+str(i))
                        raise RuntimeError("Error updating quantities with log_hdf5.")
                except KeyError:
                    for key in data_set.attrs.keys():
                        if data_set.attrs[key] == i:
                            hoomd.context.msg.error("Quantity position is not vacant.")
                            raise RuntimeError("Error updating quantities with log_hdf5.")
                    data_set.attrs[quantities[i]] = i
