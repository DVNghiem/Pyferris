use pyo3::create_exception;

create_exception!(
    _pyferris,
    ParallelExecutionError,
    pyo3::exceptions::PyException
);

create_exception!(
    _pyferris,
    JsonParsingError,
    pyo3::exceptions::PyException
);

create_exception!(
    _pyferris,
    FileReaderError,
    pyo3::exceptions::PyException
);


create_exception!(
    _pyferris,
    FileWriterError,
    pyo3::exceptions::PyException
);

create_exception!(
    _pyferris,
    FolderCreationError,
    pyo3::exceptions::PyException
);