"""
Pytest configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a sample text for testing purposes. It contains multiple sentences."


@pytest.fixture
def sample_sources():
    """Sample research sources for testing."""
    return [
        {
            'title': 'Article 1',
            'url': 'https://example.com/article1',
            'domain': 'example.com',
            'snippet': 'This is the first article snippet.'
        },
        {
            'title': 'Article 2',
            'url': 'https://test.edu/article2',
            'domain': 'test.edu',
            'snippet': 'This is the second article snippet with more content.'
        }
    ]
