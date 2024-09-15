from __future__ import annotations

import contextlib
import functools
import threading
import warnings
import weakref
from typing import Callable, Generator, Hashable, TypeAlias, TypeVar

__all__ = ["ReentrantRWLock", "ThreadSafeSingeltonCache"]


def deprecated(message: str | None = None):
    def inner(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used."""
        # https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter
            warnings.warn(
                message if message else "Call to deprecated function {}.".format(func.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)  # reset filter
            return func(*args, **kwargs)

        return new_func

    return inner


class ReentrantRWLock:
    """This class implements reentrant read-write lock objects.

    A read-write lock can be aquired in read mode or in write mode or both.
    Many different readers are allowed while no thread holds the write lock.
    While a writer holds the write lock, no other threads, aside from the writer,
    may hold the read or the write lock.

    A thread may upgrade the lock to write mode while already holding the read lock.
    Similarly, a thread already having write access may aquire the read lock
    (or may already have it), to retain read access when releasing the write lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock (read or write), the same thread may acquire it
    again without blocking any number of times;
    the thread must release each lock (read/write) the same number of times it has acquired it!

    The lock provides contextmanagers in the form of `for_read()` and `for_write()`,
    which automatically aquire and release the corresponding lock, e.g.,
    >>> with lock.for_read():  # get read access until end of context
    >>>     ...
    >>>     with lock.for_write():  # upgrade to write access until end of inner
    >>>         ...
    """

    def __init__(self) -> None:
        self._writer: int | None = None  # current writer
        self._writer_count: int = 0  # number of times writer holding write lock
        # set of current readers mapping to number of times holding read lock
        # entry is missing if not holding the read lock (no 0 values)
        self._readers: dict[int, int] = dict()
        # main lock + condition, is used for:
        # * protecting read/write access to _writer, _writer_times and _readers
        # * is actively held when having write access (so no other thread has access)
        # * future writers can wait() on the lock to be notified once nobody is reading/writing anymore
        self._lock = threading.Condition(threading.RLock())  # reentrant

    @contextlib.contextmanager
    def for_read(self) -> Generator[ReentrantRWLock, None, None]:
        """
        used for 'with' block, e.g., with lock.for_read(): ...
        """
        try:
            self.acquire_read()
            yield self
        finally:
            self.release_read()

    @contextlib.contextmanager
    def for_write(self) -> Generator[ReentrantRWLock, None, None]:
        """
        used for 'with' block, e.g., with lock.for_write(): ...
        """
        try:
            self.acquire_write()
            yield self
        finally:
            self.release_write()

    def acquire_read(self) -> None:
        """
        Acquire one read lock. Blocks only if a another thread has acquired the write lock.
        """
        ident: int = threading.current_thread().ident  # type: ignore
        with self._lock:
            self._readers[ident] = self._readers.get(ident, 0) + 1

    def release_read(self) -> None:
        """
        Release one currently held read lock from this thread.
        """
        ident: int = threading.current_thread().ident  # type: ignore
        with self._lock:
            if ident not in self._readers:
                raise RuntimeError(
                    f"Read lock was released while not holding it by thread {ident}"
                )
            if self._readers[ident] == 1:
                del self._readers[ident]
            else:
                self._readers[ident] -= 1
            if not self._readers:  # if no other readers remain
                self._lock.notify()  # wake the next writer if any

    def acquire_write(self) -> None:
        """
        Acquire one write lock. Blocks until there are no acquired read or write locks from other threads.
        """
        ident: int = threading.current_thread().ident  # type: ignore
        self._lock.acquire()  # is reentrant, so current writer can aquire again
        if self._writer == ident:
            self._writer_count += 1
            return

        # do not be reader while waiting for write or notify will not be called
        times_reading = self._readers.pop(ident, 0)
        while len(self._readers) > 0:
            self._lock.wait()
        self._writer = ident
        self._writer_count += 1
        if times_reading:
            # restore number of read locks thread originally had
            self._readers[ident] = times_reading

    def release_write(self) -> None:
        """
        Release one currently held write lock from this thread.
        """
        if self._writer != threading.current_thread().ident:
            raise RuntimeError(
                f"Write lock was released while not holding it by thread {threading.current_thread().ident}"
            )
        self._writer_count -= 1
        if self._writer_count == 0:
            self._writer = None
            self._lock.notify()  # wake the next writer if any
        self._lock.release()


Key: TypeAlias = Hashable
Value = TypeVar("Value")


class ThreadSafeSingeltonCache:
    """This is a thread safe dictionary intended to be used as a cache.
    Using the :func:`get_or_create` function guarantees that every object returned
    for a given key is a singleton across all threads.
    Objects that are not in the cache will be created using factory or otherwise default_factory initially.
    When ``use_weakref = True``, then the values can be deleted by the Python garbage collector (GC) only if
    no other references, aside from this cache, exist to the object.
    Otherwise, ``use_weakref = False``, the keys are cached for the entire runtime of the program.

    .. note::

       Ideally only the get_or_create function should be used to fill the cache, as this function will create the objects initially and return them in a thread safe way.

    .. note::

       Preferably values should not be set directly or deleted, as that might violate the singleton invariant in some way. Only do that if you are sure what you are doing.
    """

    def __init__(
        self, default_factory: Callable[[Key], Value] | None, use_weakref: bool = False
    ) -> None:
        self._default_factory = default_factory
        # lock must be reentrant, could deadlock otherwise (if constructing Impl in __init__ of Impl)
        self._lock = ReentrantRWLock()
        self._cache: dict[Key, Value] = weakref.WeakValueDictionary() if use_weakref else dict()

    @property
    def uses_weakref(self) -> bool:
        return isinstance(self._cache, weakref.WeakValueDictionary)

    def __bool__(self) -> bool:
        with self._lock.for_read():
            return bool(self._cache)

    def __len__(self) -> int:
        with self._lock.for_read():
            return len(self._cache)

    def __getitem__(self, key: Key) -> Value:
        with self._lock.for_read():
            return self._cache[key]

    def __setitem__(self, key: Key, item: Value) -> None:
        """Prefer using the :func:`get_or_create` function for creating items."""
        with self._lock.for_write():
            self._cache[key] = item

    def __delitem__(self, key: Key) -> None:
        """Use with care! Once an object is deleted from the cache a new one might be created (might not be singleton anymore)"""
        with self._lock.for_write():
            del self._cache[key]

    def get(self, key: Key, default=None) -> Value | None:
        """Return the value for `key` if `key` is in the cache, else `default`.
        If `default` is not given, it defaults to None, so that this method never raises a KeyError.
        This function does not create a new value in cache.
        If the function returns with default value, there is no guarantee that the entry has not
        been created in the mean time! Do NOT set the value manually after checking with get, use :func:`get_or_create` instead!

        :return: the value assosiated with `key` or `default` if it does not exist
        :rtype: Value | None
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_or_create(self, key: Key, factory: Callable[[Key], Value] | None = None) -> Value:
        """Return singleton value for `key` or create value with `factory` (or otherwise `default_factory`) otherwise.
        Guarantees that a value with given key is a singleton in the entire program, even across multiple threads.

        :return: the value assosiated with `key`, newly created if it did not exist
        :rtype: Value
        """
        _sentinel = object()  # do not use None, as None could be a legit value in cache
        strong_ref = self.get(key, _sentinel)
        if strong_ref is _sentinel:
            with self._lock.for_write():
                # must check again as entry could have been created while waiting for write lock (race condition)
                strong_ref = self.get(key, _sentinel)
                if strong_ref is _sentinel:
                    # now we can be sure nobody will create entry with key because we have write lock
                    if factory is not None:
                        strong_ref = factory(key)
                    elif self._default_factory is None:
                        raise RuntimeError(
                            "Neither `factory` nor `default_factory` were set, entry could not be created"
                        )
                    else:
                        strong_ref = self._default_factory(key)
                    self._cache[key] = strong_ref
        return strong_ref

    def keys(self) -> tuple[Key]:
        """Returns a tuple of all keys which currently exist.
        Changes that happen to the cache after this function returns are not reflected in the tuple.

        .. warning::

        In case ``uses_weakref == True`` no guarantee is given that when this function returns
        the returned keys actually exist.

        :return: a tuple of keys that currently exist
        :rtype: tuple[Key]
        """
        with self._lock.for_read():
            return tuple(self._cache.keys())

    def values(self) -> tuple[Value]:
        """Returns a tuple of all values which currently exist.

        :return: a tuple of values that currently exist
        :rtype: tuple[Value]
        """
        with self._lock.for_read():
            return tuple(self._cache.values())

    def items(self) -> tuple[tuple[Key, Value]]:
        """Returns a tuple of all key value pairs which currently exist.

        :return: a tuple of key value pairs that currently exist
        :rtype: tuple[tuple[Key, Value]]
        """
        with self._lock.for_read():
            return tuple(self._cache.items())

    def clear(self) -> None:
        """Clears the cache.
        Should probably not be used again afterwards, as the newly created values might not be singletons anymore,
        e.g., other threads could still hold references to old objects.
        """
        with self._lock.for_write():
            self._cache.clear()
