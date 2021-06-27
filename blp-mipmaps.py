import os
from struct import *
from enum import Enum
from argparse import *

parser = ArgumentParser(description="Replaces source blp's mipmaps with base image of other blp.")
parser.add_argument('-s', '--src', action='store', dest='src', help='source blp file to add mipmaps to')
parser.add_argument('-m', '--mip', action='store', dest='mip', help='blp file to insert into source file\'s mip level')
parser.add_argument('-l', '--level', action='store', type=int, dest='level', help='mip level to override, starting at 0.')
args = parser.parse_args()

class BLP:

    class ColorEncoding(Enum):
        JPEG = 0
        PALETTE = 1
        DXT = 2
        ARGB888 = 3
        ARGB888_DUP = 4

    class PixelFormat(Enum):
        DXT1 = 0
        DXT3 = 1
        ARGB888 = 2
        ARGB1555 = 3
        ARGB4444 = 4
        RGB565 = 5
        DXT5 = 7
        UNSPECIFIED = 8
        ARGB2565 = 9

    def __init__(self, path, level = 0):
        f = open(path, 'r+b')
        self.filepath = path
        self.magic = f.read(4).decode()
        self.format_version = int.from_bytes(f.read(4), byteorder='little')
        self.color_encoding = int.from_bytes(f.read(1), byteorder='little')
        self.alpha_bit_depth = int.from_bytes(f.read(1), byteorder='little')
        self.pixel_format = int.from_bytes(f.read(1), byteorder='little')
        self.mipmap_flags = int.from_bytes(f.read(1), byteorder='little')
        self.width = int.from_bytes(f.read(4), byteorder='little')
        self.height = int.from_bytes(f.read(4), byteorder='little')
        self.mipmap_offsets = unpack('16I', f.read(4*16))
        self.mipmap_sizes = unpack('16I', f.read(4*16))
        # self.mips_bytes = f.read()
        self.mipmap_count = 0
        f.close()
        for mip in self.mipmap_offsets:
            if mip != 0:
                self.mipmap_count += 1
    
    def print_data(self):
        print('Magic: ' + self.magic)
        print('Format Version: ' + str(self.format_version))
        print('Color Encoding: ' + str(self.ColorEncoding(self.color_encoding)) + '(' + str(self.color_encoding) + ')')
        print('Alpha Bit Depth: ' + str(self.alpha_bit_depth))
        print('Pixel Format: ' + str(self.ColorEncoding(self.pixel_format)) + '(' + str(self.pixel_format) + ')')
        print('Mipmap Flags: ' + str(self.mipmap_flags))
        print('Number of mipmaps: ' + str(self.mipmap_count))
        print('Dimensions: ' + str(self.width) + ', ' + str(self.height))
        print('Offsets: ' + str(self.mipmap_offsets))
        print('Sizes: ' + str(self.mipmap_sizes))
    
    # Returns bytes of the top-level mip
    def get_bytes(self):
        with open(self.filepath, 'rb+') as f:
            f.seek(self.mipmap_offsets[0])
            bytes = f.read(self.mipmap_sizes[0])
        return bytes
    
    def insert_mip(self, bytes, level):
        with open(self.filepath, 'rb') as f:
            left = f.read(self.mipmap_offsets[level])
            f.seek(self.mipmap_offsets[level] + self.mipmap_sizes[level])
            right = f.read()
        
        with open(self.filepath, 'w+b') as f:
            f.truncate()
            f.write(left)
            f.write(bytes)
            f.write(right)

def main():
    # dir = os.path.dirname(os.path.realpath(__file__)) + '\\'

    src_blp = BLP(args.src)
    mip_blp = BLP(args.mip)
    # src_blp = BLP(dir + args.src)
    # mip_blp = BLP(dir + args.mip)

    bytes_to_insert = mip_blp.get_bytes()
    src_blp.insert_mip(bytes_to_insert, args.level)
    # src_blp.print_data()
    print("Inserted " + args.mip + " into " + args.src + "[" + str(args.level) + "]")

if __name__ == "__main__":
    main()