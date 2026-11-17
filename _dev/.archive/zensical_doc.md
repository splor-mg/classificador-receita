Get started¶
Zensical is a modern static site generator designed to simplify building and maintaining project documentation. It's built by the creators of Material for MkDocs and shares the same core design principles and philosophy – batteries included, easy to use, with powerful customization options.

You can learn more about how both projects interconnect with each other here.

Installation¶
Zensical is written in Rust and Python, and is published as a Python package. We recommend to use a Python virtual environment when installing with pip or with uv. Both options automatically install all necessary dependencies alongside Zensical.

Prerequisites

You need to have Python and a Python package manager installed on your system before you install Zensical. We recommend you follow the Python Setup and Usage instructions for your operating system provided on the Python website. Modern Python distributions include the pip package manager, so unless you are developing Python software and use uv, this is the simplest option to install Zensical on your system.

Use with Docker

If you are familiar with Docker and wish to use Zensical in a container then you can use our official Docker image. For installation and usage instructions, see the documentation on Docker Hub.

Install with pip¶
Zensical can be installed into a virtual environment with pip.


 macOS
 Windows
 Linux
Open up a terminal window and install Zensical by first setting up a virtual environment and then using pip to install the Zensical package into it:


python3 -m venv .venv
source .venv/bin/activate
pip install zensical

Install with uv¶
If you are developing software using Python, chances are you're already using uv as a package manager, which has become popular in recent years. To install Zensical with uv, use:


 macOS
 Windows
 Linux

uv init
uv add zensical



-------------------


Create your site¶
After you've installed Zensical, you can bootstrap your project documentation using the zensical executable. Go to the directory where you want your project to be located and enter:


zensical new .
This creates the following structure:


.
├─ .github/
├─ docs/
│  ├─ index.md
│  └─ markdown.md
└─ zensical.toml
To learn more about the specific files and directories that are generated for you, please consult the usage guide for the new command.

Configuration¶
Zensical comes with many configuration options that have sensible defaults, which allows to build a documentation site with almost no configuration. site_name is the only required setting:1


[project]
site_name = "My site"
Unless you're building documentation for offline usage, it's strongly recommended to specify the site_url setting as well, since it's a prerequisite for the following features:

Instant navigation
Instant previews
Custom error pages
Preview as you write¶
Zensical includes a web server, so you can preview your documentation site as you write. The server will automatically rebuild the site when you make changes to source files. Start it with:


zensical serve
Point your browser to localhost:8000 and you should see:

Creating your site

Build your site¶
When you're finished editing, you can build a static site from your Markdown files with:


zensical build
The contents of this directory make up your project documentation. There's no need for operating a database or server, as it is completely self-contained. The site can be hosted on GitHub Pages, a CDN of your choice or your private web space.

If you intend to distribute your documentation as a set of files to be read from a local filesystem rather than a web server (such as in a .zip file), please consult the offline usage guide.

site_name is currently required because MkDocs, the static site generator Zensical replaces, requires it. We plan to make this setting optional in a future release. ↩



--------------

Publish your site¶
The great thing about hosting project documentation in a git repository is the ability to deploy it automatically when new changes are pushed. Zensical makes this ridiculously simple.

GitHub Pages¶
If you're already hosting your code on GitHub, GitHub Pages is certainly the most convenient way to publish your project documentation. It's free of charge and pretty easy to set up.

with GitHub Actions¶
Using GitHub Actions you can automate the deployment of your project documentation. At the root of your repository, create a new GitHub Actions workflow, e.g. .github/workflows/docs.yml, and copy and paste the following contents:


name: Documentation
on:
  push:
    branches:
      - master
      - main
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v5
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: 3.x
      - run: pip install zensical
      - run: zensical build --clean 
      - uses: actions/upload-pages-artifact@v4
        with:
          path: site
      - uses: actions/deploy-pages@v4
        id: deployment
When a new commit is pushed to the branch you are using for deployment (e.g. master or main), the static site is automatically built and deployed. Push your changes to see the workflow in action.

Your documentation should shortly appear at <username>.github.io/<repository>.

GitLab Pages¶
If you're hosting your code on GitLab, deploying to GitLab Pages can be done by using the GitLab CI task runner. At the root of your repository, create a task definition named .gitlab-ci.yml and copy and paste the following contents:


pages:
  stage: deploy
  image: python:latest
  script:
    - pip install zensical
    - zensical build --clean 
  pages:
    publish: public
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
Prerequisites

Make sure to change site_dir to public in your configuration as GitLab requires this.

When a new commit is pushed to the default branch (e.g. master or main), the static site is automatically built and deployed. Push your changes to see the workflow in action.

