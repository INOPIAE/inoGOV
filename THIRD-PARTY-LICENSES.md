# Third-Party Licenses

This document lists the third-party software components used in the
inoGOV application and the license information available for them.

## License Compatibility

The project is distributed under GNU Affero General Public License v3.0
or later (AGPL-3.0-or-later), if that is the license selected for the
project. The presence of a license in this inventory is not, by itself,
a legal compatibility assessment. Review each license, notices, and
distribution obligations before release.

------------------------------------------------------------------------

## Backend Dependencies (Python)

The following direct requirements were taken from the provided
`requirements.txt`. They are version constraints, not a record of the
exact installed versions. Transitive Python dependencies are not
included because a resolved `uv.lock` or equivalent installed-package
inventory was not provided.

### Core Framework & Web Server

#### FastAPI

-   **License:** MIT License
-   **Requirement:** `>=0.115`
-   **Description:** Modern, fast web framework for building APIs
-   **Homepage:** https://fastapi.tiangolo.com/
-   **License Text:**
    https://github.com/fastapi/fastapi/blob/master/LICENSE

#### Uvicorn

-   **License:** BSD 3-Clause License
-   **Requirement:** `>=0.30`
-   **Description:** ASGI web server implementation
-   **Homepage:** https://www.uvicorn.org/
-   **License Text:**
    https://github.com/encode/uvicorn/blob/master/LICENSE.md

### Database & Migrations

#### SQLAlchemy

-   **License:** MIT License
-   **Requirement:** `>=2.0`
-   **Description:** SQL toolkit and Object-Relational Mapping (ORM)
    library
-   **Homepage:** https://www.sqlalchemy.org/
-   **License Text:**
    https://github.com/sqlalchemy/sqlalchemy/blob/main/LICENSE

#### Alembic

-   **License:** MIT License
-   **Requirement:** `>=1.13`
-   **Description:** Database migration tool for SQLAlchemy
-   **Homepage:** https://alembic.sqlalchemy.org/
-   **License Text:**
    https://github.com/sqlalchemy/alembic/blob/main/LICENSE

#### Psycopg (binary extra)

-   **License:** LGPL-3.0-or-later (verify bundled components
    separately)
-   **Requirement:** `>=3.2`
-   **Description:** PostgreSQL database adapter for Python; binary
    extra may include separately licensed native components
-   **Homepage:** https://www.psycopg.org/
-   **License Text:**
    https://github.com/psycopg/psycopg/blob/master/LICENSE.txt

### Data Validation & Serialization

#### Pydantic Settings

-   **License:** MIT License
-   **Requirement:** `>=2.4`
-   **Description:** Settings management using Pydantic
-   **Homepage:**
    https://docs.pydantic.dev/latest/concepts/pydantic_settings/
-   **License Text:**
    https://github.com/pydantic/pydantic-settings/blob/main/LICENSE

#### Email-validator

-   **License:** CC0-1.0
-   **Requirement:** `>=2.2`
-   **Description:** Email address validation library
-   **Homepage:** https://github.com/JoshData/python-email-validator
-   **License Text:**
    https://github.com/JoshData/python-email-validator/blob/main/LICENSE

#### Openpyxl

-   **License:** MIT License
-   **Requirement:** `>=3.1`
-   **Description:** Library for reading and writing Excel XLSX/XLSM
    files
-   **Homepage:** https://openpyxl.readthedocs.io/
-   **License Text:**
    https://foss.heptapod.net/openpyxl/openpyxl/-/blob/branch/3.1/LICENCE.rst

### Security & Authentication

#### PyJWT

-   **License:** MIT License
-   **Requirement:** `>=2.9`
-   **Description:** JSON Web Token implementation
-   **Homepage:** https://pyjwt.readthedocs.io/
-   **License Text:**
    https://github.com/jpadilla/pyjwt/blob/master/LICENSE

#### pwdlib

-   **License:** MIT License
-   **Requirement:** `>=0.2`
-   **Description:** Password hashing helper library
-   **Homepage:** https://github.com/frankie567/pwdlib
-   **License Text:**
    https://github.com/frankie567/pwdlib/blob/main/LICENSE

#### PyOTP

-   **License:** MIT License
-   **Requirement:** `>=2.9`
-   **Description:** Python One-Time Password Library
-   **Homepage:** https://github.com/pyauth/pyotp
-   **License Text:**
    https://github.com/pyauth/pyotp/blob/develop/LICENSE

### Utilities & File Handling

#### python-multipart

-   **License:** Apache License 2.0
-   **Requirement:** `>=0.0.9`
-   **Description:** Streaming multipart parser for Python
-   **Homepage:** https://github.com/Kludex/python-multipart
-   **License Text:**
    https://github.com/Kludex/python-multipart/blob/master/LICENSE.txt

### Development & Testing

#### pytest

-   **License:** MIT License
-   **Requirement:** `>=8.0`
-   **Description:** Testing framework
-   **Homepage:** https://pytest.org/
-   **License Text:**
    https://github.com/pytest-dev/pytest/blob/main/LICENSE

#### HTTPX

-   **License:** BSD 3-Clause License
-   **Requirement:** `>=0.27`
-   **Description:** HTTP client for Python
-   **Homepage:** https://www.python-httpx.org/
-   **License Text:**
    https://github.com/encode/httpx/blob/master/LICENSE.md

------------------------------------------------------------------------

## Frontend Dependencies (JavaScript/Node.js)

The npm inventory below includes resolved package versions found in the
supplied `package-lock.json`, including transitive dependencies. License
identifiers are copied from the lockfile; they have not been
independently verified against each package's license file.

-   **Packages listed:** 216
-   **Lockfile version:** 3

### All npm Packages

#### @asamuzakjp/css-color

