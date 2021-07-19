import struct
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

        # Set file name
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
