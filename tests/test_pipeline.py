"""
PyFerris Pipeline Processing Tests

Tests for pipeline functionality:
- Pipeline class
- Chain class
- pipeline_map function
"""

import pytest
import time

from pyferris import Pipeline, Chain, pipeline_map


class TestPipeline:
    """Test Pipeline functionality."""

    def test_pipeline_creation(self):
        """Test basic Pipeline creation."""
        pipeline = Pipeline()
        assert pipeline is not None

    def test_pipeline_single_stage(self):
        """Test Pipeline with single stage."""
        pipeline = Pipeline()
        
        def double_item(item):
            return item * 2
        
        pipeline.add(double_item)
        
        input_data = [1, 2, 3, 4, 5]
        result = pipeline.execute(input_data)
        expected = [2, 4, 6, 8, 10]
        assert result == expected

    def test_pipeline_multiple_stages(self):
        """Test Pipeline with multiple stages."""
        pipeline = Pipeline()
        
        # Stage 1: Double each number
        def double_item(item):
            return item * 2
        
        # Stage 2: Add 1 to each number
        def add_one_item(item):
            return item + 1
        
        pipeline.add(double_item)
        pipeline.add(add_one_item)
        
        input_data = [1, 2, 3, 4, 5]
        result = pipeline.execute(input_data)
        # After doubling: [2, 4, 6, 8, 10]
        # After adding 1: [3, 5, 7, 9, 11]
        expected = [3, 5, 7, 9, 11]
        assert result == expected

    def test_pipeline_data_transformation(self):
        """Test Pipeline with various data transformations."""
        pipeline = Pipeline()
        
        # Stage 1: Convert to strings
        def to_string(item):
            return str(item)
        
        # Stage 2: Add prefix
        def add_prefix(item):
            return f"item_{item}"
        
        # Stage 3: Convert to uppercase
        def to_upper(item):
            return item.upper()
        
        pipeline.add(to_string)
        pipeline.add(add_prefix)
        pipeline.add(to_upper)
        
        input_data = [1, 2, 3]
        result = pipeline.execute(input_data)
        expected = ["ITEM_1", "ITEM_2", "ITEM_3"]
        assert result == expected

    def test_pipeline_empty_input(self):
        """Test Pipeline with empty input."""
        pipeline = Pipeline()
        
        def identity(data):
            return data
        
        pipeline.add(identity)
        
        result = pipeline.execute([])
        assert result == []

    def test_pipeline_single_item(self):
        """Test Pipeline with single item."""
        pipeline = Pipeline()
        
        def process_item(data):
            return data * 3
        
        pipeline.add(process_item)
        
        result = pipeline.execute([7])
        assert result == [21]

    def test_pipeline_stage_modification(self):
        """Test Pipeline stage modification."""
        pipeline = Pipeline()
        
        def stage1(data):
            return data + 1
        
        def stage2(data):
            return data * 2
        
        # Add stages
        pipeline.add(stage1)
        pipeline.add(stage2)
        
        # Execute
        input_data = [1, 2, 3]
        result = pipeline.execute(input_data)
        expected = [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2
        assert result == expected

    def test_pipeline_error_handling(self):
        """Test Pipeline error handling."""
        pipeline = Pipeline()
        
        def failing_stage(data):
            if data == 3:
                raise ValueError("Stage failed")
            return data
        
        pipeline.add(failing_stage)
        
        # Should propagate the exception
        with pytest.raises(ValueError, match="Stage failed"):
            pipeline.execute([1, 2, 3, 4])

    def test_pipeline_complex_stages(self):
        """Test Pipeline with complex processing stages."""
        pipeline = Pipeline()
        
        # Stage 1: Apply different transformations based on parity
        def transform_by_parity(data):
            if data % 2 == 0:
                return data * 2  # Double evens
            else:
                return data * 3  # Triple odds
        
        # Stage 2: Add a constant
        def add_constant(data):
            return data + 10
        
        # Stage 3: Apply final transformation
        def final_transform(data):
            return data if data < 50 else data // 2
        
        pipeline.add(transform_by_parity)
        pipeline.add(add_constant)
        pipeline.add(final_transform)
        
        input_data = [1, 2, 3, 4, 5, 6]
        result = pipeline.execute(input_data)
        
        # 1: 1*3=3, 3+10=13, 13<50=13
        # 2: 2*2=4, 4+10=14, 14<50=14  
        # 3: 3*3=9, 9+10=19, 19<50=19
        # 4: 4*2=8, 8+10=18, 18<50=18
        # 5: 5*3=15, 15+10=25, 25<50=25
        # 6: 6*2=12, 12+10=22, 22<50=22
        expected = [13, 14, 19, 18, 25, 22]
        assert result == expected

    def test_pipeline_no_stages(self):
        """Test Pipeline with no stages."""
        pipeline = Pipeline()
        
        # Should return input unchanged
        input_data = [1, 2, 3]
        result = pipeline.execute(input_data)
        assert result == input_data

    @pytest.mark.slow
    def test_pipeline_performance(self):
        """Test Pipeline performance with large data."""
        pipeline = Pipeline()
        
        def cpu_intensive_stage(data):
            return sum(range(data))
        
        def filter_large(data):
            return data if data > 100 else None
        
        # Filter out None values after execution
        def remove_none(result_list):
            return [x for x in result_list if x is not None]
        
        pipeline.add(cpu_intensive_stage)
        pipeline.add(filter_large)
        
        input_data = list(range(20, 40))  # Numbers that will produce sums > 100
        
        start_time = time.time()
        result = pipeline.execute(input_data)
        # Remove None values (items that didn't pass the filter)
        filtered_result = remove_none(result)
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert execution_time < 5.0  # 5 seconds should be plenty
        assert len(filtered_result) > 0  # Should have some results


class TestChain:
    """Test Chain functionality."""

    def test_chain_creation(self):
        """Test basic Chain creation."""
        chain = Chain()
        assert chain is not None

    def test_chain_single_function(self):
        """Test Chain with single function."""
        chain = Chain()
        
        def square(x):
            return x * x
        
        chain.then(square)
        
        result = chain.execute_one(5)
        assert result == 25

    def test_chain_multiple_functions(self):
        """Test Chain with multiple functions."""
        chain = Chain()
        
        def add_one(x):
            return x + 1
        
        def multiply_by_two(x):
            return x * 2
        
        def square(x):
            return x * x
        
        chain.then(add_one)
        chain.then(multiply_by_two)
        chain.then(square)
        
        # Input: 3 -> 4 -> 8 -> 64
        result = chain.execute_one(3)
        assert result == 64

    def test_chain_string_operations(self):
        """Test Chain with string operations."""
        chain = Chain()
        
        def add_prefix(s):
            return f"prefix_{s}"
        
        def to_upper(s):
            return s.upper()
        
        def add_suffix(s):
            return f"{s}_SUFFIX"
        
        chain.then(add_prefix)
        chain.then(to_upper)
        chain.then(add_suffix)
        
        result = chain.execute_one("test")
        assert result == "PREFIX_TEST_SUFFIX"

    def test_chain_type_conversions(self):
        """Test Chain with type conversions."""
        chain = Chain()
        
        def to_string(x):
            return str(x)
        
        def repeat_three_times(s):
            return s * 3
        
        def get_length(s):
            return len(s)
        
        chain.then(to_string)
        chain.then(repeat_three_times)
        chain.then(get_length)
        
        # Input: 42 -> "42" -> "424242" -> 6
        result = chain.execute_one(42)
        assert result == 6

    def test_chain_no_functions(self):
        """Test Chain with no functions."""
        chain = Chain()
        
        # Should return input unchanged
        result = chain.execute_one("unchanged")
        assert result == "unchanged"

    def test_chain_error_handling(self):
        """Test Chain error handling."""
        chain = Chain()
        
        def normal_function(x):
            return x * 2
        
        def failing_function(x):
            raise ValueError("Chain function failed")
        
        chain.then(normal_function)
        chain.then(failing_function)
        
        # Should propagate the exception
        with pytest.raises(ValueError, match="Chain function failed"):
            chain.execute_one(5)

    def test_chain_complex_data(self):
        """Test Chain with complex data structures."""
        chain = Chain()
        
        def add_key(d):
            d["new_key"] = "new_value"
            return d
        
        def transform_values(d):
            return {k: v.upper() if isinstance(v, str) else v for k, v in d.items()}
        
        def extract_keys(d):
            return list(d.keys())
        
        chain.then(add_key)
        chain.then(transform_values)
        chain.then(extract_keys)
        
        input_data = {"existing": "value"}
        result = chain.execute_one(input_data)
        
        # Should have both keys, order might vary
        assert set(result) == {"existing", "new_key"}

    def test_chain_mathematical_operations(self):
        """Test Chain with mathematical operations."""
        chain = Chain()
        
        def power_of_two(x):
            return x ** 2
        
        def add_ten(x):
            return x + 10
        
        def divide_by_three(x):
            return x / 3
        
        def round_result(x):
            return round(x, 2)
        
        chain.then(power_of_two)
        chain.then(add_ten)
        chain.then(divide_by_three)
        chain.then(round_result)
        
        # Input: 8 -> 64 -> 74 -> 24.67 -> 24.67
        result = chain.execute_one(8)
        expected = round(74 / 3, 2)
        assert result == expected


class TestPipelineMap:
    """Test pipeline_map functionality."""

    def test_pipeline_map_basic(self):
        """Test basic pipeline_map functionality."""
        def add_one(x):
            return x + 1
        
        def multiply_by_two(x):
            return x * 2
        
        operations = [add_one, multiply_by_two]
        data = [1, 2, 3, 4, 5]
        
        result = pipeline_map(data, operations, chunk_size=2)
        
        # Each item: x -> (x+1) -> (x+1)*2
        expected = [4, 6, 8, 10, 12]
        assert result == expected

    def test_pipeline_map_single_operation(self):
        """Test pipeline_map with single operation."""
        def square(x):
            return x * x
        
        operations = [square]
        data = [1, 2, 3, 4]
        
        result = pipeline_map(data, operations, chunk_size=2)
        expected = [1, 4, 9, 16]
        assert result == expected

    def test_pipeline_map_multiple_operations(self):
        """Test pipeline_map with multiple operations."""
        def add_five(x):
            return x + 5
        
        def multiply_by_three(x):
            return x * 3
        
        def subtract_two(x):
            return x - 2
        
        operations = [add_five, multiply_by_three, subtract_two]
        data = [1, 2, 3]
        
        result = pipeline_map(data, operations, chunk_size=1)
        
        # Each item: x -> (x+5) -> (x+5)*3 -> ((x+5)*3)-2
        # 1 -> 6 -> 18 -> 16
        # 2 -> 7 -> 21 -> 19
        # 3 -> 8 -> 24 -> 22
        expected = [16, 19, 22]
        assert result == expected

    def test_pipeline_map_empty_data(self):
        """Test pipeline_map with empty data."""
        def identity(x):
            return x
        
        operations = [identity]
        
        result = pipeline_map([], operations, chunk_size=1)
        assert result == []

    def test_pipeline_map_empty_operations(self):
        """Test pipeline_map with empty operations."""
        data = [1, 2, 3]
        
        result = pipeline_map(data, [], chunk_size=1)
        # Should return original data
        assert result == data

    def test_pipeline_map_different_chunk_sizes(self):
        """Test pipeline_map with different chunk sizes."""
        def double(x):
            return x * 2
        
        operations = [double]
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        expected = [2, 4, 6, 8, 10, 12, 14, 16]
        
        # Test various chunk sizes
        for chunk_size in [1, 2, 3, 4, 8, 16]:
            result = pipeline_map(data, operations, chunk_size=chunk_size)
            assert result == expected

    def test_pipeline_map_complex_operations(self):
        """Test pipeline_map with complex operations."""
        def to_string(x):
            return str(x)
        
        def add_prefix(s):
            return f"num_{s}"
        
        def get_length(s):
            return len(s)
        
        operations = [to_string, add_prefix, get_length]
        data = [1, 22, 333]
        
        result = pipeline_map(data, operations, chunk_size=2)
        
        # 1 -> "1" -> "num_1" -> 5
        # 22 -> "22" -> "num_22" -> 6
        # 333 -> "333" -> "num_333" -> 7
        expected = [5, 6, 7]
        assert result == expected

    def test_pipeline_map_error_handling(self):
        """Test pipeline_map error handling."""
        def normal_op(x):
            return x + 1
        
        def failing_op(x):
            if x == 3:
                raise ValueError("Operation failed")
            return x * 2
        
        operations = [normal_op, failing_op]
        data = [1, 2, 3, 4]
        
        # Should propagate the exception
        with pytest.raises((ValueError, Exception)):
            pipeline_map(data, operations, chunk_size=2)

    @pytest.mark.slow
    def test_pipeline_map_performance(self):
        """Test pipeline_map performance characteristics."""
        def cpu_operation(x):
            # Small CPU-intensive operation
            return sum(range(x % 50))
        
        def filter_operation(x):
            return x if x > 10 else 0
        
        operations = [cpu_operation, filter_operation]
        data = list(range(100))
        
        # Test with different chunk sizes
        times = {}
        
        for chunk_size in [1, 10, 25]:
            start_time = time.time()
            result = pipeline_map(data, operations, chunk_size=chunk_size)
            execution_time = time.time() - start_time
            times[chunk_size] = execution_time
            
            # All should produce same result
            assert len(result) == len(data)
        
        # All executions should complete in reasonable time
        for chunk_size, exec_time in times.items():
            assert exec_time < 2.0, f"Chunk size {chunk_size} took too long: {exec_time:.2f}s"


class TestPipelineIntegration:
    """Test integration between pipeline components."""

    def test_pipeline_and_chain_together(self):
        """Test using Pipeline and Chain together."""
        # Create a chain for individual item processing
        item_chain = Chain()
        item_chain.then(lambda x: x * 2)
        item_chain.then(lambda x: x + 1)
        
        # Create a pipeline that uses the chain
        pipeline = Pipeline()
        
        def apply_chain_to_all(data):
            return item_chain.execute_one(data)
        
        def filter_large(data):
            return data if data > 10 else None
        
        pipeline.add(apply_chain_to_all)
        pipeline.add(filter_large)
        
        input_data = [1, 2, 3, 4, 5, 6, 7, 8]
        result = pipeline.execute(input_data)
        
        # Each item: x -> x*2 -> (x*2)+1
        # Then filter > 10 (None for items <= 10)
        # 1->3->None, 2->5->None, 3->7->None, 4->9->None, 5->11, 6->13, 7->15, 8->17
        # Result: [None, None, None, None, 11, 13, 15, 17]
        expected = [None, None, None, None, 11, 13, 15, 17]
        assert result == expected

    def test_nested_pipelines(self):
        """Test nested pipeline processing."""
        # Create a simple nested transformation using chains within pipeline stages
        outer_pipeline = Pipeline()
        
        # Create inner chain for complex transformations
        inner_chain = Chain()
        inner_chain.then(lambda x: x * 2)
        inner_chain.then(lambda x: x + 1)
        
        def apply_inner_processing(data):
            # Apply the inner chain to the data
            return inner_chain.execute_one(data)
        
        def final_transformation(data):
            # Apply final transformation
            return data ** 2
        
        outer_pipeline.add(apply_inner_processing)
        outer_pipeline.add(final_transformation)
        
        input_data = [1, 2, 3, 4]
        result = outer_pipeline.execute(input_data)
        
        # 1: 1*2+1=3, 3^2=9
        # 2: 2*2+1=5, 5^2=25
        # 3: 3*2+1=7, 7^2=49
        # 4: 4*2+1=9, 9^2=81
        expected = [9, 25, 49, 81]
        assert result == expected

    def test_pipeline_with_parallel_operations(self):
        """Test pipeline integration with parallel operations."""
        pipeline = Pipeline()
        
        def square_operation(data):
            return data * data
        
        def filter_and_transform(data):
            if data > 25:
                return data + 100  # Add 100 to large values
            else:
                return data  # Keep small values as-is
        
        pipeline.add(square_operation)
        pipeline.add(filter_and_transform)
        
        input_data = list(range(1, 11))  # 1 to 10
        result = pipeline.execute(input_data)
        
        # Squares: [1,4,9,16,25,36,49,64,81,100]
        # Transform: values > 25 get +100, others stay same
        # [1,4,9,16,25,136,149,164,181,200]
        expected = [1, 4, 9, 16, 25, 136, 149, 164, 181, 200]
        assert result == expected


class TestPipelineEdgeCases:
    """Test edge cases for pipeline processing."""

    def test_pipeline_with_none_values(self):
        """Test pipeline handling of None values."""
        pipeline = Pipeline()
        
        def handle_none(data):
            return data if data is not None else 0
        
        def double_values(data):
            return data * 2
        
        pipeline.add(handle_none)
        pipeline.add(double_values)
        
        input_data = [1, None, 3, None, 5]
        result = pipeline.execute(input_data)
        expected = [2, 0, 6, 0, 10]
        assert result == expected

    def test_chain_with_side_effects(self):
        """Test chain with functions that have side effects."""
        chain = Chain()
        side_effects = []
        
        def log_and_double(x):
            side_effects.append(f"processing {x}")
            return x * 2
        
        def log_and_add_one(x):
            side_effects.append(f"adding one to {x}")
            return x + 1
        
        chain.then(log_and_double)
        chain.then(log_and_add_one)
        
        result = chain.execute_one(5)
        
        assert result == 11  # (5*2)+1
        assert len(side_effects) == 2
        assert "processing 5" in side_effects[0]
        assert "adding one to 10" in side_effects[1]

    def test_pipeline_memory_efficiency(self):
        """Test pipeline memory efficiency with large data."""
        pipeline = Pipeline()
        
        def memory_efficient_double(data):
            # Simple operation that doesn't require much memory
            return data * 2
        
        def filter_divisible_by_four(data):
            return data if data % 4 == 0 else None
        
        pipeline.add(memory_efficient_double)
        pipeline.add(filter_divisible_by_four)
        
        # Large input data
        large_data = list(range(1000))
        result = pipeline.execute(large_data)
        
        # Filter out None values
        filtered_result = [x for x in result if x is not None]
        
        # Should process successfully
        assert len(filtered_result) > 0
        # All results should be divisible by 4
        for item in filtered_result:
            assert item % 4 == 0


if __name__ == "__main__":
    pytest.main([__file__])
