# Hey Emacs, this is -*- coding: utf-8 -*-

from string import Template
from typing import TYPE_CHECKING

from autocodegen.utils import kebab_case

if TYPE_CHECKING:
    from autocodegen import Context

template_str = r"""\
;; Hey Emacs, this is -*- coding: utf-8 -*-

(require 'hydra)
(require 'prettier)
(require 'blacken)
(require 'flycheck)
(require 'lsp-mode)
(require 'lsp-pyright)
(require 'lsp-ruff)
(require 'lsp-rust)
(require 'vterm)

(define-minor-mode acg-templates-mode
  "acg-templates project-specific minor mode."
  :lighter " acg-templates")

(add-to-list 'rm-blacklist " acg-templates")

(defun acg-templates/lsp-javascript-deps-providers-path (relative-path)
  (let ((path-hop
         (expand-file-name
          (file-name-concat (rh-project-get-root)
                            "node_modules/.bin" relative-path))))
    path-hop))

(defun acg-templates/lsp-javascript-setup ()
  ;; (setq-local lsp-deps-providers (copy-tree lsp-deps-providers))

  (plist-put
   lsp-deps-providers
   :acg-templates/local-npm
   (list :path #'acg-templates/lsp-javascript-deps-providers-path))

  (lsp--require-packages)

  (lsp-dependency 'typescript-language-server
                  '(:acg-templates/local-npm
                    "typescript-language-server"))

  (lsp-dependency 'tailwindcss-language-server
                  '(:acg-templates/local-npm
                    "tailwindcss-language-server"))

  (lsp-dependency 'typescript
                  '(:acg-templates/local-npm "tsserver"))

  (add-hook
   'lsp-after-initialize-hook
   #'acg-templates/flycheck-add-eslint-next-to-lsp))

(defun acg-templates/flycheck-after-syntax-check-hook-once ()
  (remove-hook
   'flycheck-after-syntax-check-hook
   #'acg-templates/flycheck-after-syntax-check-hook-once
   t)
  (flycheck-buffer))

(defun acg-templates/flycheck-add-eslint-next-to-lsp ()
  (when (seq-contains-p '(js2-mode typescript-mode web-mode) major-mode)
    (flycheck-add-next-checker 'lsp 'javascript-eslint)))

(defun acg-templates/lsp-python-deps-providers-path (relative-path)
  (let ((venv-bin-path-outer
         (expand-file-name
          (file-name-concat (rh-project-get-root)
                            ".venv/bin" relative-path)))
        (venv-bin-path-inner
         (expand-file-name
          (file-name-concat (rh-project-get-root)
                            "hop" ".venv/bin" relative-path))))
    (if (file-exists-p venv-bin-path-outer)
        venv-bin-path-outer
      venv-bin-path-inner)))

(defun acg-templates/lsp-python-setup ()
  (plist-put
   lsp-deps-providers
   :acg-templates/local-venv
   (list :path #'acg-templates/lsp-python-deps-providers-path))

  (lsp-dependency 'pyright
                  '(:acg-templates/local-venv
                    "basedpyright-langserver")))

(eval-after-load 'lsp-javascript
  #'acg-templates/lsp-javascript-setup)

(eval-after-load 'lsp-pyright
  #'acg-templates/lsp-python-setup)

(defun acg-templates-setup ()
  (when buffer-file-name
    (let ((hop-outer (expand-file-name (rh-project-get-root)))
          venv-bin-path venv-path project-root)
      (when hop-outer
        (setq venv-bin-path (acg-templates/lsp-python-deps-providers-path ""))
        (setq venv-path (directory-file-name (file-name-directory venv-bin-path)))
        (setq project-root (directory-file-name (file-name-directory venv-path)))

        (cond
         ;; This is required as tsserver does not work with files in archives
         ((bound-and-true-p archive-subfile-mode)
          (company-mode 1))

         ((or (string-match-p "\\.py\\'\\|\\.pyi\\'" buffer-file-name)
              (string-match-p "^#!.*python"
                              (or (save-excursion
                                    (goto-char (point-min))
                                    (thing-at-point 'line t))
                                  "")))

          ;;; /b/; pyright-lsp config
          ;;; /b/{

          ;; (lsp-workspace-folders-add project-root)
          ;; Adding additional project-root non-persistent
          (cl-pushnew (lsp-f-canonical project-root)
                      (lsp-session-folders (lsp-session)) :test 'equal)

          ;; (setq-local lsp-pyright-venv-path project-root)
          ;; (setq-local lsp-pyright-venv-directory ".venv")

          (setq-local lsp-pyright-prefer-remote-env nil)
          (setq-local lsp-pyright-langserver-command "basedpyright")
          (setq-local lsp-pyright-python-executable-cmd
                      (file-name-concat venv-bin-path "python"))

          ;; (setq-local lsp-pyright-venv-path venv-path)
          ;; (setq-local lsp-pyright-python-executable-cmd "poetry run python")
          ;; (setq-local lsp-pyright-langserver-command-args
          ;;             `(,(file-name-concat venv-bin-path "pyright")
          ;;               "--stdio"))
          ;; (setq-local lsp-pyright-venv-directory venv-path)

          ;;; /b/}

          ;;; /b/; ruff-lsp config
          ;;; /b/{

          (setq-local lsp-ruff-server-command
                      `(,(file-name-concat venv-bin-path "ruff")
                        "server"))
          (setq-local lsp-ruff-python-path
                      (file-name-concat venv-bin-path "python"))

          ;;; /b/}

          ;;; /b/; Python black
          ;;; /b/{

          (setq-local blacken-executable
                      (file-name-concat venv-bin-path "black"))

          ;;; /b/}

          (setq-local lsp-enabled-clients '(pyright ruff))
          ;; (setq-local lsp-enabled-clients '(pyright))
          ;; (setq-local lsp-enabled-clients '(ruff))
          (setq-local lsp-before-save-edits nil)
          (setq-local lsp-modeline-diagnostics-enable nil)

          (blacken-mode 1)
          ;; (run-with-idle-timer 0 nil #'lsp)
          (lsp-deferred))

         ((string-match-p "\\.toml\\'" buffer-file-name)
          (run-with-idle-timer 0 nil #'prettier-mode))

         ((string-match-p "\\.json\\'" buffer-file-name)
          (run-with-idle-timer 0 nil #'prettier-mode))

         ((string-match-p "\\.yml\\'\\|\\.yaml\\'" buffer-file-name)
          (run-with-idle-timer 0 nil #'prettier-mode))

         ((string-match-p "\\.js\\'" buffer-file-name)
          (run-with-idle-timer 0 nil #'prettier-mode))

         ((string-match-p "\\.md\\'" buffer-file-name)
          (run-with-idle-timer 0 nil #'prettier-mode)))))))

;;; /b/}
"""


def generate(ctx: Context) -> str:
    project_name = ctx.template_config.project_name

    return Template(template_str).substitute(
        {
            "project_name_kebab": kebab_case(project_name),
        },
    )