-   **License:** MIT
-   **Version:** `5.1.11`
-   **Package Information:**
    https://www.npmjs.com/package/@asamuzakjp/css-color
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@asamuzakjp/css-color
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @asamuzakjp/dom-selector

-   **License:** MIT
-   **Version:** `7.1.1`
-   **Package Information:**
    https://www.npmjs.com/package/@asamuzakjp/dom-selector
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@asamuzakjp/dom-selector
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @asamuzakjp/generational-cache

-   **License:** MIT
-   **Version:** `1.0.1`
-   **Package Information:**
    https://www.npmjs.com/package/@asamuzakjp/generational-cache
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@asamuzakjp/generational-cache
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @asamuzakjp/nwsapi

-   **License:** MIT
-   **Version:** `2.3.9`
-   **Package Information:**
    https://www.npmjs.com/package/@asamuzakjp/nwsapi
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@asamuzakjp/nwsapi
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @babel/helper-string-parser

-   **License:** MIT
-   **Version:** `7.29.7`
-   **Package Information:**
    https://www.npmjs.com/package/@babel/helper-string-parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/helper-string-parser
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/helper-string-parser

-   **License:** MIT
-   **Version:** `8.0.6`
-   **Package Information:**
    https://www.npmjs.com/package/@babel/helper-string-parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/helper-string-parser
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/helper-validator-identifier

-   **License:** MIT
-   **Version:** `7.29.7`
-   **Package Information:**
    https://www.npmjs.com/package/@babel/helper-validator-identifier
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/helper-validator-identifier
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/helper-validator-identifier

-   **License:** MIT
-   **Version:** `8.0.6`
-   **Package Information:**
    https://www.npmjs.com/package/@babel/helper-validator-identifier
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/helper-validator-identifier
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/parser

-   **License:** MIT
-   **Version:** `7.29.9`
-   **Package Information:** https://www.npmjs.com/package/@babel/parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/parser
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/parser

-   **License:** MIT
-   **Version:** `8.0.7`
-   **Package Information:** https://www.npmjs.com/package/@babel/parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/parser
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/types

-   **License:** MIT
-   **Version:** `7.29.8`
-   **Package Information:** https://www.npmjs.com/package/@babel/types
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/types
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @babel/types

-   **License:** MIT
-   **Version:** `8.0.6`
-   **Package Information:** https://www.npmjs.com/package/@babel/types
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@babel/types
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @bramus/specificity

-   **License:** MIT
-   **Version:** `2.4.3`
-   **Package Information:**
    https://www.npmjs.com/package/@bramus/specificity
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@bramus/specificity
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/color-helpers

-   **License:** MIT-0
-   **Version:** `6.1.2`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/color-helpers
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/color-helpers
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/css-calc

-   **License:** MIT
-   **Version:** `3.4.3`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/css-calc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/css-calc
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/css-color-parser

-   **License:** MIT
-   **Version:** `4.2.6`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/css-color-parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/css-color-parser
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/css-parser-algorithms

-   **License:** MIT
-   **Version:** `4.0.2`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/css-parser-algorithms
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/css-parser-algorithms
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/css-syntax-patches-for-csstree

-   **License:** MIT-0
-   **Version:** `1.1.15`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/css-syntax-patches-for-csstree
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/css-syntax-patches-for-csstree
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @csstools/css-tokenizer

-   **License:** MIT
-   **Version:** `4.0.2`
-   **Package Information:**
    https://www.npmjs.com/package/@csstools/css-tokenizer
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@csstools/css-tokenizer
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @exodus/bytes

-   **License:** MIT
-   **Version:** `1.16.0`
-   **Package Information:** https://www.npmjs.com/package/@exodus/bytes
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@exodus/bytes
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @jridgewell/gen-mapping

-   **License:** MIT
-   **Version:** `0.3.13`
-   **Package Information:**
    https://www.npmjs.com/package/@jridgewell/gen-mapping
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@jridgewell/gen-mapping
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @jridgewell/remapping

-   **License:** MIT
-   **Version:** `2.3.5`
-   **Package Information:**
    https://www.npmjs.com/package/@jridgewell/remapping
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@jridgewell/remapping
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @jridgewell/resolve-uri

-   **License:** MIT
-   **Version:** `3.1.2`
-   **Package Information:**
    https://www.npmjs.com/package/@jridgewell/resolve-uri
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@jridgewell/resolve-uri
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @jridgewell/sourcemap-codec

-   **License:** MIT
-   **Version:** `1.6.0`
-   **Package Information:**
    https://www.npmjs.com/package/@jridgewell/sourcemap-codec
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@jridgewell/sourcemap-codec
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @jridgewell/trace-mapping

-   **License:** MIT
-   **Version:** `0.3.31`
-   **Package Information:**
    https://www.npmjs.com/package/@jridgewell/trace-mapping
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@jridgewell/trace-mapping
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @one-ini/wasm

-   **License:** MIT
-   **Version:** `0.2.1`
-   **Package Information:** https://www.npmjs.com/package/@one-ini/wasm
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@one-ini/wasm
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @oxc-project/types

-   **License:** MIT
-   **Version:** `0.153.0`
-   **Package Information:**
    https://www.npmjs.com/package/@oxc-project/types
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@oxc-project/types
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @popperjs/core

