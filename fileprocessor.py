def process_file(filename, line_processor, meta_processor):
    with open(filename) as file:
        for line in file:
            line_processor(line.rstrip())
    return meta_processor()
