"""
Tests for Level 3 Features - Shared Memory
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pyferris import SharedArray, SharedDict, SharedQueue, SharedCounter
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure PyFerris is built with: maturin develop")
    sys.exit(1)


class TestSharedMemory(unittest.TestCase):
    
    def test_shared_array_basic(self):
        """Test basic SharedArray functionality"""
        arr = SharedArray(capacity=100)
        
        # Test initial state
        self.assertEqual(arr.len, 0)
        self.assertTrue(arr.is_empty())
        
        # Test append
        arr.append(1.5)
        arr.append(2.5)
        arr.append(3.5)
        
        self.assertEqual(arr.len, 3)
        self.assertFalse(arr.is_empty())
        
        # Test get
        self.assertEqual(arr.get(0), 1.5)
        self.assertEqual(arr.get(1), 2.5)
        self.assertEqual(arr.get(2), 3.5)
    
    def test_shared_array_set(self):
        """Test SharedArray set functionality"""
        arr = SharedArray(capacity=10)
        
        # Add some data
        for i in range(5):
            arr.append(float(i))
        
        # Test set
        arr.set(2, 99.5)
        self.assertEqual(arr.get(2), 99.5)
        
        # Test out of bounds
        with self.assertRaises(Exception):  # IndexError
            arr.set(10, 1.0)
    
    def test_shared_array_extend(self):
        """Test SharedArray extend functionality"""
        arr = SharedArray(capacity=20)
        
        # Extend with list
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        arr.extend(data)
        
        self.assertEqual(arr.len, 5)
        self.assertEqual(arr.to_list(), data)
    
    def test_shared_array_slice(self):
        """Test SharedArray slice functionality"""
        arr = SharedArray(capacity=20)
        
        # Add test data
        data = [float(i) for i in range(10)]
        arr.extend(data)
        
        # Test slice
        slice_result = arr.slice(2, 6)
        expected = [2.0, 3.0, 4.0, 5.0]
        self.assertEqual(slice_result, expected)
        
        # Test slice with default end
        slice_result = arr.slice(7, None)
        expected = [7.0, 8.0, 9.0]
        self.assertEqual(slice_result, expected)
    
    def test_shared_array_sum(self):
        """Test SharedArray parallel sum"""
        arr = SharedArray(capacity=100)
        
        data = [float(i) for i in range(1, 11)]  # 1.0 to 10.0
        arr.extend(data)
        
        result = arr.sum()
        expected = sum(data)  # 55.0
        self.assertEqual(result, expected)
    
    def test_shared_array_parallel_map(self):
        """Test SharedArray parallel map"""
        arr = SharedArray(capacity=100)
        
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        arr.extend(data)
        
        # Square all elements
        results = arr.parallel_map(lambda x: x ** 2)
        expected = [1.0, 4.0, 9.0, 16.0, 25.0]
        self.assertEqual(results, expected)
    
    def test_shared_array_from_data(self):
        """Test creating SharedArray from existing data"""
        data = [1.5, 2.5, 3.5, 4.5]
        arr = SharedArray.from_data(data)
        
        self.assertEqual(arr.len, 4)
        self.assertEqual(arr.to_list(), data)
    
    def test_shared_array_clear(self):
        """Test SharedArray clear functionality"""
        arr = SharedArray(capacity=10)
        
        # Add data
        arr.extend([1.0, 2.0, 3.0])
        self.assertEqual(arr.len, 3)
        
        # Clear
        arr.clear()
        self.assertEqual(arr.len, 0)
        self.assertTrue(arr.is_empty())
    
    def test_shared_dict_basic(self):
        """Test basic SharedDict functionality"""
        d = SharedDict()
        
        # Test initial state
        self.assertEqual(d.len, 0)
        self.assertTrue(d.is_empty())
        
        # Test set and get
        d.set("key1", "value1")
        d.set("key2", 42)
        d.set("key3", [1, 2, 3])
        
        self.assertEqual(d.len, 3)
        self.assertFalse(d.is_empty())
        
        self.assertEqual(d.get("key1"), "value1")
        self.assertEqual(d.get("key2"), 42)
        self.assertEqual(d.get("key3"), [1, 2, 3])
        self.assertIsNone(d.get("nonexistent"))
    
    def test_shared_dict_contains(self):
        """Test SharedDict contains functionality"""
        d = SharedDict()
        
        d.set("test_key", "test_value")
        
        self.assertTrue(d.contains("test_key"))
        self.assertFalse(d.contains("missing_key"))
    
    def test_shared_dict_pop(self):
        """Test SharedDict pop functionality"""
        d = SharedDict()
        
        d.set("key1", "value1")
        d.set("key2", "value2")
        
        # Pop existing key
        result = d.pop("key1")
        self.assertEqual(result, "value1")
        self.assertEqual(d.len, 1)
        self.assertFalse(d.contains("key1"))
        
        # Pop non-existent key
        result = d.pop("missing")
        self.assertIsNone(result)
    
    def test_shared_dict_keys_values_items(self):
        """Test SharedDict keys, values, items"""
        d = SharedDict()
        
        test_data = {"a": 1, "b": 2, "c": 3}
        for k, v in test_data.items():
            d.set(k, v)
        
        keys = set(d.keys())
        self.assertEqual(keys, set(test_data.keys()))
        
        values = d.values()
        self.assertEqual(set(values), set(test_data.values()))
        
        items = d.items()
        items_dict = dict(items)
        self.assertEqual(items_dict, test_data)
    
    def test_shared_dict_setdefault(self):
        """Test SharedDict setdefault functionality"""
        d = SharedDict()
        
        # Set default for new key
        result = d.setdefault("new_key", "default_value")
        self.assertEqual(result, "default_value")
        self.assertEqual(d.get("new_key"), "default_value")
        
        # Get existing value
        result = d.setdefault("new_key", "different_value")
        self.assertEqual(result, "default_value")  # Should return existing
    
    def test_shared_dict_clear(self):
        """Test SharedDict clear functionality"""
        d = SharedDict()
        
        # Add data
        d.set("key1", "value1")
        d.set("key2", "value2")
        self.assertEqual(d.len, 2)
        
        # Clear
        d.clear()
        self.assertEqual(d.len, 0)
        self.assertTrue(d.is_empty())
    
    def test_shared_queue_basic(self):
        """Test basic SharedQueue functionality"""
        q = SharedQueue()
        
        # Test initial state
        self.assertEqual(q.size, 0)
        self.assertTrue(q.empty())
        
        # Test put and get
        q.put("item1")
        q.put("item2")
        q.put(42)
        
        self.assertEqual(q.size, 3)
        self.assertFalse(q.empty())
        
        # Test FIFO order
        item1 = q.get()
        self.assertEqual(item1, "item1")
        self.assertEqual(q.size, 2)
        
        item2 = q.get()
        self.assertEqual(item2, "item2")
        
        item3 = q.get()
        self.assertEqual(item3, 42)
        
        self.assertEqual(q.size, 0)
        self.assertTrue(q.empty())
    
    def test_shared_queue_max_size(self):
        """Test SharedQueue with max size"""
        q = SharedQueue(max_size=2)
        
        # Fill to capacity
        q.put("item1")
        q.put("item2")
        
        # Should raise error when full
        with self.assertRaises(Exception):
            q.put("item3")
    
    def test_shared_queue_get_nowait(self):
        """Test SharedQueue get_nowait functionality"""
        q = SharedQueue()
        
        # Empty queue
        result = q.get_nowait()
        self.assertIsNone(result)
        
        # With item
        q.put("test_item")
        result = q.get_nowait()
        self.assertEqual(result, "test_item")
        
        # Empty again
        result = q.get_nowait()
        self.assertIsNone(result)
    
    def test_shared_queue_clear(self):
        """Test SharedQueue clear functionality"""
        q = SharedQueue()
        
        # Add items
        q.put("item1")
        q.put("item2")
        self.assertEqual(q.size, 2)
        
        # Clear
        q.clear()
        self.assertEqual(q.size, 0)
        self.assertTrue(q.empty())
    
    def test_shared_counter_basic(self):
        """Test basic SharedCounter functionality"""
        counter = SharedCounter(initial_value=10)
        
        # Test initial value
        self.assertEqual(counter.value, 10)
        
        # Test increment
        result = counter.increment()
        self.assertEqual(result, 11)
        self.assertEqual(counter.value, 11)
        
        # Test decrement
        result = counter.decrement()
        self.assertEqual(result, 10)
        self.assertEqual(counter.value, 10)
    
    def test_shared_counter_arithmetic(self):
        """Test SharedCounter arithmetic operations"""
        counter = SharedCounter(initial_value=100)
        
        # Test add
        result = counter.add(25)
        self.assertEqual(result, 125)
        self.assertEqual(counter.value, 125)
        
        # Test subtract
        result = counter.subtract(50)
        self.assertEqual(result, 75)
        self.assertEqual(counter.value, 75)
    
    def test_shared_counter_set_and_reset(self):
        """Test SharedCounter set and reset"""
        counter = SharedCounter(initial_value=42)
        
        # Test set
        old_value = counter.set(100)
        self.assertEqual(old_value, 42)
        self.assertEqual(counter.value, 100)
        
        # Test reset
        old_value = counter.reset()
        self.assertEqual(old_value, 100)
        self.assertEqual(counter.value, 0)
    
    def test_shared_counter_compare_and_swap(self):
        """Test SharedCounter compare and swap"""
        counter = SharedCounter(initial_value=50)
        
        # Successful swap
        result = counter.compare_and_swap(50, 75)
        self.assertEqual(result, 50)  # Returns old value
        self.assertEqual(counter.value, 75)
        
        # Failed swap (current value != expected)
        result = counter.compare_and_swap(50, 100)
        self.assertEqual(result, 75)  # Returns current value (unchanged)
        self.assertEqual(counter.value, 75)


if __name__ == '__main__':
    unittest.main()
