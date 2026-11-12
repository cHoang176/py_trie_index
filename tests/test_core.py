import unittest

from py_trie_index import Trie


class TrieConstructionTests(unittest.TestCase):
    def test_empty_trie(self):
        t = Trie()
        self.assertEqual(len(t), 0)
        self.assertEqual(list(t), [])
        self.assertEqual(t.prefix_matches(""), [])
        self.assertIsNone(t.longest_prefix("anything"))

    def test_bulk_construction(self):
        t = Trie(["cat", "car", "card"])
        self.assertEqual(len(t), 3)
        self.assertEqual(sorted(t), ["car", "card", "cat"])

    def test_duplicate_words_are_idempotent(self):
        t = Trie(["cat", "cat", "cat"])
        self.assertEqual(len(t), 1)
        self.assertIn("cat", t)

    def test_empty_string_is_rejected(self):
        t = Trie()
        with self.assertRaises(ValueError):
            t.add("")

    def test_non_string_is_rejected(self):
        t = Trie()
        with self.assertRaises(TypeError):
            t.add(123)  # type: ignore[arg-type]


class TrieMembershipTests(unittest.TestCase):
    def setUp(self):
        self.t = Trie(["cat", "car", "card", "dog"])

    def test_contains_exact_word(self):
        self.assertIn("cat", self.t)
        self.assertIn("card", self.t)
        self.assertNotIn("ca", self.t)
        self.assertNotIn("cats", self.t)
        self.assertNotIn("", self.t)

    def test_contains_non_string(self):
        self.assertNotIn(123, self.t)

    def test_len_tracks_additions(self):
        self.assertEqual(len(self.t), 4)
        self.t.add("cart")
        self.assertEqual(len(self.t), 5)


class TriePrefixTests(unittest.TestCase):
    def setUp(self):
        self.t = Trie(["cat", "car", "card", "dog", "do"])

    def test_prefix_matches_returns_sorted(self):
        self.assertEqual(self.t.prefix_matches("ca"), ["car", "card", "cat"])
        self.assertEqual(self.t.prefix_matches("car"), ["car", "card"])
        self.assertEqual(self.t.prefix_matches("dog"), ["dog"])

    def test_prefix_matches_exact_word_includes_itself(self):
        self.assertEqual(self.t.prefix_matches("do"), ["do", "dog"])

    def test_prefix_matches_empty_prefix_returns_all(self):
        self.assertEqual(
            self.t.prefix_matches(""),
            ["car", "card", "cat", "do", "dog"],
        )

    def test_prefix_matches_missing_prefix(self):
        self.assertEqual(self.t.prefix_matches("z"), [])
        self.assertEqual(self.t.prefix_matches("catx"), [])

    def test_prefix_matches_non_string(self):
        with self.assertRaises(TypeError):
            self.t.prefix_matches(None)  # type: ignore[arg-type]

    def test_longest_prefix(self):
        self.assertEqual(self.t.longest_prefix("cardinal"), "card")
        self.assertEqual(self.t.longest_prefix("car"), "car")
        self.assertEqual(self.t.longest_prefix("do"), "do")
        self.assertEqual(self.t.longest_prefix("d"), None)
        self.assertEqual(self.t.longest_prefix(""), None)
        self.assertEqual(self.t.longest_prefix("xyz"), None)


class TrieRemovalTests(unittest.TestCase):
    def setUp(self):
        self.t = Trie(["cat", "car", "card", "dog"])

    def test_remove_present_word(self):
        self.assertTrue(self.t.remove("car"))
        self.assertEqual(len(self.t), 3)
        self.assertNotIn("car", self.t)
        self.assertEqual(self.t.prefix_matches("car"), ["card"])

    def test_remove_absent_word(self):
        self.assertFalse(self.t.remove("cow"))
        self.assertFalse(self.t.remove(""))
        self.assertEqual(len(self.t), 4)

    def test_remove_prunes_dead_nodes(self):
        t = Trie(["cat"])
        self.assertTrue(t.remove("cat"))
        self.assertEqual(len(t), 0)
        self.assertEqual(t.prefix_matches("c"), [])
        # Re-adding after a prune must still work.
        t.add("cat")
        self.assertIn("cat", t)
        self.assertEqual(len(t), 1)

    def test_remove_does_not_prune_shared_prefix(self):
        self.assertTrue(self.t.remove("card"))
        self.assertIn("car", self.t)
        self.assertIn("cat", self.t)
        self.assertEqual(self.t.prefix_matches("car"), ["car"])


if __name__ == "__main__":
    unittest.main()
