from ...steps import XsltStep


def get_step():
    return XsltStep(
        files=["update_changeList.xsl"],
        name="update_changeList",
        pipe_files=True
    )
