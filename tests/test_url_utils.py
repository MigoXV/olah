"""
Unit tests for parse_range_params and get_all_ranges in olah/utils/url_utils.py
"""

import pytest
from olah.utils.url_utils import parse_range_params, get_all_ranges


class TestParseRangeParams:
    """Tests for parse_range_params function."""

    def test_simple_range(self):
        """Test parsing a simple byte range like 'bytes=0-499'."""
        unit, ranges, suffix = parse_range_params("bytes=0-499")
        assert unit == "bytes"
        assert ranges == [(0, 499)]
        assert suffix is None

    def test_open_end_range(self):
        """Test parsing an open-ended range like 'bytes=500-'."""
        unit, ranges, suffix = parse_range_params("bytes=500-")
        assert unit == "bytes"
        assert ranges == [(500, None)]
        assert suffix is None

    def test_suffix_range(self):
        """Test parsing a suffix range like 'bytes=-500'."""
        unit, ranges, suffix = parse_range_params("bytes=-500")
        assert unit == "bytes"
        assert ranges == []
        assert suffix == 500

    def test_multiple_ranges(self):
        """Test parsing multiple ranges like 'bytes=0-99,200-299'."""
        unit, ranges, suffix = parse_range_params("bytes=0-99,200-299")
        assert unit == "bytes"
        assert ranges == [(0, 99), (200, 299)]
        assert suffix is None

    def test_multiple_ranges_with_open_end(self):
        """Test parsing multiple ranges including open-ended range."""
        unit, ranges, suffix = parse_range_params("bytes=0-99,500-")
        assert unit == "bytes"
        assert ranges == [(0, 99), (500, None)]
        assert suffix is None

    def test_range_with_spaces(self):
        """Test parsing ranges with extra spaces."""
        unit, ranges, suffix = parse_range_params("bytes = 0-99 , 200-299")
        assert unit == "bytes"
        assert ranges == [(0, 99), (200, 299)]
        assert suffix is None

    def test_large_range_values(self):
        """Test parsing ranges with large values."""
        unit, ranges, suffix = parse_range_params("bytes=0-999999999999")
        assert unit == "bytes"
        assert ranges == [(0, 999999999999)]
        assert suffix is None

    def test_empty_header_raises(self):
        """Test that empty header raises ValueError."""
        with pytest.raises(ValueError, match="Range header cannot be empty"):
            parse_range_params("")

    def test_invalid_format_no_equals_raises(self):
        """Test that header without '=' raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Range header format"):
            parse_range_params("bytes0-499")

    def test_invalid_range_no_dash_raises(self):
        """Test that range without '-' raises ValueError."""
        with pytest.raises(ValueError, match="Invalid range specifier"):
            parse_range_params("bytes=499")

    def test_invalid_range_empty_both_raises(self):
        """Test that range with empty start and end raises ValueError."""
        with pytest.raises(ValueError, match="Invalid range specifier"):
            parse_range_params("bytes=-")


class TestGetAllRanges:
    """Tests for get_all_ranges function."""

    def test_simple_range(self):
        """Test converting a simple range to absolute positions."""
        ranges = get_all_ranges(1000, "bytes", [(0, 499)], None)
        assert ranges == [(0, 500)]  # end is exclusive

    def test_open_end_range(self):
        """Test converting open-ended range."""
        ranges = get_all_ranges(1000, "bytes", [(500, None)], None)
        assert ranges == [(500, 1000)]

    def test_suffix_range(self):
        """Test converting suffix range."""
        ranges = get_all_ranges(1000, "bytes", [], 200)
        assert ranges == [(800, 1000)]

    def test_multiple_ranges(self):
        """Test converting multiple ranges."""
        ranges = get_all_ranges(1000, "bytes", [(0, 99), (200, 299)], None)
        assert ranges == [(0, 100), (200, 300)]

    def test_range_exceeds_file_size(self):
        """Test that range is clamped to file size."""
        ranges = get_all_ranges(500, "bytes", [(0, 999)], None)
        assert ranges == [(0, 500)]

    def test_invalid_range_skipped(self):
        """Test that invalid range (start > end after clamping) is skipped."""
        ranges = get_all_ranges(100, "bytes", [(200, 300)], None)
        assert ranges == []  # Range is outside file, should be empty

    def test_start_none_defaults_to_zero(self):
        """Test that None start defaults to 0."""
        ranges = get_all_ranges(1000, "bytes", [(None, 499)], None)
        assert ranges == [(0, 500)]
