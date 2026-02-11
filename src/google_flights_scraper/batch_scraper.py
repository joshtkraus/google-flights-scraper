"""Batch scraping functions for Google Flights scraper."""

import asyncio
import random
import sys

import pandas as pd

from .scraper import GoogleFlightsScraper

# Default per-task timeout (seconds) — covers full browser lifecycle
DEFAULT_TASK_TIMEOUT = 120


async def scrape_multiple(
    departure_code: str,
    departure_country: str,
    arrival_codes: list[str],
    arrival_countries: list[str],
    start_dates: list[str],
    end_dates: list[str],
    seat_classes: list[str],
    output_path: str | None = None,
    delay_seconds: float = 3.0,
    delay_jitter: float = 0.5,
    n_jobs: int = 1,
    task_timeout: int = DEFAULT_TASK_TIMEOUT,
):
    """Scrape multiple destinations with fixed dates.

    Args:
        departure_code (str): IATA code or city for departure airport
        departure_country (str): Country for departure airport
        arrival_codes (list[str]): List of IATA codes or cities for arrival airports
        arrival_countries (list[str]): List of countries (same length as arrival_codes)
        start_dates (list[str]): List of departure dates in MM/DD/YYYY format
        end_dates (list[str]): List of return dates in MM/DD/YYYY format
        seat_classes (list[str]): List of seat classes (same length as arrival_codes)
        output_path (str | None): Optional path to save CSV output
        delay_seconds (float): Base delay between searches in seconds when n_jobs=1 (default 3.0)
        delay_jitter (float): Max random ± jitter applied to delay_seconds (default 0.5).
        n_jobs (int): Number of concurrent scrapes (default 1). When >1, delay_seconds
                      is ignored and concurrency is controlled by the semaphore.
        task_timeout (int): Max seconds to wait for a single scrape before cancelling (default 120).

    Returns:
        DataFrame: Results for all destinations
    """
    # Validate Inputs
    await _validate_inputs(arrival_codes, arrival_countries, start_dates, end_dates, seat_classes)

    tasks = [
        {
            "departure_code": departure_code,
            "departure_country": departure_country,
            "arrival_code": arrival_code,
            "arrival_country": arrival_country,
            "start_date": start_date,
            "end_date": end_date,
            "seat_class": seat_class,
        }
        for arrival_code, arrival_country, start_date, end_date, seat_class in zip(
            arrival_codes, arrival_countries, start_dates, end_dates, seat_classes, strict=True
        )
    ]

    results = await _run_tasks(
        tasks,
        delay_seconds=delay_seconds,
        delay_jitter=delay_jitter,
        n_jobs=n_jobs,
        task_timeout=task_timeout,
    )

    df = pd.DataFrame(results)

    if "price_relativity" in df.columns:
        df = df.sort_values("price_relativity", ascending=False, na_position="last")

    if output_path:
        df.to_csv(output_path, index=False)

    return df


async def _validate_inputs(
    arrival_codes: list[str],
    arrival_countries: list[str],
    start_dates: list[str],
    end_dates: list[str],
    seat_classes: list[str],
):
    """Validate batch scraper inputs.

    Args:
        arrival_codes (list[str]): List of IATA codes or cities for arrival airports
        arrival_countries (list[str]): List of countries (same length as arrival_codes)
        start_dates (list[str]): List of departure dates in MM/DD/YYYY format
        end_dates (list[str]): List of return dates in MM/DD/YYYY format
        seat_classes (list[str]): List of seat classes (same length as arrival_codes)

    Raises:
        ValueError: If inputs are not the same length
    """
    if len(arrival_codes) != len(arrival_countries):
        raise ValueError("arrival_codes and arrival_countries must have same length")

    if len(arrival_codes) != len(start_dates):
        raise ValueError("arrival_codes and start_dates must have same length")

    if len(arrival_codes) != len(end_dates):
        raise ValueError("arrival_codes and end_dates must have same length")

    if len(arrival_codes) != len(seat_classes):
        raise ValueError("arrival_codes and seat_classes must have same length")


async def _run_tasks(
    tasks: list[dict],
    delay_seconds: float,
    delay_jitter: float,
    n_jobs: int,
    task_timeout: int,
):
    """Run scraping tasks either sequentially or concurrently.

    Args:
        tasks (list[dict]): List of task parameter dicts
        delay_seconds (float): Base delay between sequential runs
        delay_jitter (float): Max ± random jitter on delay
        n_jobs (int): Number of concurrent scrapes
        task_timeout (int): Max seconds per task before cancelling

    Returns:
        list[dict]: Flattened results for each task
    """
    if n_jobs == 1:
        return await _run_sequential(tasks, delay_seconds, delay_jitter, task_timeout)
    else:
        return await _run_concurrent(tasks, n_jobs, task_timeout)


