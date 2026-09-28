from ...steps import XsltStep


def get_step():
    return XsltStep(
        files=["check_for_ub_publisher.xsl"],
        name="check_for_ub_publisher",
        pipe_files=True
    )
