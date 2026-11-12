# py_trie_index

A prefix tree that answers autocomplete queries over a fixed vocabulary in time proportional to the query length plus the number of matches.

```python
from py_trie_index import Trie

trie = Trie(["cat", "car", "card", "dog", "do"])

trie.prefix_matches("ca")   # ['car', 'card', 'cat']
trie.prefix_matches("")     # ['car', 'card', 'cat', 'do', 'dog']
trie.longest_prefix("cardinal")  # 'card'
"cat" in trie                # True
len(trie)                    # 5
```

## Why this exists

Linear scans over a vocabulary are fine until the vocabulary is large enough that every keystroke in a search box pays for the whole list. A trie pays for the prefix once and then walks only the matching subtree. The trade-off is memory: every node stores its own dictionary of children, so a vocabulary with little shared prefix costs more than the flat list it replaces. For autocomplete over a modest, mostly-shared vocabulary the latency is worth it; for a handful of words it is not.

## API

The package exports one name, `Trie`.

- `Trie(words=None)` — build an index, optionally from an iterable of strings.
- `add(word)` — add a word. Raises `ValueError` for the empty string and `TypeError` for non-strings. Duplicate additions are idempotent.
- `add_all(words)` — add every word from an iterable.
- `prefix_matches(prefix)` — return a new sorted list of every word starting with `prefix`. The empty prefix returns the whole vocabulary.
- `longest_prefix(prefix)` — return the longest stored word that is a prefix of `prefix`, or `None`.
- `remove(word)` — remove a word, returning `True` if it was present. Prunes nodes that become childless.
- `word in trie` — membership test, `False` for the empty string and non-strings.
- `len(trie)` — number of distinct words.
- `iter(trie)` — iterate all words in unspecified order; sort yourself if you need one.

## Edge cases

The empty string is not a valid word. It is rejected by `add` and `remove`, never reported by `prefix_matches`, and `longest_prefix("")` returns `None`. This is deliberate: the empty string is a prefix of every word, so indexing it would make `prefix_matches("")` and `longest_prefix` ambiguous about whether they mean "match everything" or "match the empty word".

`prefix_matches` returns a fresh sorted list on every call. Mutating it does not affect the trie, but sorting on every call is a cost worth knowing about if you call it in a hot loop.