async def _run_sequential(
    tasks: list[dict],
    delay_seconds: float,
    delay_jitter: float,
    task_timeout: int,
):
    """Run tasks one at a time with a randomized delay between each.

    Args:
        tasks (list[dict]): List of task parameter dicts
        delay_seconds (float): Base delay in seconds between tasks
        delay_jitter (float): Max ± random jitter on delay. Actual delay is
                              uniform in [delay_seconds - jitter, delay_seconds + jitter],
                              clamped to a minimum of 0.
        task_timeout (int): Max seconds per task before cancelling

    Returns:
        list[dict]: Flattened results
    """
    results = []
    total = len(tasks)

    for i, task in enumerate(tasks, 1):
        result = await _scrape_task_with_timeout(task, task_timeout)
        results.append(result)

        if i < total and delay_seconds > 0:
            jitter = random.uniform(-delay_jitter, delay_jitter)
            actual_delay = max(0.0, delay_seconds + jitter)
            await asyncio.sleep(actual_delay)

    return results


async def _run_concurrent(tasks: list[dict], n_jobs: int, task_timeout: int):
    """Run tasks concurrently up to n_jobs at a time, with per-task jitter on start.

    Each task sleeps a small random duration before acquiring the semaphore to
    stagger the initial burst and avoid all workers hitting the server simultaneously.

    Args:
        tasks (list[dict]): List of task parameter dicts
        n_jobs (int): Maximum number of concurrent scrapes
        task_timeout (int): Max seconds per task before cancelling

    Returns:
        list[dict]: Flattened results (in original task order)
    """
    semaphore = asyncio.Semaphore(n_jobs)

    async def scrape_with_jitter_and_semaphore(task: dict):
        # Stagger start times across [0, 2s] before competing for semaphore
        await asyncio.sleep(random.uniform(0, 2.0))
        async with semaphore:
            return await _scrape_task_with_timeout(task, task_timeout)

    return await asyncio.gather(*[scrape_with_jitter_and_semaphore(task) for task in tasks])


async def _scrape_task_with_timeout(task: dict, task_timeout: int):
    """Wrap _scrape_task with a hard per-task timeout.

    If the task exceeds task_timeout seconds, it is cancelled and returns
    an error result rather than blocking the semaphore slot indefinitely.

    Args:
        task (dict): Task parameters
        task_timeout (int): Max seconds to allow before cancelling

    Returns:
        dict: Flattened result dict, with error status if timed out
    """
    # Copy so pop() in _scrape_task doesn't mutate the original
    task_copy = task.copy()

    try:
        return await asyncio.wait_for(_scrape_task(task_copy), timeout=task_timeout)
    except asyncio.TimeoutError:
        print(
            f"  Task timed out after {task_timeout}s: "
            f"{task.get('departure_code')} → {task.get('arrival_code')} "
            f"({task.get('start_date')} - {task.get('end_date')})",
            file=sys.stderr,
        )
        return {
            "departure_airport": task.get("departure_code"),
            "departure_country": task.get("departure_country"),
            "arrival_airport": task.get("arrival_code"),
            "arrival_country": task.get("arrival_country"),
            "departure_date": task.get("start_date"),
            "return_date": task.get("end_date"),
            "seat_class": task.get("seat_class"),
            "status": f"Error: Task timed out after {task_timeout}s",
            "price": None,
        }


async def _scrape_task(task: dict):
    """Execute a single scrape task and return flattened result.

    Args:
        task (dict): Task parameters including optional trip_length key

    Returns:
        dict: Flattened result dict
    """
    trip_length = task.pop("trip_length", None)

    try:
        scraper = GoogleFlightsScraper()
        result = await scraper.scrape_flight(**task)
        flat_result = _flatten_result(result)
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        flat_result = {
            "departure_airport": task.get("departure_code"),
            "departure_country": task.get("departure_country"),
            "arrival_airport": task.get("arrival_code"),
            "arrival_country": task.get("arrival_country"),
            "departure_date": task.get("start_date"),
            "return_date": task.get("end_date"),
            "seat_class": task.get("seat_class"),
            "status": f"Error: {str(e)}",
            "price": None,
        }

    if trip_length is not None:
        flat_result["trip_length_days"] = trip_length

    return flat_result


def _flatten_result(result: dict) -> dict:
    """Flatten nested result dictionary for CSV export.

    Args:
        result (dict): Result dictionary from scraper

    Returns:
        dict: Flattened dictionary
    """
    flat = {}

    if "inputs" in result:
        for key, value in result["inputs"].items():
            flat[key] = value

    if "departure_flight" in result:
        for key, value in result["departure_flight"].items():
            flat[f"departure_{key}"] = value

    if "return_flight" in result:
        for key, value in result["return_flight"].items():
            flat[f"return_{key}"] = value

    flat["price"] = result.get("price")
    flat["price_classification"] = result.get("price_classification")
    flat["price_difference"] = result.get("price_difference")
    flat["price_relativity"] = result.get("price_relativity")
    flat["status"] = result.get("status")
    flat["url"] = result.get("url")

    return flat
