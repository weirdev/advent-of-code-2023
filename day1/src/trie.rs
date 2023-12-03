use std::{iter::zip, net};

#[derive(Eq, PartialEq, Debug)]
pub struct TrieNode<K, V> {
    prefix: Vec<K>,
    children: Vec<Box<TrieNode<K, V>>>,
    value: Option<V>,
}

#[derive(Eq, PartialEq, Debug)]
pub struct TrieSearchResult<'a, K, V> {
    prefix_match_idx: usize,
    node: &'a TrieNode<K, V>,
}

impl<K, V> TrieNode<K, V>
where
    K: Eq + PartialOrd + Clone,
{
    pub fn empty() -> Self {
        Self {
            prefix: vec![],
            children: vec![],
            value: None,
        }
    }

    pub fn get(&self, key: &[K]) -> Option<&V> {
        self.search(key).and_then(|r| r.get_match())
    }

    pub fn search(&self, key: &[K]) -> Option<TrieSearchResult<K, V>> {
        let search_start = TrieSearchResult {
            prefix_match_idx: 0,
            node: self,
        };
        return search_start.search(key);
    }

    // Returns the value stored at the given key (if any)
    // TODO: Should be able to use search here
    pub fn insert(&mut self, key: &[K], value: V) -> Option<V> {
        if key.is_empty() {
            let mut wrapped_value = Some(value);
            std::mem::swap(&mut self.value, &mut wrapped_value);
            return wrapped_value;
        }

        for child in self.children.iter_mut() {
            // TODO: When we add ordering, we can use binary search here
            if child.prefix[0] == key[0] {
                // This is the child we are looking for
                let diff_index = child
                    .prefix
                    .iter()
                    .zip(key.iter())
                    .enumerate()
                    .skip(1) // Skip the one we already know is equal
                    .filter(|(_i, (c1, c2))| c1 != c2)
                    .map(|(i, _)| i)
                    .next();
                if let Some(diff_index) = diff_index {
                    return split_insert_diverging_key_and_prefix(child, key, value, diff_index);
                } else if child.prefix.len() < key.len() {
                    // If the child prefix is a prefix of the key,
                    // recurse to insert into child node with the remainder of the prefix
                    return child.insert(&key[child.prefix.len()..], value);
                } else if child.prefix.len() > key.len() {
                    // If the key is a prefix of the child prefix,
                    // the new direct child node will be the key being inserted
                    // with a grandchild node containing the remainder of the old child prefix
                    let mut pre_split_children = Vec::new();
                    std::mem::swap(&mut child.children, &mut pre_split_children);
                    let mut pre_split_value = None;
                    std::mem::swap(&mut child.value, &mut pre_split_value);
                    let grandchild = Box::new(TrieNode {
                        prefix: child.prefix[key.len()..].to_vec(),
                        children: pre_split_children,
                        value: pre_split_value,
                    });
                    child.prefix = key.to_vec();
                    child.children = vec![grandchild];
                    child.value = Some(value);
                    return None;
                } else {
                    // If the child prefix is equal to the key,
                    // replace the child value with the key being inserted
                    // and return the old value
                    let mut wrapped_value = Some(value);
                    std::mem::swap(&mut child.value, &mut wrapped_value);
                    return wrapped_value;
                }
            }
        }

        // No existing matching child node was found, so add a new one
        // TODO: Order
        self.children.push(Box::new(TrieNode {
            prefix: key.to_vec(),
            children: vec![],
            value: Some(value),
        }));
        None
    }
}

impl<'a, K, V> TrieSearchResult<'a, K, V>
where
    K: Eq + PartialOrd + Clone,
{
    pub fn search(&self, mut key: &[K]) -> Option<TrieSearchResult<'a, K, V>> {
        if key.is_empty() {
            return Some(self.clone());
        }

        let self_max_prefix_cmp_count =
            std::cmp::min(self.node.prefix.len() - self.prefix_match_idx, key.len());
        if &self.node.prefix
            [self.prefix_match_idx..self.prefix_match_idx + self_max_prefix_cmp_count]
            == &key[..self_max_prefix_cmp_count]
        {
        } else {
            // Mismatch before consuming the current node
            return None;
        }

        if self_max_prefix_cmp_count == key.len() {
            // Consumed the entire key, stay at this node
            return Some(TrieSearchResult {
                prefix_match_idx: self.prefix_match_idx + self_max_prefix_cmp_count,
                node: self.node,
            });
        }

        // Otherwise, we have key remaining, so we need to descend into a child node
        key = &key[self_max_prefix_cmp_count..];

        // TODO: When we add ordering, we can use binary search here
        for child in self.node.children.iter() {
            if child.prefix[0] == key[0] {
                // This is the child we are looking for
                let child_search_start = TrieSearchResult {
                    prefix_match_idx: 1,
                    node: child,
                };

                return child_search_start.search(&key[1..]);
            }
        }

        None
    }

    pub fn get_match(&self) -> Option<&'a V> {
        if self.prefix_match_idx == self.node.prefix.len() {
            self.node.value.as_ref()
        } else {
            None
        }
    }

    pub fn get(&self, key: &[K]) -> Option<&'a V> {
        if key.is_empty() {
            self.get_match()
        } else {
            self.search(key).and_then(|r| r.get_match())
        }
    }
}

