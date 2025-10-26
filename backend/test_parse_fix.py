"""
Test script to verify parse_array_field works correctly
Run this BEFORE starting Django server to confirm the fix
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from unittest.mock import Mock
from apps.projects.views_create import parse_array_field

print("=" * 80)
print("🧪 Testing parse_array_field function...")
print("=" * 80)

# Test 1: Native FormData arrays (multiple values)
print("\n📋 Test 1: Native FormData arrays")
request1 = Mock()
request1.data.getlist = Mock(return_value=['1', '2', '3'])
request1.data.get = Mock(return_value='1')

result1 = parse_array_field(request1, 'section_ids', convert_to_int=True)
print(f"Input: getlist() = ['1', '2', '3']")
print(f"Output: {result1}")
print(f"Type: {type(result1)}")
print(f"Expected: [1, 2, 3]")
print(f"✅ PASS" if result1 == [1, 2, 3] else f"❌ FAIL")

# Test 2: JSON string
print("\n📋 Test 2: JSON string")
request2 = Mock()
request2.data.getlist = Mock(return_value=['[1,2,3]'])  # Single value
request2.data.get = Mock(return_value='[1,2,3]')

result2 = parse_array_field(request2, 'section_ids', convert_to_int=True)
print(f"Input: get() = '[1,2,3]' (JSON string)")
print(f"Output: {result2}")
print(f"Type: {type(result2)}")
print(f"Expected: [1, 2, 3]")
print(f"✅ PASS" if result2 == [1, 2, 3] else f"❌ FAIL")

# Test 3: String file types
print("\n📋 Test 3: String arrays (file types)")
request3 = Mock()
request3.data.getlist = Mock(return_value=['pdf', 'video', 'doc'])
request3.data.get = Mock(return_value='pdf')

result3 = parse_array_field(request3, 'allowed_file_types', convert_to_int=False)
print(f"Input: getlist() = ['pdf', 'video', 'doc']")
print(f"Output: {result3}")
print(f"Type: {type(result3)}")
print(f"Expected: ['pdf', 'video', 'doc']")
print(f"✅ PASS" if result3 == ['pdf', 'video', 'doc'] else f"❌ FAIL")

# Test 4: Empty array
print("\n📋 Test 4: Empty array")
request4 = Mock()
request4.data.getlist = Mock(return_value=None)
request4.data.get = Mock(return_value=None)

result4 = parse_array_field(request4, 'external_links', convert_to_int=False)
print(f"Input: getlist() = None, get() = None")
print(f"Output: {result4}")
print(f"Type: {type(result4)}")
print(f"Expected: []")
print(f"✅ PASS" if result4 == [] else f"❌ FAIL")

print("\n" + "=" * 80)
print("✅ All tests completed!")
print("=" * 80)
print("\n💡 If all tests passed, the function works correctly.")
print("   The issue is likely Django not reloading the module.")
print("\n🔧 Solution:")
print("   1. Stop Django (Ctrl+C)")
print("   2. Delete __pycache__ folders")
print("   3. Restart Django")
print("=" * 80)
