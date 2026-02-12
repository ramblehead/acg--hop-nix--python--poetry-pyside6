# Hey Emacs, this is -*- coding: utf-8 -*-

from string import Template
from typing import TYPE_CHECKING

from autocodegen.utils import kebab_case

if TYPE_CHECKING:
    from autocodegen import Context

template_str = r"""\
;; -*- coding: utf-8 -*-

(${project_name_kebab}-mode 1)
(${project_name_kebab}-setup)
"""


def generate(ctx: Context) -> str:
    project_name = ctx.template_config.project_name

    return Template(template_str).substitute(
        {
            "project_name_kebab": kebab_case(project_name),
        },
    )
