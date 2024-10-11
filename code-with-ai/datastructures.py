import threading

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self, max_size=1000):
        self.head = None
        self.size = 0
        self.max_size = max_size
        self.lock = threading.Lock()

    def add(self, value):
        # validate input data
        if not isinstance(value, (int, float, str)):
            raise ValueError("Value must be an int, float, or str")

        # add thread safety
        with self.lock:
            if self.size >= self.max_size:
                raise MemoryError("Exceeded maximum linked list size")
            
            new_node = Node(value)
            if self.head is None:
                self.head = new_node
            else:
                current = self.head
                while current.next:
                    current = current.next
                current.next = new_node
            self.size += 1

    def remove(self, value):
        with self.lock:
            current = self.head
            previous = None
            while current:
                if current.value == value:
                    if previous:
                        previous.next = current.next
                    else:
                        self.head = current.next
                    self.size -= 1
                    return True
                previous = current
                current = current.next
            return False

    def print_iteration(self):
        with self.lock:
            current = self.head
            while current:
                print(current.value, end=' ')
                current = current.next
            print()