-   **License:** MIT
-   **Version:** `2.11.8`
-   **Package Information:**
    https://www.npmjs.com/package/@popperjs/core
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@popperjs/core
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-android-arm-eabi

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-android-arm-eabi
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-android-arm-eabi
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-android-arm64

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-android-arm64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-android-arm64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-darwin-arm64

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-darwin-arm64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-darwin-arm64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-darwin-x64

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-darwin-x64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-darwin-x64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-freebsd-x64

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-freebsd-x64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-freebsd-x64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-arm-gnueabihf

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm-gnueabihf
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm-gnueabihf
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-arm64-gnu

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm64-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm64-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-arm64-musl

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm64-musl
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-arm64-musl
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-ppc64-gnu

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-ppc64-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-ppc64-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-s390x-gnu

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-s390x-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-s390x-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-x64-gnu

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-x64-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-x64-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-linux-x64-musl

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-linux-x64-musl
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-linux-x64-musl
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-openharmony-arm64

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-openharmony-arm64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-openharmony-arm64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-win32-arm64-msvc

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-win32-arm64-msvc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-win32-arm64-msvc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/binding-win32-x64-msvc

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/binding-win32-x64-msvc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/binding-win32-x64-msvc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @rolldown/pluginutils

-   **License:** MIT
-   **Version:** `1.0.1`
-   **Package Information:**
    https://www.npmjs.com/package/@rolldown/pluginutils
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@rolldown/pluginutils
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @types/chai

-   **License:** MIT
-   **Version:** `5.2.3`
-   **Package Information:** https://www.npmjs.com/package/@types/chai
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@types/chai
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @types/deep-eql

-   **License:** MIT
-   **Version:** `4.0.2`
-   **Package Information:**
    https://www.npmjs.com/package/@types/deep-eql
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@types/deep-eql
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @types/estree

-   **License:** MIT
-   **Version:** `1.0.9`
-   **Package Information:** https://www.npmjs.com/package/@types/estree
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@types/estree
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vitejs/plugin-vue

-   **License:** MIT
-   **Version:** `6.0.9`
-   **Package Information:**
    https://www.npmjs.com/package/@vitejs/plugin-vue
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vitejs/plugin-vue
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @vitest/mocker

-   **License:** MIT
-   **Version:** `5.0.3`
-   **Package Information:**
    https://www.npmjs.com/package/@vitest/mocker
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vitest/mocker
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @vitest/spy

-   **License:** MIT
-   **Version:** `5.0.3`
-   **Package Information:** https://www.npmjs.com/package/@vitest/spy
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vitest/spy
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### @vue-macros/common

-   **License:** MIT
-   **Version:** `3.1.4`
-   **Package Information:**
    https://www.npmjs.com/package/@vue-macros/common
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue-macros/common
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/compiler-core

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/compiler-core
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/compiler-core
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/compiler-dom

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/compiler-dom
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/compiler-dom
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/compiler-sfc

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/compiler-sfc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/compiler-sfc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/compiler-ssr

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/compiler-ssr
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/compiler-ssr
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/devtools-api

-   **License:** MIT
-   **Version:** `8.2.1`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/devtools-api
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/devtools-api
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/devtools-kit

-   **License:** MIT
-   **Version:** `8.2.1`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/devtools-kit
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/devtools-kit
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/devtools-shared

-   **License:** MIT
-   **Version:** `8.2.1`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/devtools-shared
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/devtools-shared
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/reactivity

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/reactivity
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/reactivity
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/runtime-core

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/runtime-core
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/runtime-core
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/runtime-dom

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/runtime-dom
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/runtime-dom
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/server-renderer

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/server-renderer
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/server-renderer
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/shared

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:** https://www.npmjs.com/package/@vue/shared
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/shared
-   **Dependency Type:** Runtime dependency or transitive dependency

#### @vue/test-utils

-   **License:** MIT
-   **Version:** `2.5.1`
-   **Package Information:**
    https://www.npmjs.com/package/@vue/test-utils
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/@vue/test-utils
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### abbrev

-   **License:** ISC
-   **Version:** `5.0.0`
-   **Package Information:** https://www.npmjs.com/package/abbrev
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/abbrev
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### acorn

-   **License:** MIT
-   **Version:** `8.19.0`
-   **Package Information:** https://www.npmjs.com/package/acorn
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/acorn
-   **Dependency Type:** Runtime dependency or transitive dependency

#### ansi-regex

-   **License:** MIT
-   **Version:** `5.0.1`
-   **Package Information:** https://www.npmjs.com/package/ansi-regex
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ansi-regex
-   **Dependency Type:** Runtime dependency or transitive dependency

#### ansi-styles

-   **License:** MIT
-   **Version:** `4.3.0`
-   **Package Information:** https://www.npmjs.com/package/ansi-styles
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ansi-styles
-   **Dependency Type:** Runtime dependency or transitive dependency

#### array-back

-   **License:** MIT
-   **Version:** `6.2.3`
-   **Package Information:** https://www.npmjs.com/package/array-back
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/array-back
-   **Dependency Type:** Runtime dependency or transitive dependency

#### assertion-error

-   **License:** MIT
-   **Version:** `2.0.1`
-   **Package Information:**
    https://www.npmjs.com/package/assertion-error
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/assertion-error
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### ast-kit

-   **License:** MIT
-   **Version:** `2.2.0`
-   **Package Information:** https://www.npmjs.com/package/ast-kit
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ast-kit
-   **Dependency Type:** Runtime dependency or transitive dependency

#### ast-kit

-   **License:** MIT
-   **Version:** `3.0.0`
-   **Package Information:** https://www.npmjs.com/package/ast-kit
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ast-kit
-   **Dependency Type:** Runtime dependency or transitive dependency

#### ast-walker-scope

-   **License:** MIT
-   **Version:** `0.10.0`
-   **Package Information:**
    https://www.npmjs.com/package/ast-walker-scope
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ast-walker-scope
-   **Dependency Type:** Runtime dependency or transitive dependency

#### balanced-match

-   **License:** MIT
-   **Version:** `4.0.4`
-   **Package Information:**
    https://www.npmjs.com/package/balanced-match
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/balanced-match
-   **Dependency Type:** Runtime dependency or transitive dependency

#### bidi-js

