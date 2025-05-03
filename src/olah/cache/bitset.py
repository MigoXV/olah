# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


class Bitset:
    def __init__(self, size) -> None:
        """
        Initializes a Bitset object with a given size.
        
        :param size: The number of bits in the Bitset.
        :type size: int
        """
        self.size = size
        self.bits = bytearray((0,) * ((size + 7) // 8))
    
    def _resize_if_needed(self, index: int) -> None:
        """
        Resizes the internal bytearray if the index is out of the current capacity.
        
        :param index: The index that needs to be checked and potentially resized for.
        :type index: int
        """
        if index >= self.size:
            new_size = (index + 7) // 8
            self.bits.extend(bytearray((0,) * (new_size - len(self.bits))))
            self.size = new_size * 8
            self._resize_if_needed(index)  # Ensure the index is within the new size

    def set(self, index: int) -> None:
        """
        Sets the bit at the specified index to 1.
        
        :param index: The index of the bit to be set.
        :type index: int
        :raises IndexError: If the index is out of range.
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        byte_index = index // 8
        bit_index = index % 8
        self.bits[byte_index] |= 1 << bit_index

    def clear(self, index: int) -> None:
        """
        Sets the bit at the specified index to 0.
        
        :param index: The index of the bit to be cleared.
        :type index: int
        :raises IndexError: If the index is out of range.
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        self._resize_if_needed(index)
        byte_index = index // 8
        bit_index = index % 8
        self.bits[byte_index] &= ~(1 << bit_index)

    def test(self, index: int) -> bool:
        """
        Checks the value of the bit at the specified index.
        
        :param index: The index of the bit to be checked.
        :type index: int
        :raises IndexError: If the index is out of range.
        :return: True if the bit is set (1), False if the bit is cleared (0).
        :rtype: bool
        """
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        byte_index = index // 8
        bit_index = index % 8
        return bool(self.bits[byte_index] & (1 << bit_index))

    def __str__(self) -> str:
        """
        Returns a string representation of the Bitset.

        :return: A string representation of the Bitset.
        :rtype: str
        """
        return "".join(bin(byte)[2:].zfill(8)[::-1] for byte in self.bits)
