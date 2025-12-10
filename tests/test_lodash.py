import pytest
from pyferris import lodash
from pyferris.pipeline import Chain

def test_array_functions():
    assert lodash.chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
    assert lodash.compact([0, 1, False, 2, '', 3]) == [1, 2, 3]
    assert sorted(lodash.uniq([1, 2, 1, 3])) == [1, 2, 3]
    assert lodash.flatten([[1, 2], [3, 4], 5]) == [1, 2, 3, 4, 5]
    assert sorted(lodash.intersection([1, 2], [2, 3])) == [2]
    assert sorted(lodash.union([1, 2], [2, 3])) == [1, 2, 3]
    assert lodash.zip([1, 2], ['a', 'b']) == [[1, 'a'], [2, 'b']]

def test_collection_functions():
    data = [{'a': 1}, {'a': 2}, {'a': 1}]
    grouped = lodash.group_by(data, 'a')
    assert len(grouped[1]) == 2
    assert len(grouped[2]) == 1
    
    counted = lodash.count_by(data, 'a')
    assert counted[1] == 2
    assert counted[2] == 1
    
    shuffled = lodash.shuffle([1, 2, 3, 4, 5])
    assert len(shuffled) == 5
    assert set(shuffled) == {1, 2, 3, 4, 5}
    
    partitioned = lodash.partition([1, 2, 3, 4], lambda x: x % 2 == 0)
    assert partitioned[0] == [2, 4]
    assert partitioned[1] == [1, 3]

def test_object_functions():
    obj = {'a': {'b': 2}}
    assert lodash.get(obj, 'a.b') == 2
    assert lodash.get(obj, 'a.c', 'default') == 'default'
    
    new_obj = lodash.set(obj, 'a.c', 3)
    assert new_obj['a']['c'] == 3
    
    merged = lodash.merge({'a': 1}, {'b': 2})
    assert merged == {'a': 1, 'b': 2}
    
    picked = lodash.pick({'a': 1, 'b': 2, 'c': 3}, ['a', 'c'])
    assert picked == {'a': 1, 'c': 3}
    
    omitted = lodash.omit({'a': 1, 'b': 2, 'c': 3}, ['b'])
    assert omitted == {'a': 1, 'c': 3}

def test_lang_functions():
    assert lodash.is_equal({'a': 1}, {'a': 1})
    assert not lodash.is_equal({'a': 1}, {'a': 2})
    assert lodash.is_empty([])
    assert lodash.is_empty({})
    assert not lodash.is_empty([1])
    assert lodash.to_array('abc') == ['a', 'b', 'c']

def test_string_functions():
    assert lodash.camel_case('Foo Bar') == 'fooBar'
    assert lodash.kebab_case('Foo Bar') == 'foo-bar'
    assert lodash.snake_case('Foo Bar') == 'foo_bar'
    assert lodash.capitalize('foo') == 'Foo'
    assert lodash.words('hello world') == ['hello', 'world']
    assert lodash.truncate('hello world', 5) == 'he...'

def test_chain_integration():
    result = (Chain([1, 2, 3, 4])
              .map(lambda x: x * 2)
              .filter(lambda x: x > 4)
              .value())
    assert result == [6, 8]
    
    result_uniq = (Chain([1, 2, 1, 3])
                   .uniq()
                   .sort()
                   .value())
    assert result_uniq == [1, 2, 3]
    
    result_chunk = (Chain([1, 2, 3, 4])
                    .chunk(2)
                    .value())
    assert result_chunk == [[1, 2], [3, 4]]
