import json
import os
import argparse
from tiff_file.tiff_file import TiffFile
from utils import InvalidTIFFileException
import pandas as pd

TIFFS_CSV = "tiffs.csv"


def recognize_tiff(input_file):
    """
        TODO: Add docs
    """
    tiff = TiffFile(input_file)
    tiff_dict = {'name': os.path.basename(input_file.name),
                 'magic': tiff.magic,
                 'number_of_ifds': tiff.count_image_file_dirs(),
                 'count_baseline_tags': tiff.count_baseline_tags(),
                 'count_extension_tags': tiff.count_extension_tags(),
                 'count_private_tags': tiff.count_private_tags(),
                 'count_unknown_tags': tiff.count_unknown_tags(),
                 'image_count': tiff.count_images(),
                 'image_percentage': tiff.get_image_percentage() / os.fstat(input_file.fileno()).st_size,
                 'count_dangerous_fields': len(tiff.get_features(input_file)),
                 'count_valid_ifd_offsets': tiff.check_ifd_offsets(input_file),
                 'is_malware': 0,
                }

    baseline_tags = json.load(open("C:\\Users\\itayro\\PycharmProjects\\MTFD\\baseline_tags.json", "r"))
    extension_tags = json.load(open("C:\\Users\\itayro\\PycharmProjects\\MTFD\\extension_tags.json", "r"))
    private_tags = json.load(open("C:\\Users\\itayro\\PycharmProjects\\MTFD\\private_tags.json", "r"))

    tiff_tags_dict = {}

    for single_tag in baseline_tags + extension_tags + private_tags:
        tiff_tags_dict[single_tag['name']] = 0

    for tiff_tag in tiff.get_tags():
        if tiff_tag in [base_tag['name'] for base_tag in baseline_tags]:
            tiff_tags_dict[tiff_tag] = tiff_tags_dict.get(tiff_tag, 0) + 1
        if tiff_tag in [base_tag['name'] for base_tag in extension_tags]:
            tiff_tags_dict[tiff_tag] = tiff_tags_dict.get(tiff_tag, 0) + 1
        if tiff_tag in [base_tag['name'] for base_tag in private_tags]:
            tiff_tags_dict[tiff_tag] = tiff_tags_dict.get(tiff_tag, 0) + 1


#    print("unkown:")
#    print([tag if tag not in [iter_tag['name'] for iter_tag in all_tags] else '' for tag in tiff.get_tags()])

    tiff_dict.update(tiff_tags_dict)

    return tiff_dict


def main():
    arg_parser = argparse.ArgumentParser(description="A TIFF file parser")
    arg_parser.add_argument("-i", dest="input_file", type=argparse.FileType('rb'),
                            help="The input TIFF file", default=None)
    arg_parser.add_argument("-d", dest="input_dir", type=str,
                            help="The input directory that contains TIFF files", default=None)

    args = arg_parser.parse_args()
    tiffs = []
    invalid_tiffs = []
    if args.input_file is not None:
        tiffs.append(recognize_tiff(args.input_file))
    elif args.input_dir is not None:
        tiffs = []
        for subdir, dirs, files in os.walk(args.input_dir):
            for filename in files:
                with open(os.path.join(subdir, filename), 'rb') as file_object:
                    print(filename)
                    try:
                        tiffs.append(recognize_tiff(file_object))
                    except InvalidTIFFileException:
                        invalid_tiffs.append(filename)

        df = pd.DataFrame(tiffs)
        df.to_csv('tiffs.csv', index=False)
    else:
        raise Exception('No input was provided.')

    with open("invalid_tiffs.txt", "w") as invalids_file:
        invalids_file.write('\n'.join(invalid_tiffs))


if __name__ == "__main__":
    main()
