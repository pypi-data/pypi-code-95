import pendulum


def give_me_time_in_iso(timestamp: float):
    return pendulum.from_timestamp(timestamp).to_iso8601_string()


def is_this_a_valid_datetime_string(alleged_date: str):
    try:
        give_me_a_timestamp_from_this_string(alleged_date)
        return True
    except ValueError:
        return False
    except Exception:
        raise


def give_me_a_timestamp_from_this_string(str_date: str):
    return pendulum.parse(str_date).timestamp()


def the_time_in_iso_now_is():
    return pendulum.now().to_iso8601_string()


def the_time_now_is() -> float:
    return pendulum.now().timestamp()


def go_back_in_time(time_to_reduce: float, seconds_to_reduce: int):
    stamp = pendulum.from_timestamp(time_to_reduce)
    return stamp.subtract(seconds=seconds_to_reduce).timestamp()


def go_forth_in_time(time_to_add: float, seconds_to_add: int):
    stamp = pendulum.from_timestamp(time_to_add)
    return stamp.add(seconds=seconds_to_add).timestamp()


def is_time_between(begin_time: float, end_time: float, check_time: float = None):
    # If check time is not given, default to current UTC time
    check_time = pendulum.from_timestamp(check_time) or pendulum.now()
    period = pendulum.period(pendulum.from_timestamp(begin_time), pendulum.from_timestamp(end_time))
    return check_time in period


def is_this_time_behind(base_time: float):
    # If check time is not given, default to current UTC time
    return pendulum.from_timestamp(base_time) < pendulum.now()


def is_this_time_ahead(base_time: float):
    # If check time is not given, default to current UTC time
    return pendulum.from_timestamp(base_time) > pendulum.now()


def countdown(base_date: float):
    return pendulum.now().diff(pendulum.from_timestamp(base_date)).in_seconds()


def countdown_for_humanoids(base_date: float):
    secs = pendulum.now().diff(pendulum.from_timestamp(base_date)).in_seconds()
    return pendulum.now().add(seconds=secs).diff_for_humans()
