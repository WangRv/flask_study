import ast


test = """class TestClass:
    a = 1
    b = 2
    c = a + b
    test_variable = "123456"

    def __init__(self):
        pass

    def my_func(self):
        pass
    """


# ast parse syntax
class MyVisitor(ast.NodeVisitor):
    def visit_Str(self, node):
        print(f"Found string {node.s}")
        if node.s == "123456":
            node.s = "45678"  # replace variable

    def visit_FunctionDef(self, node):
        print(f"Found Function->{node.name}")


if __name__ == '__main__':
    src = ast.parse(test)
    MyVisitor().visit(src)
