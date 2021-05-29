tag_value_to_name = {
    254: 'NewSubfileType',
    256: 'ImageWidth',
    257: 'ImageLength',
    258: 'BitsPerSample',
    259: 'Compression',
    262: 'PhotometricInterpretation',
    266: 'FillOrder',
    269: 'DocumentNumber',
    270: 'ImageDescription',
    273: 'StripOffsets',
    274: 'Orientation',
    277: 'SamplesPerPixel',
    278: 'RowsPerStrip',
    279: 'StripByteCount',
    282: 'XResolution',
    283: 'YResolution',
    284: 'PlanarConfiguration',
    293: 'T6Options',
    296: 'ResolutionUnit',
    297: 'PageNumber',
    305: 'Software',
    306: 'DateTime',
    315: 'Artist',
    317: 'Predictor',
    338: 'ExtraSamples',
    33432: 'CopyRight',
    34675: 'InterColorProfile',
}

"""
    Conversion from type value to python struct's format chars.
"""
type_to_bytes_number = {
    # BYTE unsigned.
    'BYTE': {
        'value': 1,
        'rep': 'c',
        'byte_count': 1,
    },
    # ASCII byte.
    'ASCII': {
        'value': 2,
        'rep': 'c',
        'byte_count': 1,
    },
    # SHORT number.
    'SHORT': {
        'value': 3,
        'rep': 'H',
        'byte_count': 2,
    },
    # LONG number.
    'LONG': {
        'value': 4,
        'rep': 'L',
        'byte_count': 4,
    },
    # 2 LONGs representing a rational number.
    'RATIONAL': {
        'value': 5,
        'rep': 'LL',
        'byte_count': 8,
    },
    'SBYTE': {
        'value': 6,
        'rep': 'c',
        'byte_count': 1,
    },
    # UNDEFINED.
    'UNDEFINED': {
        'value': 7,
        'rep': 'x',
        'byte_count': None,
    },
    # signed SHORT number.
    'SSHORT': {
        'value': 8,
        'rep': 'h',
        'byte_count': 2,
    },
    # signed LONG number.
    'SLONG': {
        'value': 9,
        'rep': 'l',
        'byte_count': 1,
    },
    # 2 signed LONGs representing a signed rational number.
    'SRATIONAL': {
        'value': 5,
        'rep': 'll',
        'byte_count': 8,
    },

}


class TiffIFDEntry:
    def __init__(self, ifd_tag, ifd_type, ifd_count, ifd_value):
        self._tag = ifd_tag
        self._type = ifd_type
        self._count = ifd_count
        self._value = ifd_value
        self._is_value = self.calculate_is_value()

    @property
    def tag(self):
        return self._tag

    @property
    def tag_name(self):
        return tag_value_to_name[self._tag]

    @property
    def type(self):
        return self._type

    @property
    def type_name(self):
        for type_name in type_to_bytes_number.keys():
            if type_to_bytes_number[type_name]['value'] == self._type:
                return type_name

    @property
    def count(self):
        return self._count

    @property
    def value(self):
        return self._value

    def calculate_is_value(self):
        """
            Calculate whether or not the entry has a value or an offset.
        :return: True if the entry has value, False if an offset.
        """
        is_value = False
        if self.type_name in ('BYTE', 'SBYTE') and 4 >= self.count:
            is_value = True
        elif 'ASCII' == self.type_name and 4 >= self.count:
            is_value = True
        elif 'UNDEFINED' == self.type_name and 4 >= self.count:
            is_value = True
        elif self.type_name in ('SHORT', 'SSHORT') and 2 >= self.count:
            is_value = True
        elif self.type_name in ('LONG', 'SLONG') and 1 >= self.count:
            is_value = True
        return is_value
