

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the proper subdirectories so tests can access them.
# This doesn't resolve Manzara but we aren't testing that now.
import commands
import definitions