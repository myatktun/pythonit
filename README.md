# About

Just learning python by solving my own problems. This repository has python scripts that
convert markdown to rst and html. Markdown and html files are then synced with an S3 bucket.

## Pyenv and Python LSP Server

For pylsp to work with pyenv virtual environment, just set local pyenv version to both virtual
environment version and global version, by editing `.python-version` file or run

```
pyenv local <venv_version> <global_version>
```

Need to specify <venv_version> first, otherwise pyenv will default to global_version, and
require to activate virtual environment manually.

## File Converters

**Markdown to RST**

Markdown files are written in the format of

```md
# Main Header

1. [Section Header](#section-header)

##### [back to top](#main-header)

## Section Header

* [Section Content](#section-content)
* **Section Content** <a id="section-content"></a>
    - foo
    - **bar**
        >+ baz

##### [back to top](#main-header)
```

The converted rst files will be in the format of

```rst
Main Header
===========

1. `Section Header`_

`back to top <#main-header>`_

==============
Section Header
==============

* `Section Content`_

Section Content
---------------
    * foo
    * **bar**
        - baz

`back to top <#main-header>`_
```

rst files are converted to html using [Sphinx](https://www.sphinx-doc.org/en/master/).

## Environment Variables

Set the environment variables for MONGO_URI, DB_NAME, LOCAL_DIR and S3_BUCKET.

To convert markdown to rst, set environment variables for MD_DIR, RST_DIR.

To sync files with S3, set environment variables for LOCAL_DIR, LOCAL_HTML_DIR, S3_HTML_BUCKET,
S3_BUCKET.
