#!/usr/bin/env python3
"""
Auto-Apply Launcher - Wrapper to run auto-apply with proper imports
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
from core.automation.linkedin_auto_apply import LinkedInAutoApplyV2

if __name__ == '__main__':
    auto_apply = LinkedInAutoApplyV2()
    auto_apply.run()
