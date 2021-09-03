import os
import struct
from functools import reduce

from tiff_file.ifd import IFD_OFFSET_IN_BYTES, TiffIFD
from utils import InvalidTIFFileException

IMAGE_FILE_HEADER_LITTLE_ENDIAN = b'II'
IMAGE_FILE_HEADER_BIG_ENDIAN = b'MM'

IMAGE_FILE_HEADER_SIZE_IN_BYTES = 2
MAGIC_NUMBER_SIZE_IN_BYTES = 2


class TiffFile:

    def __init__(self, file_object):

        # Reset file object location
        file_object.seek(0)

        potential_file_header = file_object.read(IMAGE_FILE_HEADER_SIZE_IN_BYTES)
        # Check that the image header is correct.
        if potential_file_header not in (IMAGE_FILE_HEADER_BIG_ENDIAN, IMAGE_FILE_HEADER_LITTLE_ENDIAN):
            raise InvalidTIFFileException

        # Get file size.
        self._file_size = os.fstat(file_object.fileno()).st_size

        # Set file name.
        self._file_name = file_object.name

        # Set endianness of the file.
        self._is_little_endian = potential_file_header == IMAGE_FILE_HEADER_LITTLE_ENDIAN

        # Read the magic number.
        self._magic, = struct.unpack(
            "{endianness}h".format(endianness='<' if self._is_little_endian else '>'),
            file_object.read(MAGIC_NUMBER_SIZE_IN_BYTES))

        # Read first IFD offset.
        self._first_ifd_offset, = struct.unpack(
            "{endianness}I".format(endianness='<' if self._is_little_endian else '>'),
            file_object.read(IFD_OFFSET_IN_BYTES))

        # Parse the IFDs of the file.
        self._ifd_list = []
        current_offset = self._first_ifd_offset
        while 0 != current_offset:
            # Parse IFD
            try:
                ifd = TiffIFD(self._is_little_endian, current_offset)
                self._ifd_list.append(ifd)
                current_offset = ifd.parse_ifd(file_object)
            except Exception:
                break
            # If succeeded, parse the ifd data as well.
            try:
                ifd.calculate_ifd_data(file_object)
            except Exception:
                pass

    @property
    def file_name(self):
        return self._file_name

    @property
    def magic(self):
        return self._magic

    @property
    def ifd_list(self):
        return self._ifd_list

    def count_image_file_dirs(self):
        """
            Count the number of IFDs in a single TIFF file.
        :return: number of IFDs in a single TIFF file.
        """
        return len(self._ifd_list)

    def count_baseline_tags(self):
        """
            Count the number of baseline tags in a single TIFF file.
        :return: number of baseline tags in a single TIFF file.
        """
        return reduce(lambda acc, tags_count: acc + tags_count, [ifd.count_baseline_tags() for ifd in self._ifd_list], 0)

    def count_extension_tags(self):
        """
            Count the number of extension tags in a single TIFF file.
        :return: number of extension tags in a single TIFF file.
        """
        return reduce(lambda acc, tags_count: acc + tags_count, [ifd.count_extension_tags() for ifd in self._ifd_list], 0)

    def count_private_tags(self):
        """
            Count the number of private tags in a single TIFF file.
        :return: number of private tags in a single TIFF file.
        """
        return reduce(lambda acc, tags_count: acc + tags_count, [ifd.count_private_tags() for ifd in self._ifd_list], 0)

    def count_unknown_tags(self):
        """
            Count the number of unknown tags in a single TIFF file.
        :return: number of private tags in a single TIFF file.
        """
        return reduce(lambda acc, tags_count: acc + tags_count, [ifd.count_unknown_tags() for ifd in self._ifd_list], 0)

    def get_tags(self):
        """
            Get all the tags in a single TIFF file.
        :return: A list of all the tags in a single TIFF file.
        """
        tags = []
        for ifd in self._ifd_list:
            for ifd_entry in ifd.entries:
                tags.append(ifd_entry.tag_name)
        return tags

    def count_images(self):
        count = 0
        for ifd in self._ifd_list:
            if ifd.get_image_data() is not None:
                count += 1
        return count

    def get_image_percentage(self):
        image_bytes = 0
        for ifd in self._ifd_list:
            if ifd.get_image_data() is not None:
                for strip in ifd.get_image_data():
                    image_bytes += len(strip)
        return image_bytes

    def get_features(self, file_object):
        entries = {}
        for idx, ifd in enumerate(self._ifd_list):
            ifd_entries = ifd.check_dangerous_entries(file_object)
            for ifd_entry, status in ifd_entries.items():
                if status:
                    entries[ifd_entry] = status
        return entries

    def check_ifd_offsets(self, file_object):
        counter = 0
        for ifd in self._ifd_list:
            if ifd.is_valid_ifd_offset(os.fstat(file_object.fileno()).st_size):
                counter = counter + 1
        return counter
