#!/usr/bin/env python3
"""
Enable maintenance mode for testing Feature #354
"""
import sys
sys.path.insert(0, 'backend')

from app.core.config import settings

# Enable maintenance mode
settings.MAINTENANCE_MODE = True
settings.MAINTENANCE_MESSAGE = "System is undergoing scheduled maintenance. We will be back online shortly."
settings.MAINTENANCE_ETA = "2 hours"

print(f"✅ Maintenance mode enabled")
print(f"   Message: {settings.MAINTENANCE_MESSAGE}")
print(f"   ETA: {settings.MAINTENANCE_ETA}")
print(f"   Status: {settings.MAINTENANCE_MODE}")