-   **License:** MIT
-   **Version:** `1.1.0`
-   **Package Information:** https://www.npmjs.com/package/bidi-js
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/bidi-js
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### birpc

-   **License:** MIT
-   **Version:** `2.9.0`
-   **Package Information:** https://www.npmjs.com/package/birpc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/birpc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### bootstrap

-   **License:** MIT
-   **Version:** `5.3.8`
-   **Package Information:** https://www.npmjs.com/package/bootstrap
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/bootstrap
-   **Dependency Type:** Runtime dependency or transitive dependency

#### brace-expansion

-   **License:** MIT
-   **Version:** `5.0.12`
-   **Package Information:**
    https://www.npmjs.com/package/brace-expansion
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/brace-expansion
-   **Dependency Type:** Runtime dependency or transitive dependency

#### camelcase

-   **License:** MIT
-   **Version:** `5.3.1`
-   **Package Information:** https://www.npmjs.com/package/camelcase
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/camelcase
-   **Dependency Type:** Runtime dependency or transitive dependency

#### chai

-   **License:** MIT
-   **Version:** `6.3.0`
-   **Package Information:** https://www.npmjs.com/package/chai
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/chai
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### chokidar

-   **License:** MIT
-   **Version:** `5.0.0`
-   **Package Information:** https://www.npmjs.com/package/chokidar
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/chokidar
-   **Dependency Type:** Runtime dependency or transitive dependency

#### cliui

-   **License:** ISC
-   **Version:** `6.0.0`
-   **Package Information:** https://www.npmjs.com/package/cliui
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/cliui
-   **Dependency Type:** Runtime dependency or transitive dependency

#### color-convert

-   **License:** MIT
-   **Version:** `2.0.1`
-   **Package Information:** https://www.npmjs.com/package/color-convert
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/color-convert
-   **Dependency Type:** Runtime dependency or transitive dependency

#### color-name

-   **License:** MIT
-   **Version:** `1.1.4`
-   **Package Information:** https://www.npmjs.com/package/color-name
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/color-name
-   **Dependency Type:** Runtime dependency or transitive dependency

#### command-line-args

-   **License:** MIT
-   **Version:** `6.0.2`
-   **Package Information:**
    https://www.npmjs.com/package/command-line-args
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/command-line-args
-   **Dependency Type:** Runtime dependency or transitive dependency

#### commander

-   **License:** MIT
-   **Version:** `14.0.3`
-   **Package Information:** https://www.npmjs.com/package/commander
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/commander
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### confbox

-   **License:** MIT
-   **Version:** `0.3.1`
-   **Package Information:** https://www.npmjs.com/package/confbox
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/confbox
-   **Dependency Type:** Runtime dependency or transitive dependency

#### confbox

-   **License:** MIT
-   **Version:** `0.1.8`
-   **Package Information:** https://www.npmjs.com/package/confbox
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/confbox
-   **Dependency Type:** Runtime dependency or transitive dependency

#### config-chain

-   **License:** MIT
-   **Version:** `1.1.13`
-   **Package Information:** https://www.npmjs.com/package/config-chain
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/config-chain
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### css-tree

-   **License:** MIT
-   **Version:** `3.2.1`
-   **Package Information:** https://www.npmjs.com/package/css-tree
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/css-tree
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### csstype

-   **License:** MIT
-   **Version:** `3.2.3`
-   **Package Information:** https://www.npmjs.com/package/csstype
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/csstype
-   **Dependency Type:** Runtime dependency or transitive dependency

#### data-urls

-   **License:** MIT
-   **Version:** `7.0.0`
-   **Package Information:** https://www.npmjs.com/package/data-urls
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/data-urls
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### decamelize

-   **License:** MIT
-   **Version:** `1.2.0`
-   **Package Information:** https://www.npmjs.com/package/decamelize
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/decamelize
-   **Dependency Type:** Runtime dependency or transitive dependency

#### decimal.js

-   **License:** MIT
-   **Version:** `10.6.0`
-   **Package Information:** https://www.npmjs.com/package/decimal.js
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/decimal.js
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### detect-libc

-   **License:** Apache-2.0
-   **Version:** `2.1.2`
-   **Package Information:** https://www.npmjs.com/package/detect-libc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/detect-libc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### dijkstrajs

-   **License:** MIT
-   **Version:** `1.0.3`
-   **Package Information:** https://www.npmjs.com/package/dijkstrajs
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/dijkstrajs
-   **Dependency Type:** Runtime dependency or transitive dependency

#### editorconfig

-   **License:** MIT
-   **Version:** `3.0.2`
-   **Package Information:** https://www.npmjs.com/package/editorconfig
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/editorconfig
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### emoji-regex

-   **License:** MIT
-   **Version:** `8.0.0`
-   **Package Information:** https://www.npmjs.com/package/emoji-regex
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/emoji-regex
-   **Dependency Type:** Runtime dependency or transitive dependency

#### entities

-   **License:** BSD-2-Clause
-   **Version:** `7.0.1`
-   **Package Information:** https://www.npmjs.com/package/entities
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/entities
-   **Dependency Type:** Runtime dependency or transitive dependency

#### entities

-   **License:** BSD-2-Clause
-   **Version:** `8.1.0`
-   **Package Information:** https://www.npmjs.com/package/entities
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/entities
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### es-module-lexer

-   **License:** MIT
-   **Version:** `2.3.2`
-   **Package Information:**
    https://www.npmjs.com/package/es-module-lexer
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/es-module-lexer
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### estree-walker

-   **License:** MIT
-   **Version:** `3.0.3`
-   **Package Information:** https://www.npmjs.com/package/estree-walker
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/estree-walker
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### estree-walker

-   **License:** MIT
-   **Version:** `3.0.3`
-   **Package Information:** https://www.npmjs.com/package/estree-walker
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/estree-walker
-   **Dependency Type:** Runtime dependency or transitive dependency

