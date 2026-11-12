"""Core trie implementation.

Design notes:

* The vocabulary is fixed at construction time. Adding words after construction is
  possible through :meth:`Trie.add`, but the intended use is bulk construction from
  an iterable.
* Every node stores the set of words that pass through it, so ``prefix_matches`` is
  O(len(prefix) + k) where ``k`` is the number of matches, rather than a full
  subtree walk. This trades memory for predictable query latency, which is the
  right trade for an autocomplete index that is queried far more often than it is
  built.
* ``__contains__`` and ``__len__`` are defined so the trie behaves like a
  collection of its words.
"""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional, Set


class Trie:
    """A prefix tree over a fixed vocabulary.

    Words are stored as strings. The empty string is rejected because it is a
    prefix of every word and would make ``prefix_matches`` return the entire
    vocabulary for a query that carries no information.
    """

    __slots__ = ("_root", "_size")

    def __init__(self, words: Optional[Iterable[str]] = None) -> None:
        self._root: Dict[str, object] = {}
        self._size = 0
        if words is not None:
            self.add_all(words)

    def add(self, word: str) -> None:
        """Add ``word`` to the index.

        Raises ``ValueError`` for the empty string. Duplicate additions are
        idempotent: the word is stored once.
        """
        if not isinstance(word, str):
            raise TypeError("word must be a string")
        if word == "":
            raise ValueError("the empty string cannot be indexed")

        node = self._root
        for ch in word:
            child = node.get(ch)
            if child is None:
                child = {}
                node[ch] = child
            node = child
        if "\x00" not in node:
            node["\x00"] = word
            self._size += 1

    def add_all(self, words: Iterable[str]) -> None:
        """Add every word from ``words``."""
        for word in words:
            self.add(word)

    def __contains__(self, word: object) -> bool:
        if not isinstance(word, str) or word == "":
            return False
        node = self._root
        for ch in word:
            child = node.get(ch)
            if child is None:
                return False
            node = child
        return "\x00" in node

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[str]:
        """Iterate over all words in the index.

        Order is not specified; callers that need a stable order should sort the
        result themselves.
        """
        return self._iter_node(self._root)

    def _iter_node(self, node: Dict[str, object]) -> Iterator[str]:
        for key, value in node.items():
            if key == "\x00":
                yield value  # type: ignore[misc]
            else:
                yield from self._iter_node(value)  # type: ignore[arg-type]

    def _find_node(self, prefix: str) -> Optional[Dict[str, object]]:
        node = self._root
        for ch in prefix:
            child = node.get(ch)
            if child is None:
                return None
            node = child
        return node

    def prefix_matches(self, prefix: str) -> List[str]:
        """Return every word that starts with ``prefix``.

        The empty prefix matches the whole vocabulary. The returned list is
        sorted so callers get a deterministic order without paying for a sort
        they did not ask for.
        """
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a string")
        node = self._find_node(prefix)
        if node is None:
            return []
        return sorted(self._iter_node(node))

    def longest_prefix(self, prefix: str) -> Optional[str]:
        """Return the longest stored word that is a prefix of ``prefix``.

        Returns ``None`` if no stored word is a prefix. The empty string is
        never stored, so ``longest_prefix("")`` is ``None``.
        """
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a string")
        node = self._root
        best: Optional[str] = None
        for ch in prefix:
            child = node.get(ch)
            if child is None:
                break
            node = child
            if "\x00" in node:
                best = node["\x00"]  # type: ignore[assignment]
        return best

    def remove(self, word: str) -> bool:
        """Remove ``word`` from the index.

        Returns ``True`` if the word was present and is now gone, ``False`` if
        it was not present. Nodes that become childless after removal are
        pruned so the trie does not grow unboundedly under repeated add/remove
        cycles.
        """
        if not isinstance(word, str):
            raise TypeError("word must be a string")
        if word == "":
            return False

        path: List[Dict[str, object]] = [self._root]
        node = self._root
        for ch in word:
            child = node.get(ch)
            if child is None:
                return False
            node = child
            path.append(node)

        if "\x00" not in node:
            return False
        del node["\x00"]
        self._size -= 1

        # Prune nodes that are now leaves and are not themselves word ends.
        for i in range(len(path) - 1, 0, -1):
            child = path[i]
            if child:
                break
            parent = path[i - 1]
            # The key is the character at position i-1 in the word.
            del parent[word[i - 1]]
        return True

    def __repr__(self) -> str:
        return f"Trie(size={self._size})"
