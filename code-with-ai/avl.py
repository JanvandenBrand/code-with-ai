#!/usr/bin/env python3
import threading
import logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AVLNode:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None
        self.tree_lock = threading.RLock()

    def insert(self, key):
        """
        Insert a key into the AVL tree.

        Parameters:
        key (int): The key to be inserted into the tree.

        Returns:
        None
        """
        with self.tree_lock:
            self.root = self._insert(self.root, key)
            logging.info(f'Inserted key: {key}')

    def _insert(self, node, key):
        if not node:
            return AVLNode(key)

        if key < node.val:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        return self._rebalance(node)

    def delete(self, key):
        """
        Delete a node with the specified key from the AVL tree.

        Parameters:
        key (int): The key of the node to be deleted.

        Returns:
        None
        """
        with self.tree_lock:
            self.root = self._delete(self.root, key)
            logging.info(f'Deleted key: {key}')

    def _delete(self, node, key):
        if not node:
            return node

        if key < node.val:
            node.left = self._delete(node.left, key)
        elif key > node.val:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            temp = self._get_min_value_node(node.right)
            node.val = temp.val
            node.right = self._delete(node.right, temp.val)

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        return self._rebalance(node)

    def search(self, key):
        """
        Search for a key in the AVL tree.

        Parameters:
        key (int): The key to search for in the tree.

        Returns:
        AVLNode: The node containing the key, or None if the key is not found.
        """
        with self.tree_lock:
            result = self._search(self.root, key)
            logging.info(f'Searched for key: {key}, Found: {result is not None}')
            return result

    def _search(self, node, key):
        if not node or node.val == key:
            return node

        if key < node.val:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def batch_insert(self, keys):
        """
        Perform batch insertions of keys into the AVL tree.

        Parameters:
        keys (list of int): The keys to be inserted into the tree.

        Returns:
        None
        """
        with self.tree_lock:
            for key in keys:
                self.root = self._insert(self.root, key)
                logging.info(f'Batch inserted key: {key}')

    def batch_delete(self, keys):
        """
        Perform batch deletions of keys from the AVL tree.

        Parameters:
        keys (list of int): The keys of the nodes to be deleted.

        Returns:
        None
        """
        with self.tree_lock:
            for key in keys:
                self.root = self._delete(self.root, key)
                logging.info(f'Batch deleted key: {key}')

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))

        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _rebalance(self, node):
        balance = self._get_balance(node)

        if balance > 1:
            if self._get_balance(node.left) < 0:
                node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1:
            if self._get_balance(node.right) > 0:
                node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _get_min_value_node(self, node):
        if node is None:
            return None  # Handle None input gracefully
        current = node
        while current.left is not None:
            current = current.left
        return current

# Test the AVL tree implementation
avl_tree = AVLTree()
avl_tree._rebalance(None)  # Should handle None input gracefully
avl_tree._get_min_value_node(None)  # Should handle None input gracefully
print(avl_tree.search(10))  # Should return None

avl_tree = AVLTree()
avl_tree.insert(10)
avl_tree._rebalance(avl_tree.root)  # Should handle single node tree correctly
avl_tree._get_min_value_node(avl_tree.root)  # Should return the single node
print(avl_tree.search(10).val)  # Should return the node with value 10

avl_tree = AVLTree()
avl_tree.insert(10)
avl_tree.insert(20)
avl_tree.insert(30)
avl_tree._rebalance(avl_tree.root)  # Should rebalance the tree correctlyavl_tree = AVLTree()
print(avl_tree.search(20).val)  # Should return the node with value 20

avl_tree.insert(30)
avl_tree.insert(20)
avl_tree.insert(10)
avl_tree._rebalance(avl_tree.root)  # Should perform right rotation
print(avl_tree.search(20).val)  # Should return the node with value 20  

avl_tree = AVLTree()
avl_tree = AVLTree()
avl_tree.insert(10)
avl_tree.insert(20)
avl_tree.insert(30)
avl_tree._rebalance(avl_tree.root)  # Should perform left rotation
print(avl_tree.search(20).val)  # Should return the node with value 20

# Example usage
if __name__ == "__main__":
    avl_tree = AVLTree()
    print(avl_tree._get_min_value_node(None))  # Should handle None input gracefully