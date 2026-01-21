# Hey Emacs, this is -*- coding: utf-8 -*-

from string import Template
from typing import TYPE_CHECKING

from autocodegen.utils import kebab_case

if TYPE_CHECKING:
    from autocodegen import Context

template_str = """\
{
  "name": "${project_name_kebab}",
  "packageManager": "yarn@4.11.0",
  "devDependencies": {
    "prettier": "^3.6.2",
    "prettier-plugin-pkg": "^0.21.2",
    "prettier-plugin-sh": "^0.18.0",
    "prettier-plugin-toml": "^2.0.6"
  }
}
"""


def generate(ctx: Context) -> str:
    project_name = ctx.template_config.project_name

    return Template(template_str).substitute(
        {
            "project_name_kebab": kebab_case(project_name),
        },
    )
