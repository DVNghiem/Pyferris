from ._pyferris import (
    array, collection, object as object_mod, lang, function, string
)

# Array
chunk = array.chunk
compact = array.compact
uniq = array.uniq
flatten = array.flatten
intersection = array.intersection
union = array.union
zip = array.zip

# Collection
group_by = collection.group_by
count_by = collection.count_by
shuffle = collection.shuffle
sample = collection.sample
key_by = collection.key_by
partition = collection.partition
every = collection.every
some = collection.some

# Object
get = object_mod.get
set = object_mod.set
merge = object_mod.merge
clone_deep = object_mod.clone_deep
pick = object_mod.pick
omit = object_mod.omit
has = object_mod.has
invert = object_mod.invert
keys = object_mod.keys
values = object_mod.values

# Lang
is_equal = lang.is_equal
is_empty = lang.is_empty
to_array = lang.to_array
is_match = lang.is_match

# Function
memoize = function.memoize_fn
once = function.once
after = function.after
before = function.before

# String
camel_case = string.camel_case
kebab_case = string.kebab_case
snake_case = string.snake_case
capitalize = string.capitalize
words = string.words
truncate = string.truncate

__all__ = [
    'chunk', 'compact', 'uniq', 'flatten', 'intersection', 'union', 'zip',
    'group_by', 'count_by', 'shuffle', 'sample', 'key_by', 'partition', 'every', 'some',
    'get', 'set', 'merge', 'clone_deep', 'pick', 'omit', 'has', 'invert', 'keys', 'values',
    'is_equal', 'is_empty', 'to_array', 'is_match',
    'memoize', 'once', 'after', 'before',
    'camel_case', 'kebab_case', 'snake_case', 'capitalize', 'words', 'truncate'
]
