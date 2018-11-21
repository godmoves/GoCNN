import os

input_dir = "./tests/raw/"
output_dir = "./tests/input/"
completed_dir = "./tests/gnugo/"
board_size = 9
ownership = True


def rm_test_files(path, suffix):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(suffix):
                os.remove(filepath)