#### estree-walker

-   **License:** MIT
-   **Version:** `2.0.2`
-   **Package Information:** https://www.npmjs.com/package/estree-walker
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/estree-walker
-   **Dependency Type:** Runtime dependency or transitive dependency

#### expect-type

-   **License:** Apache-2.0
-   **Version:** `1.4.0`
-   **Package Information:** https://www.npmjs.com/package/expect-type
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/expect-type
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### exsolve

-   **License:** MIT
-   **Version:** `1.1.3`
-   **Package Information:** https://www.npmjs.com/package/exsolve
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/exsolve
-   **Dependency Type:** Runtime dependency or transitive dependency

#### fdir

-   **License:** MIT
-   **Version:** `6.5.0`
-   **Package Information:** https://www.npmjs.com/package/fdir
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/fdir
-   **Dependency Type:** Runtime dependency or transitive dependency

#### find-replace

-   **License:** MIT
-   **Version:** `5.0.2`
-   **Package Information:** https://www.npmjs.com/package/find-replace
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/find-replace
-   **Dependency Type:** Runtime dependency or transitive dependency

#### find-up

-   **License:** MIT
-   **Version:** `4.1.0`
-   **Package Information:** https://www.npmjs.com/package/find-up
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/find-up
-   **Dependency Type:** Runtime dependency or transitive dependency

#### fsevents

-   **License:** MIT
-   **Version:** `2.3.3`
-   **Package Information:** https://www.npmjs.com/package/fsevents
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/fsevents
-   **Dependency Type:** Runtime dependency or transitive dependency

#### get-caller-file

-   **License:** ISC
-   **Version:** `2.0.5`
-   **Package Information:**
    https://www.npmjs.com/package/get-caller-file
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/get-caller-file
-   **Dependency Type:** Runtime dependency or transitive dependency

#### glob

-   **License:** BlueOak-1.0.0
-   **Version:** `13.0.6`
-   **Package Information:** https://www.npmjs.com/package/glob
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/glob
-   **Dependency Type:** Runtime dependency or transitive dependency

#### hookable

-   **License:** MIT
-   **Version:** `5.5.3`
-   **Package Information:** https://www.npmjs.com/package/hookable
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/hookable
-   **Dependency Type:** Runtime dependency or transitive dependency

#### html-encoding-sniffer

-   **License:** MIT
-   **Version:** `6.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/html-encoding-sniffer
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/html-encoding-sniffer
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### ini

-   **License:** ISC
-   **Version:** `1.3.8`
-   **Package Information:** https://www.npmjs.com/package/ini
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ini
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### is-fullwidth-code-point

-   **License:** MIT
-   **Version:** `3.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/is-fullwidth-code-point
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/is-fullwidth-code-point
-   **Dependency Type:** Runtime dependency or transitive dependency

#### is-potential-custom-element-name

-   **License:** MIT
-   **Version:** `1.0.1`
-   **Package Information:**
    https://www.npmjs.com/package/is-potential-custom-element-name
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/is-potential-custom-element-name
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### js-beautify

-   **License:** MIT
-   **Version:** `2.0.3`
-   **Package Information:** https://www.npmjs.com/package/js-beautify
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/js-beautify
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### js-cookie

-   **License:** MIT
-   **Version:** `3.0.8`
-   **Package Information:** https://www.npmjs.com/package/js-cookie
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/js-cookie
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### jsdom

-   **License:** MIT
-   **Version:** `29.1.1`
-   **Package Information:** https://www.npmjs.com/package/jsdom
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/jsdom
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### lightningcss

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:** https://www.npmjs.com/package/lightningcss
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-android-arm64

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-android-arm64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-android-arm64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-darwin-arm64

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-darwin-arm64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-darwin-arm64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-darwin-x64

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-darwin-x64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-darwin-x64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-freebsd-x64

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-freebsd-x64
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-freebsd-x64
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-linux-arm-gnueabihf

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-linux-arm-gnueabihf
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-linux-arm-gnueabihf
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-linux-arm64-gnu

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-linux-arm64-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-linux-arm64-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-linux-arm64-musl

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-linux-arm64-musl
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-linux-arm64-musl
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-linux-x64-gnu

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-linux-x64-gnu
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-linux-x64-gnu
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-linux-x64-musl

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-linux-x64-musl
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-linux-x64-musl
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-win32-arm64-msvc

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-win32-arm64-msvc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-win32-arm64-msvc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lightningcss-win32-x64-msvc

-   **License:** MPL-2.0
-   **Version:** `1.33.0`
-   **Package Information:**
    https://www.npmjs.com/package/lightningcss-win32-x64-msvc
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lightningcss-win32-x64-msvc
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lilconfig

-   **License:** MIT
-   **Version:** `3.1.3`
-   **Package Information:** https://www.npmjs.com/package/lilconfig
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lilconfig
-   **Dependency Type:** Runtime dependency or transitive dependency

#### local-pkg

-   **License:** MIT
-   **Version:** `1.2.1`
-   **Package Information:** https://www.npmjs.com/package/local-pkg
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/local-pkg
-   **Dependency Type:** Runtime dependency or transitive dependency

#### locate-path

-   **License:** MIT
-   **Version:** `5.0.0`
-   **Package Information:** https://www.npmjs.com/package/locate-path
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/locate-path
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lodash.camelcase

-   **License:** MIT
-   **Version:** `4.3.0`
-   **Package Information:**
    https://www.npmjs.com/package/lodash.camelcase
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lodash.camelcase
-   **Dependency Type:** Runtime dependency or transitive dependency

#### lru-cache

-   **License:** BlueOak-1.0.0
-   **Version:** `11.5.3`
-   **Package Information:** https://www.npmjs.com/package/lru-cache
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/lru-cache
-   **Dependency Type:** Runtime dependency or transitive dependency

