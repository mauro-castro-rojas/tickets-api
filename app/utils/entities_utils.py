import re


def model_class_name_to_lower(class_name: str) -> str:
    """
    Convert a model class name to lower case.
    If the class name is like: `"SomethingSomething"`, the function will return
    `"something_something"`.

    Parameters
    ----------
    `class_name` : str
        The class name to convert.

    Returns
    -------
    `str`
        The class name converted to lower case.
    """

    # Split the class name by capital letters
    class_name_list = re.findall(r"[A-Z][^A-Z]*", class_name)
    # Convert the class name list to lower case
    class_name_list = [name.lower() for name in class_name_list]
    # Join the class name list with an underscore
    class_name = "_".join(class_name_list)
    return class_name