Your documentation is now published under <username>.gitlab.io/<repository>.


------------------------------

Customization¶
Zensical makes it easy to get started with a modern documentation site. However, sometimes you may want to adjust the look and feel of your documentation to better match your project's branding or to add custom functionality. This guide explains how you can customize Zensical.

Adding assets¶
Zensical offers several options for theme customization. To change the appearance of your pages, you can add your own CSS files located within your documentation directory. For more advanced modifications, you can include custom JavaScript code.

Additional CSS¶
To customize the appearance of your site, you can add a custom style sheet that overrides or extends Zensical’s default styles. Whether you want to adjust the design or apply specific branding, simply place your style sheet file within the docs directory:


zensical.toml
mkdocs.yml

.
├─ docs/
│  └─ stylesheets/
│     └─ extra.css
└─ zensical.toml
Then, add the following lines to zensical.toml:


[project]
extra_css = ["stylesheets/extra.css"]

Additional JavaScript¶
To enhance your documentation with custom functionality or interactive features, you can add JavaScript files to your project. Place your custom scripts within the docs directory:


zensical.toml
mkdocs.yml

.
├─ docs/
│  └─ javascripts/
│     └─ extra.js
└─ zensical.toml
Then, add the following lines to zensical.toml:


[project]
extra_javascript = ["javascripts/extra.js"]

Making sure your JavaScript code runs at the right time
It is likely that you will want to run some initialization code in your JavaScript once the page has been fully loaded by the browser. This means installing a callback function subscribing to events on the document$ observable exported by Zensical.

Using the document$ observable is particularly important if you are using instant navigation since it will not result in a page refresh in the browser, but subscribers on the observable will be notified.


document$.subscribe(function() {
  console.log("Initialize third-party libraries here")
})
Modules, async, defer¶
If you want to import code as a JavaScript module, you can simply make sure that the file has the .mjs extension or you can explicitly specify that it is to be loaded as a module:


zensical.toml
mkdocs.yml

[[project.extra_javascript]]
path = "javascripts/extra.js"
type = "module"

This configuration will result in a type="module" attribute being added to the <script> tag for the extra JavaScript.

Likewise, you can add defer and async attributes to the script tag to further influence how the JavaScript is loaded. For example, for the async case:


zensical.toml
mkdocs.yml

[[project.extra_javascript]]
path = "javascripts/extra.js"
async = true

Note that Zensical will auto-detect modules by looking at the file extension only when the extra_javascript element is plain text. That means that if you want to load a module using async, you also need to specify the type attribute.

Extending the theme¶
Zensical uses MiniJinja, a Rust-based template engine inspired by Python’s popular Jinja system, to render the HTML structure of your site – including the header, footer, and navigation sidebars. It rendered the entire scaffold of your documentation site, while the main content is generated from your Markdown files.

Templates are HTML files enhanced with MiniJinja instructions for dynamic rendering. The default page template is main.html, which inherits from base.html and includes additional templates found in the partials directory. The template can be customized per page.

Configuring overrides¶
To add new templates or to override parts of existing one, you first need to configure the custom_dir setting to point to a directory in which you store your template overrides:


zensical.toml
mkdocs.yml

[project.theme]
custom_dir = "overrides"

The custom_dir path is resolved relative to your configuration file.

Theme structure¶
In order to override theme templates, it's important to understand the file system structure, since any files you store in custom_dir override the templates and partials of the same name as they are provided by Zensical. Likewise, it's important to know what files exist if you want to add your new templates or partials:


.
├─ .icons/                             # Icon sets
├─ assets/
│  ├─ images/                          # Images and icons
│  ├─ javascripts/                     # JavaScript files
│  └─ stylesheets/                     # Style sheets
├─ partials/
│  ├─ integrations/                    # Third-party integrations
│  │  ├─ analytics/                    # Analytics integrations
│  │  └─ analytics.html                # Analytics setup
│  ├─ languages/                       # Translation languages
│  ├─ actions.html                     # Actions
│  ├─ alternate.html                   # Site language selector
│  ├─ comments.html                    # Comment system (empty by default)
│  ├─ consent.html                     # Consent
│  ├─ content.html                     # Page content
│  ├─ copyright.html                   # Copyright and theme information
│  ├─ feedback.html                    # Was this page helpful?
│  ├─ footer.html                      # Footer bar
│  ├─ header.html                      # Header bar
│  ├─ icons.html                       # Custom icons
│  ├─ language.html                    # Translation setup
│  ├─ logo.html                        # Logo in header and sidebar
│  ├─ nav.html                         # Main navigation
│  ├─ nav-item.html                    # Main navigation item
│  ├─ palette.html                     # Color palette toggle
│  ├─ progress.html                    # Progress indicator
│  ├─ search.html                      # Search interface
│  ├─ social.html                      # Social links
│  ├─ source.html                      # Repository information
│  ├─ source-file.html                 # Source file information
│  ├─ tabs.html                        # Tabs navigation
│  ├─ tabs-item.html                   # Tabs navigation item
│  ├─ tags.html                        # Tags
│  ├─ toc.html                         # Table of contents
│  ├─ toc-item.html                    # Table of contents item
│  └─ top.html                         # Back-to-top button
├─ 404.html                            # 404 error page
├─ base.html                           # Base template
└─ main.html                           # Default page
Custom templates¶
Some of your pages may need a different structure. Say, you want to have a custom layout for the homepage of your documentation site, for reference pages or your blog posts. You can use the template language provided by MiniJinja to produce any HTML structure you like. Use the templates provided by Zensical as a starter or start from a clean slate.