#### magic-string

-   **License:** MIT
-   **Version:** `1.4.3`
-   **Package Information:** https://www.npmjs.com/package/magic-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/magic-string
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### magic-string

-   **License:** MIT
-   **Version:** `0.30.21`
-   **Package Information:** https://www.npmjs.com/package/magic-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/magic-string
-   **Dependency Type:** Runtime dependency or transitive dependency

#### magic-string

-   **License:** MIT
-   **Version:** `1.4.3`
-   **Package Information:** https://www.npmjs.com/package/magic-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/magic-string
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### magic-string

-   **License:** MIT
-   **Version:** `1.4.3`
-   **Package Information:** https://www.npmjs.com/package/magic-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/magic-string
-   **Dependency Type:** Runtime dependency or transitive dependency

#### magic-string-ast

-   **License:** MIT
-   **Version:** `1.0.3`
-   **Package Information:**
    https://www.npmjs.com/package/magic-string-ast
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/magic-string-ast
-   **Dependency Type:** Runtime dependency or transitive dependency

#### mdn-data

-   **License:** CC0-1.0
-   **Version:** `2.27.1`
-   **Package Information:** https://www.npmjs.com/package/mdn-data
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/mdn-data
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### minimatch

-   **License:** BlueOak-1.0.0
-   **Version:** `10.2.6`
-   **Package Information:** https://www.npmjs.com/package/minimatch
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/minimatch
-   **Dependency Type:** Runtime dependency or transitive dependency

#### minipass

-   **License:** BlueOak-1.0.0
-   **Version:** `7.1.3`
-   **Package Information:** https://www.npmjs.com/package/minipass
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/minipass
-   **Dependency Type:** Runtime dependency or transitive dependency

#### mlly

-   **License:** MIT
-   **Version:** `1.8.2`
-   **Package Information:** https://www.npmjs.com/package/mlly
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/mlly
-   **Dependency Type:** Runtime dependency or transitive dependency

#### muggle-string

-   **License:** MIT
-   **Version:** `0.4.1`
-   **Package Information:** https://www.npmjs.com/package/muggle-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/muggle-string
-   **Dependency Type:** Runtime dependency or transitive dependency

#### nanoid

-   **License:** MIT
-   **Version:** `3.3.20`
-   **Package Information:** https://www.npmjs.com/package/nanoid
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/nanoid
-   **Dependency Type:** Runtime dependency or transitive dependency

#### nopt

-   **License:** ISC
-   **Version:** `10.0.1`
-   **Package Information:** https://www.npmjs.com/package/nopt
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/nopt
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### nostics

-   **License:** MIT
-   **Version:** `1.3.0`
-   **Package Information:** https://www.npmjs.com/package/nostics
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/nostics
-   **Dependency Type:** Runtime dependency or transitive dependency

#### obug

-   **License:** MIT
-   **Version:** `2.2.1`
-   **Package Information:** https://www.npmjs.com/package/obug
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/obug
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### p-limit

-   **License:** MIT
-   **Version:** `2.3.0`
-   **Package Information:** https://www.npmjs.com/package/p-limit
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/p-limit
-   **Dependency Type:** Runtime dependency or transitive dependency

#### p-locate

-   **License:** MIT
-   **Version:** `4.1.0`
-   **Package Information:** https://www.npmjs.com/package/p-locate
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/p-locate
-   **Dependency Type:** Runtime dependency or transitive dependency

#### p-try

-   **License:** MIT
-   **Version:** `2.2.0`
-   **Package Information:** https://www.npmjs.com/package/p-try
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/p-try
-   **Dependency Type:** Runtime dependency or transitive dependency

#### parse5

-   **License:** MIT
-   **Version:** `8.0.1`
-   **Package Information:** https://www.npmjs.com/package/parse5
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/parse5
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### path-exists

-   **License:** MIT
-   **Version:** `4.0.0`
-   **Package Information:** https://www.npmjs.com/package/path-exists
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/path-exists
-   **Dependency Type:** Runtime dependency or transitive dependency

#### path-scurry

-   **License:** BlueOak-1.0.0
-   **Version:** `2.0.2`
-   **Package Information:** https://www.npmjs.com/package/path-scurry
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/path-scurry
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pathe

-   **License:** MIT
-   **Version:** `2.0.3`
-   **Package Information:** https://www.npmjs.com/package/pathe
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pathe
-   **Dependency Type:** Runtime dependency or transitive dependency

#### perfect-debounce

-   **License:** MIT
-   **Version:** `2.1.0`
-   **Package Information:**
    https://www.npmjs.com/package/perfect-debounce
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/perfect-debounce
-   **Dependency Type:** Runtime dependency or transitive dependency

#### picocolors

-   **License:** ISC
-   **Version:** `1.1.1`
-   **Package Information:** https://www.npmjs.com/package/picocolors
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/picocolors
-   **Dependency Type:** Runtime dependency or transitive dependency

#### picomatch

-   **License:** MIT
-   **Version:** `4.0.7`
-   **Package Information:** https://www.npmjs.com/package/picomatch
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/picomatch
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pinia

-   **License:** MIT
-   **Version:** `4.0.3`
-   **Package Information:** https://www.npmjs.com/package/pinia
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pinia
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pkg-types

-   **License:** MIT
-   **Version:** `1.3.1`
-   **Package Information:** https://www.npmjs.com/package/pkg-types
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pkg-types
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pkg-types

-   **License:** MIT
-   **Version:** `2.3.3`
-   **Package Information:** https://www.npmjs.com/package/pkg-types
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pkg-types
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pngjs

-   **License:** MIT
-   **Version:** `5.0.0`
-   **Package Information:** https://www.npmjs.com/package/pngjs
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pngjs
-   **Dependency Type:** Runtime dependency or transitive dependency

