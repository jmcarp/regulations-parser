from json import JSONEncoder


class Node(object):
    APPENDIX = u'appendix'
    INTERP = u'interp'
    REGTEXT = u'regtext'
    SUBPART = u'subpart'
    EMPTYPART = u'emptypart'

    INTERP_MARK = 'Interp'

    def __init__(self, text='', children=[], label=[], title=None,
                 node_type=REGTEXT, source_xml=None):

        self.text = unicode(text)

        # defensive copy
        self.children = list(children)

        self.label = [str(l) for l in label if l != '']
        title = unicode(title or '')
        self.title = title or None
        self.node_type = node_type
        self.source_xml = source_xml

    def __repr__(self):
        return (("Node( text = %s, children = %s, label = %s, title = %s, "
                + "node_type = %s)") % (repr(self.text), repr(self.children),
                repr(self.label), repr(self.title), repr(self.node_type)))

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def label_id(self):
        return '-'.join(self.label)


class NodeEncoder(JSONEncoder):
    """Custom JSON encoder to handle Node objects"""
    def default(self, obj):
        if isinstance(obj, Node):
            fields = dict(obj.__dict__)
            if obj.title is None:
                del fields['title']
            for field in ('tagged_text', 'source_xml', 'child_labels'):
                if field in fields:
                    del fields[field]
            return fields
        return super(NodeEncoder, self).default(obj)


def node_decode_hook(d):
    """Convert a JSON object into a Node"""
    if set(
            ('text', 'children',
                'label', 'node_type')) - set(d.keys()) == set():

        return Node(
            d['text'], d['children'], d['label'],
            d.get('title', None), d['node_type'])
    else:
        return d


def walk(node, fn):
    """Perform fn for every node in the tree. Pre-order traversal. fn must
    be a function that accepts a root node."""
    result = fn(node)

    if result is not None:
        results = [result]
    else:
        results = []
    for child in node.children:
        results += walk(child, fn)
    return results


def find(root, label):
    """Search through the tree to find the node with this label."""
    def check(node):
        if node.label_id() == label:
            return node
    response = walk(root, check)
    if response:
        return response[0]


def join_text(node):
    """Join the text of this node and all children"""
    bits = []
    walk(node, lambda n: bits.append(n.text))
    return ''.join(bits)


def merge_duplicates(nodes):
    """Given a list of nodes with the same-length label, merge any
    duplicates (by combining their children)"""
    found_pair = None
    for lidx, lhs in enumerate(nodes):
        for ridx, rhs in enumerate(nodes[lidx + 1:], lidx + 1):
            if lhs.label == rhs.label:
                found_pair = (lidx, ridx)
    if found_pair:
        lidx, ridx = found_pair
        lhs, rhs = nodes[lidx], nodes[ridx]
        lhs.children.extend(rhs.children)
        return merge_duplicates(nodes[:ridx] + nodes[ridx + 1:])
    else:
        return nodes


def treeify(nodes):
    """Given a list of nodes, convert those nodes into the appropriate tree
    structure based on their labels. This assumes that all nodes will fall
    under a set of 'root' nodes, which have the min-length label."""
    if not nodes:
        return nodes

    min_len, with_min = len(nodes[0].label), []

    for node in nodes:
        if len(node.label) == min_len:
            with_min.append(node)
        elif len(node.label) < min_len:
            min_len = len(node.label)
            with_min = [node]
    with_min = merge_duplicates(with_min)

    roots = []
    for root in with_min:
        if root.label[-1] == Node.INTERP_MARK:
            is_child = lambda n: n.label[:len(root.label)-1] == root.label[:-1]
        else:
            is_child = lambda n: n.label[:len(root.label)] == root.label
        children = [n for n in nodes if n.label != root.label and is_child(n)]
        root.children = root.children + treeify(children)
        roots.append(root)
    return roots


class FrozenNode(object):
    """Immutable interface for nodes. No guarantees about internal state."""
    def __init__(self, text='', children=(), label=(), title='',
                 node_type=Node.REGTEXT, tagged_text=''):
        self._text = text or ''
        self._children = tuple(children)
        self._label = tuple(label)
        self._title = title or ''
        self._node_type = node_type
        self._tagged_text = tagged_text or ''

    @property
    def text(self):
        return self._text

    @property
    def children(self):
        return self._children

    @property
    def label(self):
        return self._label

    @property
    def title(self):
        return self._title

    @property
    def node_type(self):
        return self._node_type

    @property
    def tagged_text(self):
        return self._tagged_text

    def __repr__(self):
        if not hasattr(self, '_repr_value'):
            self._repr_value = (
                "FrozenNode(text=%s, children=%s, label=%s, title=%s)"
                % (repr(self.text), repr(self.children), repr(self.label),
                   repr(self.title)))
        return self._repr_value

    def __cmp__(self, other):
        return (other.__class__ == self.__class__
                and cmp(repr(self), repr(other)))

    def __hash__(self):
        return hash(repr(self))

    @staticmethod
    def from_node(node):
        children = map(FrozenNode.from_node, node.children)
        return FrozenNode(text=node.text, children=children, label=node.label,
                          title=node.title or '', node_type=node.node_type,
                          tagged_text=getattr(node, 'tagged_text', '') or '')

    @property
    def label_id(self):
        """Convert label into a string"""
        if not hasattr(self, '_label_id'):
            self._label_id = '-'.join(self.label)
        return self._label_id
