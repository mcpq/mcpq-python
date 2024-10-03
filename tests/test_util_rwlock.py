import time
from threading import Thread

import pytest

from mcpq._util import ReentrantRWLock

# Note: set timeout for these tests, in case of deadlock we want to fail the test
# Should be at least 3 * SLEEP_TIME
TIMEOUT = 1

# Some tests use sleeps to simulate possible race conditions
# Define how long this should be - test precision is dependend on this!
SLEEP_TIME = 0.01


@pytest.mark.timeout(TIMEOUT)
def test_single_threaded_upgrade():
    lock = ReentrantRWLock()

    with lock.for_read():
        with lock.for_write():
            pass
        assert lock._readers, "Released read lock incorrectly"


@pytest.mark.timeout(TIMEOUT)
def test_single_threaded_reentrant_read():
    lock = ReentrantRWLock()

    with lock.for_read():
        with lock.for_read():
            pass
        assert lock._readers, "Released read lock too early"


@pytest.mark.timeout(TIMEOUT)
def test_single_threaded_reentrant_write():
    lock = ReentrantRWLock()

    with lock.for_write():
        with lock.for_write():
            pass
        assert lock._writer is not None, "Released write lock too early"


@pytest.mark.timeout(TIMEOUT)
def test_single_threaded_read_when_write():
    lock = ReentrantRWLock()

    with lock.for_write():
        with lock.for_read():
            pass
        assert lock._writer is not None, "Released write lock incorrectly"


@pytest.mark.timeout(TIMEOUT)
def test_single_threaded_deep():
    lock = ReentrantRWLock()

    with lock.for_read():
        with lock.for_read():
            with lock.for_write():
                with lock.for_read():
                    with lock.for_write():
                        pass
        assert lock._writer is None, "Did not release write lock correctly"
        assert lock._readers, "Released read lock too early"
    assert not lock._readers, "Did not release read lock correctly"
    assert lock._writer is None, "Aquired write lock again??"


@pytest.mark.timeout(TIMEOUT)
def test_lock_no_ambiguous_context():
    lock = ReentrantRWLock()

    # TypeError in newer Python versions
    with pytest.raises((AttributeError, TypeError)):
        with lock:
            pass


