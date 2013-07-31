from regparser.tree.struct import *
from unittest import TestCase

class DepthTreeTest(TestCase):

    def test_walk(self):
        n1 = Node("1")
        n2 = Node("2")
        n3 = Node("3")
        n4 = Node("4")

        n1.children = [n2, n3]
        n2.children = [n4]

        order = []
        def add_node(n):
            order.append(n)
            if not n == n2:
                return n.text
        ret_val = walk(n1, add_node)
        self.assertEqual([n1, n2, n4, n3], order)
        self.assertEqual(["1", "4", "3"], ret_val)

    def test_find(self):
        n1 = Node('n1', label=['n1'])
        n2 = Node('n2', label=['n2'])
        n3 = Node('n3', label=['n3'])
        n4 = Node('n4', label=['n4'])
        n5 = Node('n5', label=['n1'])

        self.assertEqual(n1, find(n1, 'n1'))
        self.assertEqual(n1, find(Node(children=[n1,n2,n3]), 'n1'))
        self.assertEqual(n1, find(Node(children=[n2,n1,n3]), 'n1'))
        self.assertEqual(n1, find(Node(children=[n2,n3,n1]), 'n1'))
        self.assertEqual(n5, find(Node(children=[n2,n5,n3,n1]), 'n1'))
        self.assertEqual(None, find(n2, 'n1'))
        self.assertEqual(n2, find(n2, 'n2'))

    def test_join_text(self):
        n1 = Node("1")
        n2 = Node("2")
        n3 = Node("3")
        n4 = Node("4")

        n1.children = [n2, n3]
        n2.children = [n4]

        self.assertEqual("1243", join_text(n1))
        self.assertEqual("24", join_text(n2))
        self.assertEqual("3", join_text(n3))
        self.assertEqual("4", join_text(n4))

    def test_encode(self):
        n1 = Node('texttext', [Node(typ='t')], ['1','2','3'])
        n2 = Node(typ='someType', title='Some Title')

        enc = NodeEncoder(sort_keys=True)
        self.assertEqual(enc.encode(n1), enc.encode({
            'typ': Node.REGTEXT,
            'text': 'texttext',
            'children': [{'typ':'t', 'text':'', 'children':[], 'label':[]}],
            'label': ['1', '2', '3']
        }))
        self.assertEqual(enc.encode(n2), enc.encode({
            'typ': 'someType',
            'text': '',
            'children': [],
            'label': [],
            'title': 'Some Title'
        }))
