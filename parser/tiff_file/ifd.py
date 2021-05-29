from utils import InvalidTIFFileException
from tiff_file.ifd_entry import *
import struct
import math
import numpy as np

IFD_OFFSET_IN_BYTES = 4
IFD_COUNT_IN_BYTES = 2
IFD_CONTENT_IN_BYTES = 12


class TiffIFD:

    def __init__(self, is_little_endian, offset):
        self._entries = []
        self.ifd_offset = offset
        self._is_little_endian = is_little_endian

        self._rows_per_strip = None
        self._strip_byte_count = None
        self._strip_offsets = None
        self._image_length = None

    def parse_ifd(self, file_object):
        """
            Parse a single IFD structure.

        :param file_object: A file object of a TIFF file.

        :return: The offset of the next IFD structure.

        :note: The file object should be at the offset of the IFD before calling this method.
        """

        file_object.seek(self.ifd_offset)
        # Get directory entries count
        dir_entries_count, = struct.unpack(
            "{endianness}H".format(endianness='<' if self._is_little_endian else '>'),
            file_object.read(IFD_COUNT_IN_BYTES))

        # Parse entries.
        for i in range(dir_entries_count):
            entry = TiffIFDEntry(*struct.unpack(
                "{endianness}HHII".format(endianness='<' if self._is_little_endian else '>'),
                file_object.read(IFD_CONTENT_IN_BYTES)))
            if entry.tag_name == 'RowsPerStrip':
                self._rows_per_strip = entry
            elif entry.tag_name == 'StripByteCount':
                self._strip_byte_count = entry
            elif entry.tag_name == 'StripOffsets':
                self._strip_offsets = entry
            elif entry.tag_name == 'ImageLength':
                self._image_length = entry

            self._entries.append(entry)

        # Get next IFD offset.
        next_ifd_offset, = struct.unpack(
            "{endianness}I".format(endianness='<' if self._is_little_endian else '>'),
            file_object.read(IFD_OFFSET_IN_BYTES))
        return next_ifd_offset

    @property
    def entries(self):
        return self._entries

    def get_ifd_data(self, file_object):
        """
            Extract the data from the IFD based on the strips in the file.

            :param: file_object - The file object of the TIFF file.
        :return:
        """
        image_strips = []
        # Calculate the number of strips in the image.
        strips_per_image = int(math.floor((self._image_length.value + self._rows_per_strip.value - 1) /
                                          self._rows_per_strip.value))
        bytes_per_strip = self._strip_byte_count.value
        # If there is a single strip, parse it in a single unpacking.
        if strips_per_image == 1:
            file_object.seek(self._strip_offsets.value)
            image_strips.append(np.asarray(list(struct.unpack("{bytes_count}c".format(bytes_count=bytes_per_strip),
                                                              file_object.read(bytes_per_strip)))))
        # For multiple strips, parse first their offsets then the strips.
        else:
            if self._strip_offsets.type_name not in ("SHORT", "LONG"):
                raise InvalidTIFFileException
            # Parse offsets
            file_object.seek(self._strip_offsets.value)
            offsets = struct.unpack("{endianness}{offsets_count}{offset_type}".
                                    format(endianness='<' if self._is_little_endian else '>',
                                           offsets_count=self._strip_offsets.count,
                                           offset_type=type_to_bytes_number[self._strip_offsets.type_name]['rep']),
                                    file_object.read(
                                        self._strip_offsets.count * type_to_bytes_number[self._strip_offsets.type_name][
                                            'byte_count']))
            # Parse the number of bytes in each strip
            file_object.seek(self._strip_byte_count.value)
            strip_num_of_bytes = struct.unpack("{endianness}{strip_num_of_bytes_count}{offset_type}".
                                               format(endianness='<' if self._is_little_endian else '>',
                                                      strip_num_of_bytes_count=self._strip_byte_count.count,
                                                      offset_type=
                                                      type_to_bytes_number[self._strip_byte_count.type_name]['rep']),
                                               file_object.read(
                                                   self._strip_byte_count.count *
                                                   type_to_bytes_number[self._strip_byte_count.type_name][
                                                       'byte_count']))
            # Get Strips' bytes.
            for strip_offset, byte_count in zip(offsets, strip_num_of_bytes):
                file_object.seek(strip_offset)
                image_strips.append(np.asarray(list(struct.unpack("{bytes_count}c".format(bytes_count=byte_count),
                                                                  file_object.read(byte_count)))))
        return image_strips
