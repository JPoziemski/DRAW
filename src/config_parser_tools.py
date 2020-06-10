from multiprocessing import cpu_count


def get_cpu_number():
    return cpu_count()
