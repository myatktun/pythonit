# About

Just learning python by solving my own problems.

This repository has python scripts that convert markdown to rst and html. Markdown and html
files are then synced with AWS S3 bucket, and AWS Amplify is used to host a static website from
S3 files.

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

Markdown files are written in the format below.

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

The converted rst files will be in the format below.

```rst
===========
Main Header
===========

1. `Section Header`_

`back to top <#main-header>`_

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

**RST to HTML**

rst files are converted to html using [Sphinx](https://www.sphinx-doc.org/en/master/).

## Environment Variables

Set the environment variables for MONGO_URI, DB_NAME, LOCAL_DIR and S3_BUCKET.

To convert markdown to rst, set environment variables for MD_DIR, RST_DIR.

To sync files with S3, set environment variables for LOCAL_DIR, LOCAL_HTML_DIR, S3_HTML_BUCKET,
S3_BUCKET.

## Hosting Static Website with AWS S3 and Amplify

After html files are synced with S3, it is hosted using AWS Amplify.

Right now, I haven't figured out how to create and host using AWS CLI. The only workaround is
to zip all the html files, sync it to S3 and use it in the `aws amplify` command

S3 bucket need to have certain policies to allow Amplify to get objects while public access is
blocked. I'm currently using a bucket policy template generated when the site is manually
deployed using Amplify Console.

Create an Amplify app, and it will output an `<app-id>` to be used in other commands.

```sh
aws amplify create-app --name <app-name> --region <region-id>
```

Create a branch for the Amplify app.

```sh
aws amplify create-branch --region <region-id> --app-id <app-id> --branch-name <branch-name>
```

Update the S3 bucket policy in S3 Console using the template below. Edit `<branch-name>`,
`<bucket-name>`, `<account-id>`, `<region-id>`, and use the `<app-id>` generated from
`aws amplify create-app` command.

```json
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "AllowAmplifyToListPrefix_<app-id>_<branch-name>_",
            "Effect": "Allow",
            "Principal": {
                "Service": "amplify.amazonaws.com"
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::<bucket-name>",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<account-id>",
                    "s3:prefix": "",
                    "aws:SourceArn": "arn%3Aaws%3Aamplify%3A<region-id>%3A<account-id>%3Aapps%2F<app-id>%2Fbranches%2F<branch-name>"
                }
            }
        },
        {
            "Sid": "AllowAmplifyToReadPrefix_<app-id>_<branch-name>_",
            "Effect": "Allow",
            "Principal": {
                "Service": "amplify.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<bucket-name>/*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "<account-id>",
                    "aws:SourceArn": "arn%3Aaws%3Aamplify%3A<region-id>%3A<account-id>%3Aapps%2F<app-id>%2Fbranches%2F<branch-name>"
                }
            }
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::<bucket-name>/*",
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
```

Start Amplify deployment. You can also create it first.

```sh
aws amplify start-deployment --region <region-id> --app-id <app-id> --branch-name <branch-name> --source-url s3://<bucket-name>/<zip-file>
```

Can delete the Amplify app if no longer want it anymore.

```sh
aws amplify delete-app --app-id <app-id>
```