#### pofile

-   **License:** MIT
-   **Version:** `1.1.4`
-   **Package Information:** https://www.npmjs.com/package/pofile
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/pofile
-   **Dependency Type:** Runtime dependency or transitive dependency

#### postcss

-   **License:** MIT
-   **Version:** `8.5.29`
-   **Package Information:** https://www.npmjs.com/package/postcss
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/postcss
-   **Dependency Type:** Runtime dependency or transitive dependency

#### proto-list

-   **License:** ISC
-   **Version:** `1.2.4`
-   **Package Information:** https://www.npmjs.com/package/proto-list
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/proto-list
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### punycode

-   **License:** MIT
-   **Version:** `2.3.1`
-   **Package Information:** https://www.npmjs.com/package/punycode
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/punycode
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### qrcode

-   **License:** MIT
-   **Version:** `1.5.4`
-   **Package Information:** https://www.npmjs.com/package/qrcode
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/qrcode
-   **Dependency Type:** Runtime dependency or transitive dependency

#### quansync

-   **License:** MIT
-   **Version:** `0.2.11`
-   **Package Information:** https://www.npmjs.com/package/quansync
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/quansync
-   **Dependency Type:** Runtime dependency or transitive dependency

#### readdirp

-   **License:** MIT
-   **Version:** `5.1.1`
-   **Package Information:** https://www.npmjs.com/package/readdirp
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/readdirp
-   **Dependency Type:** Runtime dependency or transitive dependency

#### require-directory

-   **License:** MIT
-   **Version:** `2.1.1`
-   **Package Information:**
    https://www.npmjs.com/package/require-directory
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/require-directory
-   **Dependency Type:** Runtime dependency or transitive dependency

#### require-from-string

-   **License:** MIT
-   **Version:** `2.0.2`
-   **Package Information:**
    https://www.npmjs.com/package/require-from-string
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/require-from-string
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### require-main-filename

-   **License:** ISC
-   **Version:** `2.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/require-main-filename
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/require-main-filename
-   **Dependency Type:** Runtime dependency or transitive dependency

#### rolldown

-   **License:** MIT
-   **Version:** `1.2.13`
-   **Package Information:** https://www.npmjs.com/package/rolldown
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/rolldown
-   **Dependency Type:** Runtime dependency or transitive dependency

#### saxes

-   **License:** ISC
-   **Version:** `6.0.0`
-   **Package Information:** https://www.npmjs.com/package/saxes
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/saxes
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### scule

-   **License:** MIT
-   **Version:** `1.3.0`
-   **Package Information:** https://www.npmjs.com/package/scule
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/scule
-   **Dependency Type:** Runtime dependency or transitive dependency

#### semver

-   **License:** ISC
-   **Version:** `7.8.5`
-   **Package Information:** https://www.npmjs.com/package/semver
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/semver
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### set-blocking

-   **License:** ISC
-   **Version:** `2.0.0`
-   **Package Information:** https://www.npmjs.com/package/set-blocking
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/set-blocking
-   **Dependency Type:** Runtime dependency or transitive dependency

#### source-map-js

-   **License:** BSD-3-Clause
-   **Version:** `1.2.2`
-   **Package Information:** https://www.npmjs.com/package/source-map-js
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/source-map-js
-   **Dependency Type:** Runtime dependency or transitive dependency

#### std-env

-   **License:** MIT
-   **Version:** `4.3.0`
-   **Package Information:** https://www.npmjs.com/package/std-env
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/std-env
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### string-width

-   **License:** MIT
-   **Version:** `4.2.3`
-   **Package Information:** https://www.npmjs.com/package/string-width
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/string-width
-   **Dependency Type:** Runtime dependency or transitive dependency

#### strip-ansi

-   **License:** MIT
-   **Version:** `6.0.1`
-   **Package Information:** https://www.npmjs.com/package/strip-ansi
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/strip-ansi
-   **Dependency Type:** Runtime dependency or transitive dependency

#### symbol-tree

-   **License:** MIT
-   **Version:** `3.2.4`
-   **Package Information:** https://www.npmjs.com/package/symbol-tree
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/symbol-tree
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tinybench

-   **License:** MIT
-   **Version:** `6.2.1`
-   **Package Information:** https://www.npmjs.com/package/tinybench
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tinybench
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tinyexec

-   **License:** MIT
-   **Version:** `1.3.1`
-   **Package Information:** https://www.npmjs.com/package/tinyexec
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tinyexec
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tinyglobby

-   **License:** MIT
-   **Version:** `0.2.17`
-   **Package Information:** https://www.npmjs.com/package/tinyglobby
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tinyglobby
-   **Dependency Type:** Runtime dependency or transitive dependency

#### tldts

-   **License:** MIT
-   **Version:** `7.4.18`
-   **Package Information:** https://www.npmjs.com/package/tldts
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tldts
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tldts-core

-   **License:** MIT
-   **Version:** `7.4.18`
-   **Package Information:** https://www.npmjs.com/package/tldts-core
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tldts-core
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tough-cookie

-   **License:** BSD-3-Clause
-   **Version:** `6.0.2`
-   **Package Information:** https://www.npmjs.com/package/tough-cookie
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tough-cookie
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### tr46

-   **License:** MIT
-   **Version:** `6.0.0`
-   **Package Information:** https://www.npmjs.com/package/tr46
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/tr46
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### typical

-   **License:** MIT
-   **Version:** `7.3.0`
-   **Package Information:** https://www.npmjs.com/package/typical
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/typical
-   **Dependency Type:** Runtime dependency or transitive dependency

#### ufo

-   **License:** MIT
-   **Version:** `1.6.4`
-   **Package Information:** https://www.npmjs.com/package/ufo
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/ufo
-   **Dependency Type:** Runtime dependency or transitive dependency

#### undici

-   **License:** MIT
-   **Version:** `7.30.0`
-   **Package Information:** https://www.npmjs.com/package/undici
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/undici
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### unplugin

-   **License:** MIT
-   **Version:** `3.4.0`
-   **Package Information:** https://www.npmjs.com/package/unplugin
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/unplugin
-   **Dependency Type:** Runtime dependency or transitive dependency

#### unplugin-utils

-   **License:** MIT
-   **Version:** `0.3.2`
-   **Package Information:**
    https://www.npmjs.com/package/unplugin-utils
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/unplugin-utils
-   **Dependency Type:** Runtime dependency or transitive dependency

#### vite

-   **License:** MIT
-   **Version:** `8.3.4`
-   **Package Information:** https://www.npmjs.com/package/vite
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vite
-   **Dependency Type:** Runtime dependency or transitive dependency

#### vitest

-   **License:** MIT
-   **Version:** `5.0.3`
-   **Package Information:** https://www.npmjs.com/package/vitest
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vitest
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### vue

-   **License:** MIT
-   **Version:** `3.5.43`
-   **Package Information:** https://www.npmjs.com/package/vue
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vue
-   **Dependency Type:** Runtime dependency or transitive dependency

#### vue-component-type-helpers

-   **License:** MIT
-   **Version:** `3.3.12`
-   **Package Information:**
    https://www.npmjs.com/package/vue-component-type-helpers
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vue-component-type-helpers
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### vue-router

-   **License:** MIT
-   **Version:** `5.4.0`
-   **Package Information:** https://www.npmjs.com/package/vue-router
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vue-router
-   **Dependency Type:** Runtime dependency or transitive dependency

#### vue3-gettext

-   **License:** MIT
-   **Version:** `4.0.1`
-   **Package Information:** https://www.npmjs.com/package/vue3-gettext
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/vue3-gettext
-   **Dependency Type:** Runtime dependency or transitive dependency

#### w3c-xmlserializer

-   **License:** MIT
-   **Version:** `5.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/w3c-xmlserializer
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/w3c-xmlserializer
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### webidl-conversions

