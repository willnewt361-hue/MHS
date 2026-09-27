"""
Testing & Deployment helpers - pytest scaffold and CI hints
"""

import os

def run_unit_tests():
    """Run pytest suite"""
    os.system('pytest -q')

if __name__ == '__main__':
    print('Run: pytest -q')