Add a new template to the overrides directory you configured. Make sure its name is not the same as one of the files provided by Zensical (such as main.html and base.html). Now you can specify which template should be used for a page by adding the template option to the page header:


---
template: "my_template.html"
---

# Page title

...
Custom error pages¶
The overrides directory is also the place for adding a 404 error page, which can be configured as a fallback in your web server. If you set custom_dir to overrides, use the following layout:


├─ overrides/
│  └─ 404.html
└─ zensical.toml
Note that Zensical provides a default 404.html template.

Template overrides¶
There are two methods to override templates: You can either override entire templates or partials, or you can override specific blocks within templates, which is the recommended approach.

For more information, refer to the Jinja Template Designer Documentation.

Overriding blocks recommended¶
Zensical templates contain blocks that wrap specific features and that can be re-defined or extended by an override. Zensical defines a main.html template that inherits all its functionality from base.html. The most robust way of making changes via overrides is therefore to override main.html instead of base.html, which is more likely to change in future versions of Zensical.

In order to set up block overrides, create a main.html file inside the overrides directory:


.
└─ overrides/
   └─ main.html
Then, e.g. to override the site title, add the following lines to main.html:


{% extends "base.html" %}

{% block htmltitle %}
  <title>Lorem ipsum dolor sit amet</title>
{% endblock %}
If you intend to add something to a block rather than to replace it altogether with new content, use {{ super() }} inside the block to include the original block content. This is particularly useful when adding third-party scripts to your docs, e.g.


{% extends "base.html" %}

{% block scripts %}
  <!-- Add scripts that need to run before here -->
  {{ super() }}
  <!-- Add scripts that need to run afterwards here -->
{% endblock %}
The following template blocks are provided by the theme:

Block name	Purpose
analytics	Wraps the Google Analytics integration
announce	Wraps the announcement bar
config	Wraps the JavaScript application config
container	Wraps the main content container
content	Wraps the main content
extrahead	Empty block to add custom meta tags
fonts	Wraps the font definitions
footer	Wraps the footer with navigation and copyright
header	Wraps the fixed header bar
hero	Wraps the hero teaser (if available)
htmltitle	Wraps the <title> tag
libs	Wraps the JavaScript libraries (header)
outdated	Wraps the version warning
scripts	Wraps the JavaScript application (footer)
site_meta	Wraps the meta tags in the document head
site_nav	Wraps the site navigation and table of contents
styles	Wraps the style sheets (also extra sources)
tabs	Wraps the tabs navigation (if available)
Overriding partials¶
In order to override a partial, you can replace it with a file of the same name and location in the overrides directory. For example, to replace the original footer.html partial, create a new footer.html partial in the overrides directory:


.
└─ overrides/
   └─ partials/
      └─ footer.html
Zensical will now use the new partial when rendering the theme.



---------------------------------
How to upgrade¶
Check the changelog to identify the version you would like to upgrade to. Remember that Zensical uses semantic versioning, so if you are upgrading from one major release version to another, please carefully study the information provided on versioning of Zensical.

Once you are ready to proceed, follow the instructions according to how you installed Zensical:


with pip
with uv
Make sure you have the correct virtual environment activated that you want to upgrade, then:


pip install --upgrade --force-reinstall zensical
To show the currently installed version, use:


pip show zensical

Versioning¶
Zensical follows semantic versioning and currently uses 0.0.x versioning (alpha / development releases). We're approaching a beta release, after which we'll transition to 0.x versioning. Once we reach a stable 1.0 release, the standard semantic versioning rules will apply more strictly.




------------------------------------------