-   **License:** BSD-2-Clause
-   **Version:** `8.0.1`
-   **Package Information:**
    https://www.npmjs.com/package/webidl-conversions
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/webidl-conversions
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### webpack-virtual-modules

-   **License:** MIT
-   **Version:** `0.6.2`
-   **Package Information:**
    https://www.npmjs.com/package/webpack-virtual-modules
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/webpack-virtual-modules
-   **Dependency Type:** Runtime dependency or transitive dependency

#### whatwg-mimetype

-   **License:** MIT
-   **Version:** `5.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/whatwg-mimetype
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/whatwg-mimetype
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### whatwg-url

-   **License:** MIT
-   **Version:** `16.0.1`
-   **Package Information:** https://www.npmjs.com/package/whatwg-url
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/whatwg-url
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### which-module

-   **License:** ISC
-   **Version:** `2.0.1`
-   **Package Information:** https://www.npmjs.com/package/which-module
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/which-module
-   **Dependency Type:** Runtime dependency or transitive dependency

#### why-is-node-running

-   **License:** MIT
-   **Version:** `3.2.1`
-   **Package Information:**
    https://www.npmjs.com/package/why-is-node-running
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/why-is-node-running
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### wrap-ansi

-   **License:** MIT
-   **Version:** `6.2.0`
-   **Package Information:** https://www.npmjs.com/package/wrap-ansi
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/wrap-ansi
-   **Dependency Type:** Runtime dependency or transitive dependency

#### xml-name-validator

-   **License:** Apache-2.0
-   **Version:** `5.0.0`
-   **Package Information:**
    https://www.npmjs.com/package/xml-name-validator
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/xml-name-validator
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### xmlchars

-   **License:** MIT
-   **Version:** `2.2.0`
-   **Package Information:** https://www.npmjs.com/package/xmlchars
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/xmlchars
-   **Dependency Type:** Development dependency or development-only
    transitive dependency

#### y18n

-   **License:** ISC
-   **Version:** `4.0.3`
-   **Package Information:** https://www.npmjs.com/package/y18n
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/y18n
-   **Dependency Type:** Runtime dependency or transitive dependency

#### yargs

-   **License:** MIT
-   **Version:** `15.4.1`
-   **Package Information:** https://www.npmjs.com/package/yargs
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/yargs
-   **Dependency Type:** Runtime dependency or transitive dependency

#### yargs-parser

-   **License:** ISC
-   **Version:** `18.1.3`
-   **Package Information:** https://www.npmjs.com/package/yargs-parser
-   **License Text / Package License Metadata:**
    https://www.npmjs.com/package/yargs-parser
-   **Dependency Type:** Runtime dependency or transitive dependency

------------------------------------------------------------------------

## License Categories Summary

The npm section reflects license expressions as supplied by the
lockfile. Different license families can have different notice,
source-disclosure, attribution, and redistribution requirements. In
particular, do not treat this generated list as a definitive statement
that every dependency is compatible with AGPL-3.0-or-later.

## Obtaining Source Code

Source and package metadata for npm components are linked from each
package's npm page. Python source repositories and license texts are
linked in the corresponding backend entries. For compliance
distribution, retain the required copyright notices and license texts
for the exact versions shipped.

## License Compliance Statement

This file is an inventory aid, not legal advice or a completed
compliance audit. Before publishing, verify the actual project license,
the exact resolved Python dependency tree, the npm license texts, and
any separately distributed native/binary components.

------------------------------------------------------------------------

**Last Updated:** October 21, 2026

**Project License:** GNU Affero General Public License v3.0 or later
(AGPL-3.0-or-later) --- confirm this matches the project's actual
`LICENSE` file.
