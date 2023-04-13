def process_file(filename, line_processor, meta_processor):
    with open(filename) as file:
        for line in file:
            line_processor(line.rstrip())
    return meta_processor()


def payments_per_year(f):
    if f == "A": return 1
    if f == "B": return 2
    if f == "Q": return 4
    if f == "M": return 12
    print("Unknown freq:", f)
    return 0