impl<'a, K, V> Clone for TrieSearchResult<'a, K, V> {
    fn clone(&self) -> Self {
        TrieSearchResult {
            prefix_match_idx: self.prefix_match_idx,
            node: self.node,
        }
    }
}

fn split_insert_diverging_key_and_prefix<K, V>(
    node: &mut TrieNode<K, V>,
    key: &[K],
    value: V,
    diff_index: usize,
) -> Option<V>
where
    K: Eq + PartialOrd + Clone,
{
    let split_child_with_new_value = Box::new(TrieNode {
        prefix: key[diff_index..].to_vec(),
        children: vec![],
        value: Some(value),
    });

    let new_node_prefix = node.prefix[..diff_index].to_vec();

    let mut pre_split_children = Vec::new();
    std::mem::swap(&mut node.children, &mut pre_split_children);
    let mut pre_split_value = None;
    std::mem::swap(&mut node.value, &mut pre_split_value);
    let split_child_l22 = Box::new(TrieNode {
        prefix: node.prefix[diff_index..].to_vec(),
        children: pre_split_children,
        value: pre_split_value,
    });

    if node.prefix[diff_index] <= key[diff_index] {
        node.children = vec![split_child_with_new_value, split_child_l22];
    } else {
        node.children = vec![split_child_l22, split_child_with_new_value];
    }
    node.prefix = new_node_prefix;
    node.value = None;
    return None;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty() {
        let trie: TrieNode<i32, i32> = TrieNode::empty();
        assert_eq!(trie.prefix, vec![]);
        assert_eq!(trie.children, vec![]);
        assert_eq!(trie.value, None);
    }

    #[test]
    fn test_insert_and_get() {
        let mut trie: TrieNode<char, i32> = TrieNode::empty();
        trie.insert(&['a', 'b', 'c'], 123);
        assert_eq!(trie.get(&['a', 'b', 'c']), Some(&123));
        assert_eq!(trie.get(&['a', 'b']), None);
    }

    #[test]
    fn test_insert_overwrite() {
        let mut trie: TrieNode<char, i32> = TrieNode::empty();
        trie.insert(&['a', 'b', 'c'], 123);
        assert_eq!(trie.insert(&['a', 'b', 'c'], 456), Some(123));
        assert_eq!(trie.get(&['a', 'b', 'c']), Some(&456));
    }

    #[test]
    fn test_insert_multiple() {
        let mut trie: TrieNode<char, i32> = TrieNode::empty();
        trie.insert(&['a', 'b', 'c'], 123);
        trie.insert(&['a', 'b', 'd'], 456);
        assert_eq!(trie.get(&['a', 'b', 'c']), Some(&123));
        assert_eq!(trie.get(&['a', 'b', 'd']), Some(&456));
    }

    #[test]
    fn test_search() {
        let mut trie: TrieNode<char, i32> = TrieNode::empty();
        trie.insert(&['a', 'b', 'c'], 123);
        trie.insert(&['a', 'b', 'd'], 456);
        assert_eq!(
            trie.search(&['a', 'b', 'c']),
            Some(TrieSearchResult {
                prefix_match_idx: 1,
                node: &TrieNode {
                    prefix: vec!['c'],
                    children: vec![],
                    value: Some(123),
                }
            })
        );
        assert_eq!(
            trie.search(&['a', 'b', 'd']),
            Some(TrieSearchResult {
                prefix_match_idx: 1,
                node: &TrieNode {
                    prefix: vec!['d'],
                    children: vec![],
                    value: Some(456),
                }
            })
        );
        assert_eq!(trie.search(&['a', 'b', 'e']), None);
    }

    #[test]
    fn test_search_from_search_result() {
        let mut trie: TrieNode<char, i32> = TrieNode::empty();
        trie.insert(&['a', '1', 'b', 'c'], 123);
        trie.insert(&['a', '1', 'b', 'd'], 456);
        let mut search_result = trie.search(&['a']).unwrap();
        search_result = search_result.search(&['1']).unwrap();
        assert_eq!(&search_result.node.prefix[..], &['a', '1', 'b'][..]);
        assert_eq!(search_result.get(&['b', 'd']), Some(&456));
        assert_eq!(search_result.search(&['e']), None);
    }
}