@pytest.mark.timeout(TIMEOUT)
def test_lock_wrong_release():
    lock = ReentrantRWLock()

    with pytest.raises(RuntimeError):
        lock.release_read()

    with pytest.raises(RuntimeError):
        lock.release_write()


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_many_reads():
    lock = ReentrantRWLock()

    def read():
        with lock.for_read():
            time.sleep(SLEEP_TIME)

    t1 = Thread(name="read1", target=read, daemon=True)
    t2 = Thread(name="read2", target=read, daemon=True)
    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # a bit more than SLEEP_TIME, definitly less than 2 * SLEEP_TIME!
    assert delta < 1.5 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.5 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_write_exclusive():
    lock = ReentrantRWLock()

    def write():
        with lock.for_write():
            time.sleep(SLEEP_TIME)

    t1 = Thread(name="write1", target=write, daemon=True)
    t2 = Thread(name="write2", target=write, daemon=True)
    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_read_write_exclusive():
    lock = ReentrantRWLock()

    def read():
        with lock.for_read():
            time.sleep(SLEEP_TIME)

    def write():
        with lock.for_write():
            time.sleep(SLEEP_TIME)

    t1 = Thread(name="read", target=read, daemon=True)
    t2 = Thread(name="write", target=write, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_write_read_exclusive():
    lock = ReentrantRWLock()

    def read():
        with lock.for_read():
            time.sleep(SLEEP_TIME)

    def write():
        with lock.for_write():
            time.sleep(SLEEP_TIME)

    t1 = Thread(name="write", target=write, daemon=True)
    t2 = Thread(name="read", target=read, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_read_write_exclusive_direct():
    lock = ReentrantRWLock()

    def read():
        lock.acquire_read()
        time.sleep(SLEEP_TIME)
        lock.release_read()

    def write():
        lock.acquire_write()
        time.sleep(SLEEP_TIME)
        lock.release_write()

    t1 = Thread(name="read", target=read, daemon=True)
    t2 = Thread(name="write", target=write, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_write_read_exclusive_direct():
    lock = ReentrantRWLock()

    def read():
        lock.acquire_read()
        time.sleep(SLEEP_TIME)
        lock.release_read()

    def write():
        lock.acquire_write()
        time.sleep(SLEEP_TIME)
        lock.release_write()

    t1 = Thread(name="write", target=write, daemon=True)
    t2 = Thread(name="read", target=read, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_read_readwrite_exclusive():
    lock = ReentrantRWLock()

    def read():
        with lock.for_read():
            time.sleep(SLEEP_TIME)

    def write():
        with lock.for_read():
            with lock.for_write():
                time.sleep(SLEEP_TIME)

    t1 = Thread(name="read", target=read, daemon=True)
    t2 = Thread(name="readwrite", target=write, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_readwrite_read_exclusive():
    lock = ReentrantRWLock()

    def read():
        with lock.for_read():
            time.sleep(SLEEP_TIME)

    def write():
        with lock.for_read():
            with lock.for_write():
                time.sleep(SLEEP_TIME)

    t1 = Thread(name="readwrite", target=write, daemon=True)
    t2 = Thread(name="read", target=read, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_read_readwrite_exclusive_direct():
    lock = ReentrantRWLock()

    def read():
        lock.acquire_read()
        time.sleep(SLEEP_TIME)
        lock.release_read()

    def write():
        lock.acquire_read()
        lock.acquire_write()
        time.sleep(SLEEP_TIME)
        lock.release_write()
        lock.release_read()

    t1 = Thread(name="read", target=read, daemon=True)
    t2 = Thread(name="readwrite", target=write, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_readwrite_read_exclusive_direct():
    lock = ReentrantRWLock()

    def read():
        lock.acquire_read()
        time.sleep(SLEEP_TIME)
        lock.release_read()

    def write():
        lock.acquire_read()
        lock.acquire_write()
        time.sleep(SLEEP_TIME)
        lock.release_write()
        lock.release_read()

    t1 = Thread(name="readwrite", target=write, daemon=True)
    t2 = Thread(name="read", target=read, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 2 * SLEEP_TIME!
    assert delta > 1.9 * SLEEP_TIME, f"Time for both joins should be {delta=} > {1.9 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_readwrite_readwrite_exclusive():
    lock = ReentrantRWLock()

    def readwrite():
        with lock.for_read():
            time.sleep(SLEEP_TIME)
            with lock.for_write():
                time.sleep(SLEEP_TIME)

    t1 = Thread(name="readwrite1", target=readwrite, daemon=True)
    t2 = Thread(name="readwrite2", target=readwrite, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 3 * SLEEP_TIME but less than 4 * SLEEP_TIME!
    assert (
        2.9 * SLEEP_TIME < delta < 3.5 * SLEEP_TIME
    ), f"Time for both joins should be {2.9 * SLEEP_TIME} < {delta=} < {3.5 * SLEEP_TIME}"


@pytest.mark.timeout(TIMEOUT)
def test_multi_threaded_writeread_writeread_exclusive():
    lock = ReentrantRWLock()

    def writeread():
        with lock.for_write():
            time.sleep(SLEEP_TIME)
            with lock.for_read():
                time.sleep(SLEEP_TIME)

    t1 = Thread(name="writeread1", target=writeread, daemon=True)
    t2 = Thread(name="writeread2", target=writeread, daemon=True)
    start = time.perf_counter()
    t1.start()
    time.sleep(SLEEP_TIME * 0.01)
    t2.start()
    t1.join()
    t2.join()
    delta = time.perf_counter() - start
    # definitly at least 3 * SLEEP_TIME but less than 4 * SLEEP_TIME!
    assert (
        3.9 * SLEEP_TIME < delta < 4.5 * SLEEP_TIME
    ), f"Time for both joins should be {3.9 * SLEEP_TIME} < {delta=} < {4.5 * SLEEP_TIME}"
