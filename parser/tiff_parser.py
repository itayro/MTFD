import os
import argparse
from tiff_file.tiff_file import TiffFile


def recognize_tiff(input_file):
    """

    :param input_file: A file object of a potential TIFF file.
    :return: True if the file is of TIFF format, False otherwise.
    """

    return TiffFile(input_file)


def main():
    arg_parser = argparse.ArgumentParser(description="A TIFF file parser")
    arg_parser.add_argument("-i", dest="input_file", type=argparse.FileType('rb'),
                            help="The input TIFF file", default=None)
    arg_parser.add_argument("-d", dest="input_dir", type=str,
                            help="The input directory that contains TIFF files", default=None)

    args = arg_parser.parse_args()
    tiffs = []

    if args.input_file is not None:
        tiffs.append(recognize_tiff(args.input_file))
    elif args.input_dir is not None:
        tiffs = []
        for subdir, dirs, files in os.walk(args.input_dir):
            for filename in files:
                with open(os.path.join(subdir, filename), 'rb') as file_object:
                    print(filename)
                    tiffs.append(recognize_tiff(file_object))
    else:
        raise Exception('No input was provided.')

    for tiff in tiffs:
        print(tiff.get_tags())


if __name__ == "__main__":
    main()
