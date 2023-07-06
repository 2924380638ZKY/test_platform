from application.task_interface import node
from application.task_interface.node import WithoutToken, WithToken


class TestTask:

    def test_task(self, case, node_url):
        if case["useToken"]:
            if node.login_token is None:
                raise Exception("该用例没有token，请先登录")
            else:

                x = WithToken(node.login_token)
                x.withtoken(case, node_url)

        else:

            x = WithoutToken()
            x.withouttoken(case, node_url)

